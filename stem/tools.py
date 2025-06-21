"""
stem/tools.py

Defines callable tools for the Tatlock agent, including weather, web search, recall, and personal variable lookup.
"""

import requests
import json
from datetime import date, datetime

# --- [ADDED] Import the new config variables ---
from config import OPENWEATHER_API_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID
from hippocampus.database import query_personal_variables
from hippocampus.recall import (
    recall_memories, 
    recall_memories_with_time,
    get_conversations_by_topic,
    get_topics_by_conversation,
    get_conversation_summary,
    get_topic_statistics
)

# ... (The TOOLS list and other execute functions remain the same) ...
# You can copy just the function below and replace the old one.

TOOLS = [
    # ... your existing tools ...
    {
        "type": "function",
        "function": {
            "name": "recall_memories",
            "description": "Recall past conversations by searching for a keyword in the user's prompt, the AI's reply, or the topic name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "The keyword to search for in memory (user prompt, reply, or topic)."
                    }
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall_memories_with_time",
            "description": "Recall past conversations by searching for a keyword and limiting to a date or date range (YYYY-MM-DD).",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "The keyword to search for in memory (user prompt, reply, or topic)."
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD) to limit the search. Optional."
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD) to limit the search. Optional."
                    }
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_conversations_by_topic",
            "description": "Find all conversations that contain a specific topic, with metadata about when the topic appeared.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic_name": {
                        "type": "string",
                        "description": "The topic name to search for conversations."
                    }
                },
                "required": ["topic_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_topics_by_conversation",
            "description": "Get all topics that appear in a specific conversation, with metadata about topic frequency.",
            "parameters": {
                "type": "object",
                "properties": {
                    "conversation_id": {
                        "type": "string",
                        "description": "The conversation ID to analyze for topics."
                    }
                },
                "required": ["conversation_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_conversation_summary",
            "description": "Get a comprehensive summary of a conversation including its topics, duration, and key interactions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "conversation_id": {
                        "type": "string",
                        "description": "The conversation ID to summarize."
                    }
                },
                "required": ["conversation_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_topic_statistics",
            "description": "Get statistics about all topics across conversations, including frequency and conversation count.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_personal_variables",
            "description": "Finds and retrieves personal properties of the current user (e.g., name, first name, last name, age, domicile, city, country) by searching a local database. Provide the key to search for.",
            "parameters": {
                "type": "object",
                "properties": {
                    "searchkey": {
                        "type": "string",
                        "description": "The key for the personal variable to find. For example: 'name', 'hometown', 'age'."
                    }
                },
                "required": ["searchkey"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "Get the weather forecast for a specific city on a given date or range of dates. Defaults to today's weather if no date is provided.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city, e.g., 'San Francisco', 'Tokyo', 'Rotterdam'.",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "The start date for the forecast in YYYY-MM-DD format. Optional, defaults to today."
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date for the forecast in YYYY-MM-DD format. Optional, defaults to the start_date."
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Performs a web search to find up-to-date information, facts, or answer questions about current events, people, or topics not found in the local database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to send to the search engine."
                    }
                },
                "required": ["query"],
            },
        },
    },
]


def execute_find_personal_variables(searchkey: str, username: str = "admin") -> dict:
    """
    Find and retrieve personal properties of the current user by searching a local database.
    Args:
        searchkey (str): The key for the personal variable to find.
        username (str): The username whose database to search. Defaults to "admin".
    Returns:
        dict: Status and data or message.
    """
    results = query_personal_variables(searchkey, username)
    if not results:
        return {"status": "success", "data": [], "message": f"I don't have any information about '{searchkey}'."}
    return {"status": "success", "data": results}


def execute_get_weather_forecast(city: str, start_date: str | None = None, end_date: str | None = None) -> dict:
    """
    Get the weather forecast for a specific city and date range.
    Args:
        city (str): City name.
        start_date (str | None, optional): Start date (YYYY-MM-DD).
        end_date (str | None, optional): End date (YYYY-MM-DD).
    Returns:
        dict: Status and weather data or error message.
    """
    try:
        today = date.today()
        start_date_obj = date.fromisoformat(start_date) if start_date else today
        end_date_obj = date.fromisoformat(end_date) if end_date else start_date_obj
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        if not geo_data:
            return {"error": f"City not found: {city}"}
        lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        daily_forecasts = {}
        for forecast in forecast_data.get('list', []):
            forecast_date = datetime.fromtimestamp(forecast['dt']).date()
            if start_date_obj <= forecast_date <= end_date_obj:
                day_str = forecast_date.isoformat()
                if day_str not in daily_forecasts:
                    daily_forecasts[day_str] = {"temps": [], "descriptions": {}}
                daily_forecasts[day_str]["temps"].append(forecast['main']['temp'])
                desc = forecast['weather'][0]['description']
                daily_forecasts[day_str]["descriptions"][desc] = daily_forecasts[day_str]["descriptions"].get(desc, 0) + 1
        if not daily_forecasts:
            return {"status": "success", "data": [], "message": f"No forecast data available for the selected dates in {city}."}
        results = []
        for day, data in sorted(daily_forecasts.items()):
            most_common_desc = max(data["descriptions"], key=data["descriptions"].get)
            results.append({"date": day, "city": city, "temp_min_celsius": min(data["temps"]),
                            "temp_max_celsius": max(data["temps"]), "description": most_common_desc})
        return {"status": "success", "data": results}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to weather API: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}


