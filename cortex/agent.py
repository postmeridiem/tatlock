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

# Import from our new, organized modules
from config import OLLAMA_MODEL
from hippocampus.database import get_base_instructions
from stem.tools import (
    TOOLS,
    execute_find_personal_variables,
    execute_get_weather_forecast,
    execute_web_search,
    execute_recall_memories,
    execute_recall_memories_with_time,
    execute_get_conversations_by_topic,
    execute_get_topics_by_conversation,
    execute_get_conversation_summary,
    execute_get_topic_statistics,
    execute_get_user_conversations,
    execute_get_conversation_details,
    execute_search_conversations,
    execute_screenshot_from_url,
    execute_analyze_file
)
from hippocampus.remember import save_interaction

# Set up logging for this module
logger = logging.getLogger(__name__)

# --- Tool Dispatcher ---
AVAILABLE_TOOLS = {
    "web_search": execute_web_search,
    "find_personal_variables": execute_find_personal_variables,
    "get_weather_forecast": execute_get_weather_forecast,
    "recall_memories": execute_recall_memories,
    "recall_memories_with_time": execute_recall_memories_with_time,
    "get_conversations_by_topic": execute_get_conversations_by_topic,
    "get_topics_by_conversation": execute_get_topics_by_conversation,
    "get_conversation_summary": execute_get_conversation_summary,
    "get_topic_statistics": execute_get_topic_statistics,
    "get_user_conversations": execute_get_user_conversations,
    "get_conversation_details": execute_get_conversation_details,
    "search_conversations": execute_search_conversations,
    "screenshot_from_url": execute_screenshot_from_url,
    "analyze_file": execute_analyze_file
}

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

    base_instructions = get_base_instructions(username)

    messages_for_ollama = []
    messages_for_ollama.append({'role': 'system',
                                'content': f'The current date is {date.today().isoformat()}. The user is in Rotterdam.'})
    for instruction in base_instructions:
        messages_for_ollama.append({'role': 'system', 'content': instruction})

    messages_for_ollama.extend(history)
    messages_for_ollama.append({"role": "user", "content": user_message})

    max_interactions = 10
    tool_failures = []  # Track tool failures for analysis
    
    for i in range(max_interactions):
        logger.info(f"Tool Iteration {i+1}")
        
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
        
        response = ollama.chat(model=OLLAMA_MODEL, messages=messages_for_ollama, tools=TOOLS)
        response_message = dict(response['message'])
        
        # Add debugging for LLM response
        logger.info(f"Raw LLM response content: {response_message.get('content', 'None')}")
        logger.info(f"Raw LLM response tool_calls: {response_message.get('tool_calls', 'None')}")
        
        if response_message.get('tool_calls'):
            logger.info(f"LLM Response: {len(response_message['tool_calls'])} tool calls")
        else:
            logger.info(f"LLM Response: Final response (no tools)")

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
            logger.info(f"Found 'tool_calls' in content, attempting to parse...")
            
            # Try to parse tool calls from ```tool_calls``` code blocks
            match = re.search(r"```tool_calls\s*\n(.*?)\n```", content, re.DOTALL)
            if match:
                logger.info(f"Found ```tool_calls``` block, attempting to parse...")
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
                        logger.info(f"Successfully parsed {len(clean_tool_calls)} tool calls from content, cleared content")
                    else:
                        logger.info("No valid tool calls found in ```tool_calls``` block, keeping original content")
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.error(f"Failed to parse tool calls from ```tool_calls``` block: {e}")
                    logger.info("Keeping original content due to parsing error")
            
            # Fallback to the original <tool_call> parsing
            if not response_message.get('tool_calls'):
                match = re.search(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", content, re.DOTALL)
                if match:
                    logger.info(f"Found <tool_call> block, attempting to parse...")
                    try:
                        tool_json_str = match.group(1).replace('\\"', '"')
                        parsed_call = json.loads(tool_json_str)
                        if 'location' in parsed_call.get('parameters', {}):
                            parsed_call['parameters']['city'] = parsed_call['parameters'].pop('location')
                        response_message['tool_calls'] = [{"id": f"call_{uuid.uuid4().hex[:8]}",
                                                           "function": {"name": parsed_call.get("name"),
                                                                        "arguments": parsed_call.get("parameters", {})}}]
                        response_message['content'] = ""
                        logger.info(f"Successfully parsed tool call from <tool_call> block, cleared content")
                    except (json.JSONDecodeError, AttributeError) as e:
                        logger.error(f"Failed to parse tool call from content: {e}")
                        logger.info("Keeping original content due to parsing error")

        messages_for_ollama.append(response_message)

        # Add debugging after processing response message
        logger.info(f"After processing - content: {response_message.get('content', 'None')}")
        logger.info(f"After processing - tool_calls: {response_message.get('tool_calls', 'None')}")

        # If content is empty but no tool calls, try to get a proper response
        if not response_message.get('content') and not response_message.get('tool_calls'):
            logger.warning("Content is empty and no tool calls found, requesting new response from LLM")
            # Add a system message to request a proper response
            messages_for_ollama.append({'role': 'system', 'content': 'Please provide a helpful response to the user\'s message.'})
            response = ollama.chat(model=OLLAMA_MODEL, messages=messages_for_ollama, tools=TOOLS)
            response_message = dict(response['message'])
            messages_for_ollama[-1] = response_message  # Replace the system message with the new response
            logger.info(f"New response content: {response_message.get('content', 'None')}")

        if not response_message.get('tool_calls'):
            logger.info("No tool calls found, breaking out of loop")
            break

        tool_outputs = []
        failed_tools = []  # Track failures in this iteration
        
        if response_message.get('tool_calls') and isinstance(response_message['tool_calls'], list):
            for tool_call in response_message['tool_calls']:
                function_name = tool_call.get('function', {}).get('name')
                function_args = tool_call.get('function', {}).get('arguments')
                tool_call_id = tool_call.get('id')
                
                # Print single line tool call information
                logger.info(f"TOOL: {function_name} | Args: {json.dumps(function_args)}")
                
                if not function_name or not isinstance(function_args, dict): 
                    failed_tools.append(f"Invalid tool call format for {function_name}")
                    continue
                    
                if function_name in AVAILABLE_TOOLS:
                    tool_function = AVAILABLE_TOOLS[function_name]
                    
                    # Add username to memory-related tools
                    if function_name in ['recall_memories', 'recall_memories_with_time', 'find_personal_variables', 'get_conversations_by_topic', 'get_topics_by_conversation', 'get_conversation_summary', 'get_topic_statistics', 'get_user_conversations', 'get_conversation_details', 'search_conversations']:
                        function_args['username'] = username
                    
                    try:
                        # Check if the tool function is async
                        if inspect.iscoroutinefunction(tool_function):
                            output = run_async(tool_function(**function_args))
                        else:
                            output = tool_function(**function_args)
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

    final_content = messages_for_ollama[-1]['content'] if messages_for_ollama and messages_for_ollama[-1][
        'role'] == 'assistant' else "I'm sorry, an error occurred or no assistant reply was generated."
    
    # Add debugging for empty response issue
    logger.info(f"Final content length: {len(final_content) if final_content else 0}")
    logger.info(f"Final content preview: {final_content[:100] if final_content else 'None'}...")
    logger.info(f"Last message role: {messages_for_ollama[-1]['role'] if messages_for_ollama else 'None'}")
    
    final_history = [msg for msg in messages_for_ollama if msg['role'] != 'system']

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