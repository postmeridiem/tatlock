#!/usr/bin/env python3
"""
Test script to verify the weather query works with the new parser.
"""

import requests
import json

def test_weather_query():
    """Test weather query to Rotterdam."""
    url = "http://localhost:8000/cortex"

    payload = {
        "message": "what is the weather in rotterdam tomorrow?",
        "history": [],
        "conversation_id": "test_session"
    }

    headers = {
        "Content-Type": "application/json"
    }

    print("Testing weather query...")
    print(f"Request: {payload['message']}")
    print("-" * 50)

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response received:")
            print(f"Response: {result.get('response', 'No response')}")
            print(f"Processing time: {result.get('processing_time', 'Unknown')}s")
            print(f"Topic: {result.get('topic', 'Unknown')}")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error making request: {e}")

if __name__ == "__main__":
    test_weather_query()