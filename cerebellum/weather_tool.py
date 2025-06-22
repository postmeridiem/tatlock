"""
cerebellum/weather_tool.py

Weather forecast functionality using OpenWeather API.
"""

import requests
import logging
from datetime import date, datetime
from config import OPENWEATHER_API_KEY

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_get_weather_forecast(city: str, start_date: str | None = None, end_date: str | None = None) -> dict:
    """
    Get the weather forecast for a specific city and date range.
    
    Args:
        city (str): City name (e.g., 'San Francisco', 'Tokyo', 'Rotterdam').
        start_date (str | None, optional): Start date (YYYY-MM-DD). Defaults to today.
        end_date (str | None, optional): End date (YYYY-MM-DD). Defaults to start_date.
        
    Returns:
        dict: Status and weather data or error message.
    """
    try:
        # Check if API key is configured
        if not OPENWEATHER_API_KEY:
            return {
                "status": "error",
                "message": "Weather forecast is not available. OpenWeather API key is not configured. Please set OPENWEATHER_API_KEY environment variable to enable weather functionality."
            }
        
        today = date.today()
        start_date_obj = date.fromisoformat(start_date) if start_date else today
        end_date_obj = date.fromisoformat(end_date) if end_date else start_date_obj
        
        # Get city coordinates
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data:
            return {"status": "error", "message": f"City not found: {city}"}
        
        lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
        
        # Get weather forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        # Process forecast data
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
        
        # Format results
        results = []
        for day, data in sorted(daily_forecasts.items()):
            most_common_desc = max(data["descriptions"], key=data["descriptions"].get)
            results.append({
                "date": day, 
                "city": city, 
                "temp_min_celsius": min(data["temps"]),
                "temp_max_celsius": max(data["temps"]), 
                "description": most_common_desc
            })
        
        return {"status": "success", "data": results}
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during weather forecast: {e}")
        return {"status": "error", "message": f"Failed to connect to weather API: {e}"}
    except ValueError as e:
        logger.error(f"Invalid date format in weather forecast: {e}")
        return {"status": "error", "message": f"Invalid date format: {e}"}
    except Exception as e:
        logger.error(f"An unexpected error occurred during weather forecast: {e}")
        return {"status": "error", "message": f"An unexpected error occurred: {e}"} 