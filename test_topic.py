# File: test_topic.py

import ollama
from config import OLLAMA_MODEL # This will load your custom model name

# --- The "Perfect" Input ---
# This is a clean, simple, hard-coded conversation history.
# There are no tool calls or complex data, just plain text.
messages_for_summary = [
    {
        'role': 'system',
        'content': 'Provide a single, one-word topic for the following conversation. Examples: weather, personal_info, planning, general_knowledge, humor.'
    },
    {
        'role': 'user',
        'content': 'What is the weather like in Amsterdam?'
    },
    {
        'role': 'assistant',
        'content': 'The weather in Amsterdam is currently 15°C with scattered clouds.'
    }
]

# --- Test 1: Your Custom Model ---
# We will use the OLLAMA_MODEL you defined in your .env file
# (e.g., 'gemma3-cortex:latest')
print(f"--- 1. Testing with your custom model: {OLLAMA_MODEL} ---")
try:
    response_custom = ollama.chat(
        model=OLLAMA_MODEL,
        messages=messages_for_summary
    )
    print("RAW RESPONSE FROM YOUR MODEL:")
    print(response_custom)
    print("\nCONTENT FROM YOUR MODEL:")
    print(f"'{response_custom['message']['content']}'")
except Exception as e:
    print(f"An error occurred: {e}")


# --- Test 2: A Standard Model ---
# Now we run the EXACT same input with a standard model known for text generation
standard_model = "gemma2"
print(f"\n\n--- 2. Testing with a standard model: {standard_model} ---")
try:
    response_standard = ollama.chat(
        model=standard_model,
        messages=messages_for_summary
    )
    print("RAW RESPONSE FROM STANDARD MODEL:")
    print(response_standard)
    print("\nCONTENT FROM STANDARD MODEL:")
    print(f"'{response_standard['message']['content']}'")
except Exception as e:
    print(f"An error occurred: {e}")