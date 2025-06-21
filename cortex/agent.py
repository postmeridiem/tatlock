"""
cortex/agent.py

Core agent logic for Tatlock. Handles chat interaction, tool dispatch, and agentic loop.
"""

import ollama
import json
import re
from datetime import date, datetime
import uuid

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
    execute_search_conversations
)
from hippocampus.remember import save_interaction

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
}


def process_chat_interaction(user_message: str, history: list[dict], username: str = "admin", conversation_id: str | None = None) -> dict:
    """
    Handles the entire chat logic flow with an agentic loop for sequential tool calls.
    Args:
        user_message (str): The user's message.
        history (list[dict]): Previous conversation history.
        username (str): The username for user-specific database access. Defaults to "admin".
        conversation_id (str | None): Conversation ID for grouping messages. Defaults to None.
    Returns:
        dict: The agent's response, topic, and updated history.
    """

    base_instructions = get_base_instructions(username)

    messages_for_ollama = []
    messages_for_ollama.append({'role': 'system',
                                'content': f'The current date is {date.today().isoformat()}. The user is in Rotterdam.'})
    for instruction in base_instructions:
        messages_for_ollama.append({'role': 'system', 'content': instruction})

    messages_for_ollama.extend(history)
    messages_for_ollama.append({"role": "user", "content": user_message})

    max_interactions = 5
    for i in range(max_interactions):
        response = ollama.chat(model=OLLAMA_MODEL, messages=messages_for_ollama, tools=TOOLS)
        response_message = dict(response['message'])

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
            match = re.search(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", content, re.DOTALL)
            if match:
                try:
                    tool_json_str = match.group(1).replace('\\"', '"')
                    parsed_call = json.loads(tool_json_str)
                    if 'location' in parsed_call.get('parameters', {}):
                        parsed_call['parameters']['city'] = parsed_call['parameters'].pop('location')
                    response_message['tool_calls'] = [{"id": f"call_{uuid.uuid4().hex[:8]}",
                                                       "function": {"name": parsed_call.get("name"),
                                                                    "arguments": parsed_call.get("parameters", {})}}]
                    response_message['content'] = ""
                except (json.JSONDecodeError, AttributeError) as e:
                    print(f"Failed to parse tool call from content: {e}")

        messages_for_ollama.append(response_message)

        if not response_message.get('tool_calls'):
            break

        tool_outputs = []
        if response_message.get('tool_calls') and isinstance(response_message['tool_calls'], list):
            for tool_call in response_message['tool_calls']:
                function_name = tool_call.get('function', {}).get('name')
                function_args = tool_call.get('function', {}).get('arguments')
                tool_call_id = tool_call.get('id')
                if not function_name or not isinstance(function_args, dict): continue
                if function_name in AVAILABLE_TOOLS:
                    tool_function = AVAILABLE_TOOLS[function_name]
                    
                    # Add username to memory-related tools
                    if function_name in ['recall_memories', 'recall_memories_with_time', 'find_personal_variables', 'get_conversations_by_topic', 'get_topics_by_conversation', 'get_conversation_summary', 'get_topic_statistics', 'get_user_conversations', 'get_conversation_details', 'search_conversations']:
                        function_args['username'] = username
                    
                    output = tool_function(**function_args)
                    tool_outputs.append({"role": "tool", "tool_call_id": tool_call_id, "content": json.dumps(output)})
                else:
                    print(f"Warning: LLM tried to call an unknown tool: {function_name}")

        if tool_outputs:
            messages_for_ollama.extend(tool_outputs)
        else:
            if response_message.get('tool_calls'):
                messages_for_ollama.append({"role": "tool", "content": json.dumps(
                    {"status": "error",
                     "message": "Could not execute any of the requested tools or no valid tools were called."})})

    final_content = messages_for_ollama[-1]['content'] if messages_for_ollama and messages_for_ollama[-1][
        'role'] == 'assistant' else "I'm sorry, an error occurred or no assistant reply was generated."
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
                print(f"Could not generate topic: {e}")

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
        print(f"Error during saving interaction: {e}")

    return {
        "response": final_content,
        "topic": topic_str,
        "history": final_history,
        "conversation_id": conversation_id or datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    }