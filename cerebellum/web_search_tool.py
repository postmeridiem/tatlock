"""
cerebellum/web_search_tool.py

Web search functionality using Google Custom Search API.
"""

import requests
import logging
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_web_search(query: str) -> dict:
    """
    Perform a web search using the Google Custom Search JSON API.
    
    Args:
        query (str): The search query to send to the search engine.
        
    Returns:
        dict: Status and search results or error message.
    """
    try:
        # Check if API keys are configured
        if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
            return {
                "status": "error", 
                "message": "Web search is not available. Google API keys are not configured. Please set GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables to enable web search functionality."
            }
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_CSE_ID,
            'q': query,
            'num': 5
        }
        
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
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during web search: {e}")
        return {"status": "error", "message": f"Failed to connect to search API: {e}"}
    except Exception as e:
        logger.error(f"An error occurred during web search: {e}")
        return {"status": "error", "message": f"Failed to execute web search: {e}"} 