"""
cortex/agent.py

Core agent logic for Tatlock. Handles chat interaction, tool dispatch, and agentic loop.
"""

import ollama
import json
import re
import logging
import time
from datetime import date, datetime
import uuid
import asyncio
import inspect
from typing import List, Literal
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field

# Import from our new, organized modules
from config import OLLAMA_MODEL
from hippocampus.database import get_base_instructions
from hippocampus.reference_frame import get_tool_catalog_for_selection, get_selected_tools
from stem.tools import TOOLS, AVAILABLE_TOOLS, execute_tool
from hippocampus.remember import save_interaction
from cortex.response_parser import response_parser, response_formatter
from stem.debug_logger import get_debug_logger, reset_debug_logger

# Set up logging for this module
logger = logging.getLogger(__name__)

# --- Tool Dispatcher ---
# AVAILABLE_TOOLS now provided by dynamic tool system in stem/tools.py

# Pydantic model for structured capability assessment
class CapabilityAssessment(BaseModel):
    assessment: Literal["DIRECT", "TOOLS_NEEDED"] = Field(
        description="Whether the question can be answered directly or needs tools"
    )
    tools: List[str] = Field(
        default=[],
        description="List of specific tool keys needed, empty if none required"
    )
    response: str = Field(
        description="Direct answer if DIRECT, or 'PROCESSING WITH TOOLS' if tools needed"
    )

# Initialize instructor client for structured output
instructor_client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required but unused for local Ollama
    ),
    mode=instructor.Mode.JSON,
)

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            raise RuntimeError("nest_asyncio is required to run async tools in a running event loop. Please install it with 'pip install nest_asyncio'.")
        return loop.run_until_complete(coro)
    else:
        return asyncio.run(coro)