# --- [REPLACED] This is the new, standalone web search function ---
def execute_web_search(query: str) -> dict:
    """
    Perform a web search using the Google Custom Search JSON API.
    Args:
        query (str): The search query.
    Returns:
        dict: Status and search results or error message.
    """
    print(f"Executing web search for: {query}")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'q': query,
        'num': 5
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json()
        formatted_results = []
        for item in search_results.get("items", []):
            formatted_results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet")
            })
        if not formatted_results:
            return {"status": "success", "data": "No search results found."}
        return {"status": "success", "data": formatted_results}
    except Exception as e:
        print(f"An error occurred during web search: {e}")
        return {"error": f"Failed to execute web search. {e}"}


def execute_recall_memories(keyword: str, username: str = "admin") -> dict:
    """
    Recall past conversations by searching for a keyword in the user's prompt, the AI's reply, or the topic name.
    Args:
        keyword (str): The keyword to search for.
        username (str): The username whose database to search. Defaults to "admin".
    Returns:
        dict: Status and recall results or message.
    """
    results = recall_memories(keyword, username)
    if not results:
        return {"status": "success", "data": [], "message": f"No memories found for '{keyword}'."}
    for r in results:
        for k in ("user_prompt", "llm_reply"):
            if r[k] is None:
                r[k] = ""
            elif len(r[k]) > 200:
                r[k] = r[k][:200] + "..."
    return {"status": "success", "data": results}


def execute_recall_memories_with_time(keyword: str, username: str = "admin", start_date: str | None = None, end_date: str | None = None) -> dict:
    """
    Recall past conversations by searching for a keyword and limiting to a date or date range.
    Args:
        keyword (str): The keyword to search for.
        username (str): The username whose database to search. Defaults to "admin".
        start_date (str | None, optional): Start date (YYYY-MM-DD).
        end_date (str | None, optional): End date (YYYY-MM-DD).
    Returns:
        dict: Status and recall results or message.
    """
    results = recall_memories_with_time(keyword, username, start_date, end_date)
    if not results:
        return {"status": "success", "data": [], "message": f"No memories found for '{keyword}' in the given time range."}
    for r in results:
        for k in ("user_prompt", "llm_reply"):
            if r[k] is None:
                r[k] = ""
            elif len(r[k]) > 200:
                r[k] = r[k][:200] + "..."
    return {"status": "success", "data": results}


def execute_get_conversations_by_topic(topic_name: str, username: str = "admin") -> dict:
    """
    Find all conversations that contain a specific topic.
    Args:
        topic_name (str): The topic name to search for.
        username (str): The username whose database to search. Defaults to "admin".
    Returns:
        dict: Status and conversation results or message.
    """
    results = get_conversations_by_topic(topic_name, username)
    if not results:
        return {"status": "success", "data": [], "message": f"No conversations found containing topic '{topic_name}'."}
    return {"status": "success", "data": results}


def execute_get_topics_by_conversation(conversation_id: str, username: str = "admin") -> dict:
    """
    Get all topics that appear in a specific conversation.
    Args:
        conversation_id (str): The conversation ID to analyze.
        username (str): The username whose database to search. Defaults to "admin".
    Returns:
        dict: Status and topic results or message.
    """
    results = get_topics_by_conversation(conversation_id, username)
    if not results:
        return {"status": "success", "data": [], "message": f"No topics found for conversation '{conversation_id}'."}
    return {"status": "success", "data": results}


def execute_get_conversation_summary(conversation_id: str, username: str = "admin") -> dict:
    """
    Get a comprehensive summary of a conversation.
    Args:
        conversation_id (str): The conversation ID to summarize.
        username (str): The username whose database to search. Defaults to "admin".
    Returns:
        dict: Status and conversation summary or message.
    """
    summary = get_conversation_summary(conversation_id, username)
    if not summary:
        return {"status": "success", "data": {}, "message": f"Conversation '{conversation_id}' not found."}
    return {"status": "success", "data": summary}


def execute_get_topic_statistics(username: str = "admin") -> dict:
    """
    Get statistics about all topics across conversations.
    Args:
        username (str): The username whose database to search. Defaults to "admin".
    Returns:
        dict: Status and topic statistics or message.
    """
    results = get_topic_statistics(username)
    if not results:
        return {"status": "success", "data": [], "message": "No topic statistics available."}
    return {"status": "success", "data": results}