def process_chat_interaction(user_message: str, history: list[dict], username: str = "admin", conversation_id: str | None = None) -> dict:
    """
    Handles the entire chat logic flow with an agentic loop for sequential tool calls.
    Args:
        user_message (str): The user's message.
        history (list[dict]): Previous conversation history.
        username (str): The username for user-specific database access. Defaults to "admin".
        conversation_id (str | None): Conversation ID for grouping messages. Defaults to None.
    Returns:
        dict: The agent's response, topic, updated history, and processing time.
    """
    start_time = time.time()
    logger.info(f"[BENCHMARK] Starting process_chat_interaction for: '{user_message[:50]}...'")

    base_instructions = get_base_instructions(username)
    setup_time = time.time()
    logger.info(f"[BENCHMARK] Setup/instructions: {setup_time - start_time:.3f}s")

    # Get user location from personal variables
    location = "unknown location"
    try:
        location_result = execute_tool("find_personal_variables", searchkey="location", username=username)
        if location_result.get("status") == "success" and location_result.get("data"):
            # Use the first value found
            location = location_result["data"][0]["value"]
    except Exception as e:
        logger.warning(f"Could not retrieve user location: {e}")

    messages_for_ollama = []
    messages_for_ollama.append({'role': 'system',
                                'content': f'The current date is {date.today().isoformat()}. The user is in {location}.'})
    for instruction in base_instructions:
        messages_for_ollama.append({'role': 'system', 'content': instruction})

    messages_for_ollama.extend(history)
    messages_for_ollama.append({"role": "user", "content": user_message})

    max_interactions = 10
    tool_failures = []  # Track tool failures for analysis
    
    for i in range(max_interactions):
        logger.debug(f"Tool Iteration {i+1}")
        
        # Check if this is the last iteration and we've had tool failures
        if i == max_interactions - 1 and tool_failures:
            # Add system prompt for tool failure analysis
            failure_analysis_prompt = f"""
IMPORTANT: You have reached the maximum number of tool call attempts ({max_interactions}). 
The following tools failed to execute properly:
{chr(10).join([f"- {failure}" for failure in tool_failures])}

Please provide a comprehensive response that:
1. Acknowledges the tool failures
2. Analyzes what went wrong (API issues, invalid parameters, network problems, etc.)
3. Provides the best possible answer with the information available
4. Suggests alternative approaches or what information would be needed
5. Maintains your helpful and professional tone

Do not attempt to call any more tools - provide a final response analyzing the situation.
"""
            messages_for_ollama.append({'role': 'system', 'content': failure_analysis_prompt})
        
        logger.info(f"LLM_TOOL_CALL | Tool: chat_completion | CallID: chat_{uuid.uuid4().hex[:8]} | Args: {{'model': '{OLLAMA_MODEL}', 'messages_count': {len(messages_for_ollama)}, 'tools_count': {len(TOOLS)}}}")
        llm_start = time.time()
        logger.info(f"[BENCHMARK] Starting LLM call #{i+1}")
        response = ollama.chat(model=OLLAMA_MODEL, messages=messages_for_ollama, tools=TOOLS)
        llm_end = time.time()
        logger.info(f"[BENCHMARK] LLM call #{i+1} completed: {llm_end - llm_start:.3f}s")
        response_message = dict(response['message'])
        
        # Add debugging for LLM response (only in debug mode)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Raw LLM response content: {response_message.get('content', 'None')}")
            logger.debug(f"Raw LLM response tool_calls: {response_message.get('tool_calls', 'None')}")
        
        if response_message.get('tool_calls'):
            logger.debug(f"LLM Response: {len(response_message['tool_calls'])} tool calls")
        else:
            logger.debug(f"LLM Response: Final response (no tools)")

        if response_message.get('tool_calls'):
            clean_tool_calls = []
            for tool_call_obj in response_message['tool_calls']:
                function_obj = tool_call_obj.get('function', {})
                function_dict = {
                    'name': getattr(function_obj, 'name', None),
                    'arguments': getattr(function_obj, 'arguments', {})
                }
                clean_tool_calls.append({
                    'id': tool_call_obj.get('id'),
                    'type': 'function',
                    'function': function_dict
                })
            response_message['tool_calls'] = clean_tool_calls
        elif response_message.get('tool_calls') == '':
            response_message['tool_calls'] = None

        if not response_message.get('tool_calls') and "tool_calls" in response_message.get('content', ''):
            content = response_message['content']
            logger.debug(f"Found 'tool_calls' in content, attempting to parse...")
            
            # Try to parse tool calls from ```tool_calls``` code blocks
            match = re.search(r"```tool_calls\s*\n(.*?)\n```", content, re.DOTALL)
            if match:
                logger.debug(f"Found ```tool_calls``` block, attempting to parse...")
                try:
                    tool_json_str = match.group(1).strip()
                    parsed_calls = json.loads(tool_json_str)
                    
                    # Convert the parsed calls to the proper format
                    clean_tool_calls = []
                    for parsed_call in parsed_calls:
                        if isinstance(parsed_call, dict) and 'name' in parsed_call and 'parameters' in parsed_call:
                            clean_tool_calls.append({
                                "id": f"call_{uuid.uuid4().hex[:8]}",
                                "type": "function",
                                "function": {
                                    "name": parsed_call.get("name"),
                                    "arguments": parsed_call.get("parameters", {})
                                }
                            })
                    
                    if clean_tool_calls:
                        response_message['tool_calls'] = clean_tool_calls
                        response_message['content'] = ""
                        logger.debug(f"Successfully parsed {len(clean_tool_calls)} tool calls from content, cleared content")
                    else:
                        logger.debug("No valid tool calls found in ```tool_calls``` block, keeping original content")
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.error(f"Failed to parse tool calls from ```tool_calls``` block: {e}")
                    logger.debug("Keeping original content due to parsing error")
            
            # Fallback to the original <tool_call> parsing
            if not response_message.get('tool_calls'):
                match = re.search(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", content, re.DOTALL)
                if match:
                    logger.debug(f"Found <tool_call> block, attempting to parse...")
                    try:
                        tool_json_str = match.group(1).replace('\\"', '"')
                        parsed_call = json.loads(tool_json_str)
                        if 'location' in parsed_call.get('parameters', {}):
                            parsed_call['parameters']['city'] = parsed_call['parameters'].pop('location')
                        response_message['tool_calls'] = [{"id": f"call_{uuid.uuid4().hex[:8]}",
                                                           "function": {"name": parsed_call.get("name"),
                                                                        "arguments": parsed_call.get("parameters", {})}}]
                        response_message['content'] = ""
                        logger.debug(f"Successfully parsed tool call from <tool_call> block, cleared content")
                    except (json.JSONDecodeError, AttributeError) as e:
                        logger.error(f"Failed to parse tool call from content: {e}")
                        logger.debug("Keeping original content due to parsing error")

        messages_for_ollama.append(response_message)

        # Add debugging after processing response message (only in debug mode)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"After processing - content: {response_message.get('content', 'None')}")
            logger.debug(f"After processing - tool_calls: {response_message.get('tool_calls', 'None')}")

        # If content is empty but no tool calls, try to get a proper response
        if not response_message.get('content') and not response_message.get('tool_calls'):
            logger.warning("Content is empty and no tool calls found, requesting new response from LLM")
            # Add a system message to request a proper response
            messages_for_ollama.append({'role': 'system', 'content': 'Please provide a helpful response to the user\'s message.'})
            logger.info(f"LLM_TOOL_CALL | Tool: chat_completion_retry | CallID: chat_retry_{uuid.uuid4().hex[:8]} | Args: {{'model': '{OLLAMA_MODEL}', 'messages_count': {len(messages_for_ollama)}, 'tools_count': {len(TOOLS)}}}")
            response = ollama.chat(model=OLLAMA_MODEL, messages=messages_for_ollama, tools=TOOLS)
            response_message = dict(response['message'])
            messages_for_ollama[-1] = response_message  # Replace the system message with the new response
            logger.debug(f"New response content: {response_message.get('content', 'None')}")

        if not response_message.get('tool_calls'):
            logger.debug("No tool calls found, breaking out of loop")
            break

        tool_outputs = []
        failed_tools = []  # Track failures in this iteration
        
        if response_message.get('tool_calls') and isinstance(response_message['tool_calls'], list):
            for tool_call in response_message['tool_calls']:
                function_name = tool_call.get('function', {}).get('name')
                function_args = tool_call.get('function', {}).get('arguments')
                tool_call_id = tool_call.get('id')
                
                # Single comprehensive log entry for each tool call
                logger.info(f"LLM_TOOL_CALL | Tool: {function_name} | CallID: {tool_call_id} | Args: {json.dumps(function_args, default=str)}")
                
                if not function_name or not isinstance(function_args, dict): 
                    failed_tools.append(f"Invalid tool call format for {function_name}")
                    continue
                    
                if function_name in AVAILABLE_TOOLS:
                    # Add username to memory-related tools
                    if function_name in ['recall_memories', 'recall_memories_with_time', 'find_personal_variables', 'get_conversations_by_topic', 'get_topics_by_conversation', 'get_conversation_summary', 'get_topic_statistics', 'get_user_conversations', 'get_conversation_details', 'search_conversations']:
                        function_args['username'] = username

                    try:
                        # Use the new dynamic tool execution
                        output = execute_tool(function_name, **function_args)
                        tool_outputs.append({"role": "tool", "tool_call_id": tool_call_id, "content": json.dumps(output)})
                    except Exception as e:
                        failed_tools.append(f"{function_name}: {str(e)}")
                        tool_outputs.append({"role": "tool", "tool_call_id": tool_call_id, "content": json.dumps({
                            "status": "error",
                            "message": f"Tool {function_name} failed: {str(e)}"
                        })})
                else:
                    failed_tools.append(f"Unknown tool: {function_name}")
                    logger.warning(f"Warning: LLM tried to call an unknown tool: {function_name}")

        # Track failures for analysis
        if failed_tools:
            tool_failures.extend(failed_tools)

        if tool_outputs:
            messages_for_ollama.extend(tool_outputs)
        else:
            if response_message.get('tool_calls'):
                error_msg = "Could not execute any of the requested tools or no valid tools were called."
                tool_failures.append(error_msg)
                messages_for_ollama.append({"role": "tool", "content": json.dumps({
                    "status": "error",
                    "message": error_msg
                })})

    final_content = "I'm sorry, an error occurred or no assistant reply was generated."
    if messages_for_ollama:
        last_message = messages_for_ollama[-1]
        if isinstance(last_message, dict) and last_message.get('role') == 'assistant' and 'content' in last_message:
            final_content = last_message['content']
    
    # Add debugging for empty response issue (only in debug mode)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Final content length: {len(final_content) if final_content else 0}")
        logger.debug(f"Final content preview: {final_content[:100] if final_content else 'None'}...")
        logger.debug(f"Last message role: {messages_for_ollama[-1].get('role', 'None') if messages_for_ollama else 'None'}")
    
    final_history = [msg for msg in messages_for_ollama if msg.get('role') != 'system']

    topic_str = "general"
    if final_history:
        history_for_summary = ""
        for msg in final_history:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            if content and isinstance(content, str):
                history_for_summary += f"{role}: {content}\n"

        if history_for_summary:
            messages_for_summary = [
                {'role': 'system',
                 'content': 'You are a text summarizer. Analyze the following conversation script and respond with a single, one-word topic that best describes it. Examples: weather, personal_info, planning, general_knowledge.'},
                {'role': 'user', 'content': history_for_summary}
            ]
            try:
                logger.info(f"LLM_TOOL_CALL | Tool: topic_generation | CallID: topic_{uuid.uuid4().hex[:8]} | Args: {{'model': '{OLLAMA_MODEL}', 'messages_count': {len(messages_for_summary)}}}")
                topic_response = ollama.chat(model=OLLAMA_MODEL, messages=messages_for_summary)
                topic_str = topic_response['message']['content'].strip().lower().replace(" ", "_")

                if not topic_str:
                    topic_str = "general"
            except Exception as e:
                logger.error(f"Could not generate topic: {e}")

    try:
        save_interaction(
            user_prompt=user_message,
            llm_reply=final_content,
            full_llm_history=messages_for_ollama,
            topic=topic_str,
            username=username,
            conversation_id=conversation_id
        )
    except Exception as e:
        logger.error(f"Error during saving interaction: {e}")

    processing_time = time.time() - start_time
    processing_time = round(processing_time, 1)
    return {
        "response": final_content,
        "topic": topic_str,
        "history": final_history,
        "conversation_id": conversation_id or datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
        "processing_time": processing_time
    }

def process_chat_interaction_lean(user_message: str, history: list[dict], username: str = "admin", conversation_id: str | None = None) -> dict:
    """
    NEW LEAN TOOL SELECTION: Two-phase approach for faster LLM responses.
    Phase 1: Ask LLM if it needs tools and which ones
    Phase 2: If tools needed, call LLM again with only selected tools
    This dramatically reduces the tool schema overhead from 17 tools to 0-5 tools.
    """
    start_time = time.time()
    logger.info(f"[BENCHMARK] Starting LEAN process_chat_interaction for: '{user_message[:50]}...'")

    # Initialize debug logger for this session
    debug_logger = get_debug_logger(conversation_id)
    debug_logger.log_phase_start("Session Initialization", f"User: {username}, Message: {user_message[:100]}")

    base_instructions = get_base_instructions(username)
    setup_time = time.time()
    logger.info(f"[BENCHMARK] Setup/instructions: {setup_time - start_time:.3f}s")

    # Get user location from personal variables
    location = "unknown location"
    try:
        location_result = execute_tool("find_personal_variables", searchkey="location", username=username)
        if location_result.get("status") == "success" and location_result.get("data"):
            location = location_result["data"][0]["value"]
    except Exception as e:
        logger.warning(f"Could not retrieve user location: {e}")

    # Build base messages for main processing
    messages_for_ollama = []
    messages_for_ollama.append({'role': 'system',
                                'content': f'The current date is {date.today().isoformat()}. The user is in {location}.'})
    for instruction in base_instructions:
        messages_for_ollama.append({'role': 'system', 'content': instruction})

    messages_for_ollama.extend(history)
    messages_for_ollama.append({"role": "user", "content": user_message})

    # PHASE 1: Capability Assessment - Ask LLM if it needs tools
    phase1_start = time.time()

    tool_catalog = get_tool_catalog_for_selection()

    capability_prompt = f"""
CAPABILITY ASSESSMENT: Before providing your response, determine if you can answer the user's question with your existing knowledge, or if you need additional capabilities through tools.

Available tool categories:
• PERSONAL DATA: {[tool['key'] for tool in tool_catalog.get('personal_data', [])]}
• MEMORY/RECALL: {[tool['key'] for tool in tool_catalog.get('memory_recall', [])]}
• EXTERNAL DATA: {[tool['key'] for tool in tool_catalog.get('external_data', [])]}
• VISUAL ANALYSIS: {[tool['key'] for tool in tool_catalog.get('visual_analysis', [])]}
• CONVERSATION ANALYSIS: {[tool['key'] for tool in tool_catalog.get('conversation_analysis', [])]}

Respond with EXACTLY this format:
ASSESSMENT: [DIRECT or TOOLS_NEEDED]
TOOLS: [comma-separated list of specific tool keys needed, or NONE]
RESPONSE: [if DIRECT, provide your complete answer here; if TOOLS_NEEDED, write "PROCESSING WITH TOOLS"]

Examples:
- For "What is the capital of France?" → ASSESSMENT: DIRECT, TOOLS: NONE, RESPONSE: The capital of France is Paris.
- For "What's the weather like?" → ASSESSMENT: TOOLS_NEEDED, TOOLS: get_weather_forecast, RESPONSE: PROCESSING WITH TOOLS
- For "What did we discuss yesterday?" → ASSESSMENT: TOOLS_NEEDED, TOOLS: recall_memories, RESPONSE: PROCESSING WITH TOOLS

You can always ask to see the tool catalog again by saying "show tools" if you need to reconsider your capabilities.
"""

    # Create minimal capability assessment messages (NO heavy system instructions)
    capability_messages = [
        {'role': 'system', 'content': f'The current date is {date.today().isoformat()}. The user is in {location}.'},
        {'role': 'system', 'content': capability_prompt}
    ]

    # Add only the user message and recent history (not all system instructions)
    if history:
        capability_messages.extend(history[-3:])  # Only last 3 messages for context
    capability_messages.append({"role": "user", "content": user_message})

    logger.info(f"[BENCHMARK] Starting Phase 1 (capability assessment with structured parsing)")

    # Debug log Phase 1 start
    phase1_start = time.time()
    debug_logger.log_phase_start("Phase 1: Capability Assessment", "Determine if tools are needed and which ones")

    try:
        # Use instructor for structured output parsing
        # Convert messages for instructor (it expects OpenAI format)
        instructor_messages = []
        for msg in capability_messages:
            instructor_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Debug log the LLM request
        debug_logger.log_llm_request(OLLAMA_MODEL, instructor_messages, tools=None, iteration_type="capability_assessment")

        assessment: CapabilityAssessment = instructor_client.chat.completions.create(
            model=OLLAMA_MODEL,
            response_model=CapabilityAssessment,
            messages=instructor_messages,
            max_retries=2,
            timeout=30
        )
        phase1_end = time.time()
        logger.info(f"[BENCHMARK] Phase 1 completed: {phase1_end - phase1_start:.3f}s")
        logger.debug(f"Structured assessment: {assessment.model_dump()}")

        # Debug log the LLM response
        debug_logger.log_llm_response(
            {"assessment": assessment.assessment, "tools": assessment.tools, "response": assessment.response},
            phase1_end - phase1_start
        )

    except Exception as e:
        logger.error(f"Instructor structured parsing failed: {e}")
        # Fallback to basic ollama call
        capability_response = ollama.chat(model=OLLAMA_MODEL, messages=capability_messages, tools=[])
        phase1_end = time.time()
        logger.info(f"[BENCHMARK] Phase 1 fallback completed: {phase1_end - phase1_start:.3f}s")

        # Create assessment from fallback response
        capability_content = capability_response['message']['content']
        logger.debug(f"Fallback capability assessment response: {capability_content[:200]}...")

        # Simple parsing as fallback
        if "direct" in capability_content.lower() or "no tools" in capability_content.lower():
            assessment = CapabilityAssessment(
                assessment="DIRECT",
                tools=[],
                response=capability_content
            )
        else:
            assessment = CapabilityAssessment(
                assessment="TOOLS_NEEDED",
                tools=["recall_memories"],  # Default fallback tool
                response="PROCESSING WITH TOOLS"
            )

    # Use structured assessment result instead of regex parsing
    if assessment.assessment == "DIRECT" and len(assessment.tools) == 0:
        # Format the direct response using our response formatter
        final_response = response_formatter.format_response(assessment.response)
        logger.info(f"[BENCHMARK] Direct response path - no tools needed")

        # Save interaction and generate topic
        topic_str = "general_conversation"
        final_history = messages_for_ollama[2:] + [{"role": "assistant", "content": final_response}]

        try:
            save_interaction(username, user_message, final_response, topic_str, conversation_id)
        except Exception as e:
            logger.error(f"Error saving interaction: {e}")

        processing_time = round(time.time() - start_time, 1)
        return {
            "response": final_response,
            "topic": topic_str,
            "history": final_history,
            "conversation_id": conversation_id or datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
            "processing_time": processing_time
        }

    # PHASE 2: Tool-enabled processing
    elif assessment.assessment == "TOOLS_NEEDED" and len(assessment.tools) > 0:
        requested_tools = assessment.tools

        # Get only the selected tools from database
        selected_tools = get_selected_tools(requested_tools)

        phase2_start = time.time()
        logger.info(f"[BENCHMARK] Starting Phase 2 (tool-enabled processing)")

        # Debug log Phase 2 start
        debug_logger.log_phase_start("Phase 2: Tool-Enabled Processing", f"Selected tools: {requested_tools}")

        # Add tool usage instructions
        tool_instructions = "Use the provided tools as needed to answer the user's question. Call tools directly without asking permission."
        tool_messages = messages_for_ollama + [{'role': 'system', 'content': tool_instructions}]

        # Debug log the LLM request with tools
        debug_logger.log_llm_request(OLLAMA_MODEL, tool_messages, tools=selected_tools, iteration_type="tool_enabled")

        response = ollama.chat(model=OLLAMA_MODEL, messages=tool_messages, tools=selected_tools)
        phase2_end = time.time()
        logger.info(f"[BENCHMARK] Phase 2 completed: {phase2_end - phase2_start:.3f}s")

        # Debug log the LLM response
        debug_logger.log_llm_response(response, phase2_end - phase2_start)

        # Use the new model-agnostic parser
        parsed_response = response_parser.parse_response(response)
        logger.debug(f"Parsed response: tool_calls={len(parsed_response.tool_calls)}, needs_execution={parsed_response.needs_tool_execution}")

        # Process tool calls with full agentic loop
        if parsed_response.needs_tool_execution and parsed_response.tool_calls:
            # Add the assistant's message with parsed tool calls to conversation
            tool_calls_for_history = []
            for tc in parsed_response.tool_calls:
                tool_calls_for_history.append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": tc.arguments
                    }
                })

            messages_for_ollama.append({
                "role": "assistant",
                "content": parsed_response.content,
                "tool_calls": tool_calls_for_history
            })

            # Execute tool calls
            tool_outputs = []
            failed_tools = []

            for tool_call in parsed_response.tool_calls:
                tool_call_id = tool_call.id
                function_name = tool_call.name
                function_args = tool_call.arguments

                # Ensure arguments is a dict
                if isinstance(function_args, str):
                    try:
                        function_args = json.loads(function_args)
                    except json.JSONDecodeError:
                        function_args = {}

                logger.info(f"LLM_TOOL_CALL | Tool: {function_name} | CallID: {tool_call_id} | Args: {json.dumps(function_args, default=str)}")

                if not function_name or not isinstance(function_args, dict):
                    failed_tools.append(f"Invalid tool call format for {function_name}")
                    continue

                if function_name in AVAILABLE_TOOLS:
                    tool_function = AVAILABLE_TOOLS[function_name]

                    # Add username to memory-related tools
                    if function_name in ['recall_memories', 'recall_memories_with_time', 'find_personal_variables', 'get_conversations_by_topic', 'get_topics_by_conversation', 'get_conversation_summary', 'get_topic_statistics', 'get_user_conversations', 'get_conversation_details', 'search_conversations']:
                        function_args['username'] = username

                    try:
                        # Debug log tool execution start
                        tool_start = time.time()

                        # Use the new dynamic tool execution
                        output = execute_tool(function_name, **function_args)

                        # Debug log tool execution completion
                        tool_end = time.time()
                        debug_logger.log_tool_execution(function_name, function_args, output, tool_end - tool_start)

                        tool_outputs.append({"role": "tool", "tool_call_id": tool_call_id, "content": json.dumps(output)})
                    except Exception as e:
                        failed_tools.append(f"{function_name}: {str(e)}")
                        tool_outputs.append({"role": "tool", "tool_call_id": tool_call_id, "content": json.dumps({
                            "status": "error",
                            "message": f"Tool {function_name} failed: {str(e)}"
                        })})
                else:
                    failed_tools.append(f"Unknown tool: {function_name}")
                    logger.warning(f"Warning: LLM tried to call an unknown tool: {function_name}")

            # Add tool outputs to conversation
            if tool_outputs:
                messages_for_ollama.extend(tool_outputs)

                # Get final response from LLM after tool execution
                final_llm_response = ollama.chat(model=OLLAMA_MODEL, messages=messages_for_ollama, tools=selected_tools)
                raw_final_response = final_llm_response['message'].get('content', 'Processing completed.')

                # Format the response using our response formatter
                final_response = response_formatter.format_response(raw_final_response, tool_outputs)
            else:
                if parsed_response.tool_calls:
                    final_response = response_formatter.format_response("Could not execute any of the requested tools or no valid tools were called.")
                else:
                    final_response = response_formatter.format_response("Processing completed.")
        else:
            # No tools needed - format the direct response
            final_response = response_formatter.format_response(parsed_response.content)

        # Save interaction and generate topic
        topic_str = "tool_assisted_conversation"
        final_history = messages_for_ollama[2:] + [{"role": "assistant", "content": final_response}]

        try:
            save_interaction(username, user_message, final_response, topic_str, conversation_id)
        except Exception as e:
            logger.error(f"Error saving interaction: {e}")

        processing_time = round(time.time() - start_time, 1)
        return {
            "response": final_response,
            "topic": topic_str,
            "history": final_history,
            "conversation_id": conversation_id or datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
            "processing_time": processing_time
        }

    # Fallback: if parsing fails, use direct response
    logger.warning("Failed to parse capability assessment, using direct response")
    fallback_response = response_formatter.format_response("I apologize, but I encountered an issue processing your request. Please try again.")

    processing_time = round(time.time() - start_time, 1)
    return {
        "response": fallback_response,
        "topic": "error_fallback",
        "history": messages_for_ollama[2:] + [{"role": "assistant", "content": fallback_response}],
        "conversation_id": conversation_id or datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
        "processing_time": processing_time
    }