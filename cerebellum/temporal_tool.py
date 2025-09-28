"""
cerebellum/temporal_tool.py

Comprehensive temporal information tool for Tatlock.
Provides current date/time information and handles natural language temporal queries.
"""

import logging
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as dateutil_parse
import calendar
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_temporal_info(temporal_query: str) -> Dict[str, Any]:
    """
    Get comprehensive temporal information for any date/time query.

    Handles natural language expressions like:
    - Basic: "today", "yesterday", "tomorrow", "now", "current time"
    - Relative: "last week", "next month", "3 days ago", "in 2 weeks"
    - Specific: "next Friday", "last Tuesday", "this weekend"
    - Periods: "this month", "last year", "this quarter"
    - Calculations: "beginning of month", "end of year"

    Args:
        temporal_query (str): Natural language temporal expression

    Returns:
        Dict containing temporal information with multiple formats
    """
    try:
        now = datetime.now()
        today = now.date()
        query = temporal_query.lower().strip()

        logger.info(f"Processing temporal query: '{query}'")

        # Initialize result with current context
        result = {
            "query": temporal_query,
            "current_datetime": now.isoformat(),
            "current_date": today.isoformat(),
            "current_time": now.strftime("%H:%M:%S"),
            "current_year": now.year,
            "current_month": now.month,
            "current_day": now.day,
            "current_weekday": now.strftime("%A"),
            "timezone": str(now.astimezone().tzinfo)
        }

        # Parse the temporal query
        target_date, target_datetime = _parse_temporal_expression(query, now, today)

        if target_date:
            # Add comprehensive information about the target date
            result.update({
                "target_date": target_date.isoformat(),
                "target_year": target_date.year,
                "target_month": target_date.month,
                "target_day": target_date.day,
                "target_weekday": target_date.strftime("%A"),
                "target_month_name": target_date.strftime("%B"),
                "formatted_date": target_date.strftime("%B %d, %Y"),
                "days_from_today": (target_date - today).days,
                "is_past": target_date < today,
                "is_future": target_date > today,
                "is_today": target_date == today
            })

        if target_datetime:
            result.update({
                "target_datetime": target_datetime.isoformat(),
                "target_time": target_datetime.strftime("%H:%M:%S"),
                "hours_from_now": round((target_datetime - now).total_seconds() / 3600, 2)
            })

        # Add contextual information
        result.update(_get_contextual_info(query, now, today))

        logger.debug(f"Temporal query result: {result}")
        return {"status": "success", "data": result}

    except Exception as e:
        logger.error(f"Error processing temporal query '{temporal_query}': {e}")
        return {
            "status": "error",
            "message": f"Could not process temporal query: {str(e)}",
            "current_date": datetime.now().date().isoformat(),
            "current_time": datetime.now().strftime("%H:%M:%S")
        }

def _parse_temporal_expression(query: str, now: datetime, today: date) -> tuple:
    """Parse temporal expression and return target date/datetime."""
    target_date = None
    target_datetime = None

    # Basic temporal expressions
    if query in ["today", "now"]:
        target_date = today
        target_datetime = now

    elif query == "yesterday":
        target_date = today - timedelta(days=1)

    elif query == "tomorrow":
        target_date = today + timedelta(days=1)

    elif query in ["current time", "time now", "what time is it"]:
        target_datetime = now

    # Days of the week
    elif "last" in query and any(day in query for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
        target_date = _get_last_weekday(query, today)

    elif "next" in query and any(day in query for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
        target_date = _get_next_weekday(query, today)

    elif "this" in query and any(day in query for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
        target_date = _get_this_weekday(query, today)

    # Relative expressions with numbers
    elif re.search(r'\d+\s*(day|week|month|year)s?\s*(ago|from now|later)', query):
        target_date = _parse_relative_expression(query, today)

    # Period expressions
    elif "this week" in query:
        target_date = _get_week_start(today)

    elif "last week" in query:
        target_date = _get_week_start(today - timedelta(weeks=1))

    elif "next week" in query:
        target_date = _get_week_start(today + timedelta(weeks=1))

    elif "this month" in query:
        target_date = today.replace(day=1)

    elif "last month" in query:
        target_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)

    elif "next month" in query:
        target_date = (today.replace(day=1) + relativedelta(months=1))

    elif "this year" in query:
        target_date = today.replace(month=1, day=1)

    elif "last year" in query:
        target_date = today.replace(year=today.year-1, month=1, day=1)

    elif "next year" in query:
        target_date = today.replace(year=today.year+1, month=1, day=1)

    # Beginning/end expressions
    elif "beginning of" in query or "start of" in query:
        target_date = _get_period_start(query, today)

    elif "end of" in query:
        target_date = _get_period_end(query, today)

    return target_date, target_datetime

def _get_last_weekday(query: str, today: date) -> date:
    """Get the date of the last occurrence of a weekday."""
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }

    for day_name, day_num in weekdays.items():
        if day_name in query:
            days_back = (today.weekday() - day_num) % 7
            if days_back == 0:  # Same day, go back a week
                days_back = 7
            return today - timedelta(days=days_back)

    return today

def _get_next_weekday(query: str, today: date) -> date:
    """Get the date of the next occurrence of a weekday."""
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }

    for day_name, day_num in weekdays.items():
        if day_name in query:
            days_ahead = (day_num - today.weekday()) % 7
            if days_ahead == 0:  # Same day, go forward a week
                days_ahead = 7
            return today + timedelta(days=days_ahead)

    return today

def _get_this_weekday(query: str, today: date) -> date:
    """Get the date of a weekday in the current week."""
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }

    for day_name, day_num in weekdays.items():
        if day_name in query:
            days_diff = day_num - today.weekday()
            return today + timedelta(days=days_diff)

    return today

def _parse_relative_expression(query: str, today: date) -> date:
    """Parse expressions like '3 days ago', 'in 2 weeks', etc."""
    # Match patterns like "3 days ago", "in 2 weeks", "5 months from now"
    pattern = r'(\d+)\s*(day|week|month|year)s?\s*(ago|from now|later)'
    match = re.search(pattern, query)

    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        direction = match.group(3)

        if direction == "ago":
            amount = -amount

        if unit == "day":
            return today + timedelta(days=amount)
        elif unit == "week":
            return today + timedelta(weeks=amount)
        elif unit == "month":
            return today + relativedelta(months=amount)
        elif unit == "year":
            return today + relativedelta(years=amount)

    return today

def _get_week_start(target_date: date) -> date:
    """Get the Monday of the week containing the target date."""
    return target_date - timedelta(days=target_date.weekday())

def _get_period_start(query: str, today: date) -> date:
    """Get the start of a period (month, year, etc.)."""
    if "month" in query:
        return today.replace(day=1)
    elif "year" in query:
        return today.replace(month=1, day=1)
    elif "week" in query:
        return _get_week_start(today)
    return today

def _get_period_end(query: str, today: date) -> date:
    """Get the end of a period (month, year, etc.)."""
    if "month" in query:
        last_day = calendar.monthrange(today.year, today.month)[1]
        return today.replace(day=last_day)
    elif "year" in query:
        return today.replace(month=12, day=31)
    elif "week" in query:
        return _get_week_start(today) + timedelta(days=6)
    return today

def _get_contextual_info(query: str, now: datetime, today: date) -> Dict[str, Any]:
    """Add contextual information based on the query."""
    context = {}

    # Add week information
    context["week_start"] = _get_week_start(today).isoformat()
    context["week_end"] = (_get_week_start(today) + timedelta(days=6)).isoformat()

    # Add month information
    context["month_start"] = today.replace(day=1).isoformat()
    last_day = calendar.monthrange(today.year, today.month)[1]
    context["month_end"] = today.replace(day=last_day).isoformat()

    # Add year information
    context["year_start"] = today.replace(month=1, day=1).isoformat()
    context["year_end"] = today.replace(month=12, day=31).isoformat()

    # Add useful relative dates
    context["yesterday"] = (today - timedelta(days=1)).isoformat()
    context["tomorrow"] = (today + timedelta(days=1)).isoformat()

    return context

# Tool execution wrapper for the agent system
def execute_get_temporal_info(temporal_query: str, username: str = "admin") -> Dict[str, Any]:
    """
    Execute temporal info tool with standardized interface.

    Args:
        temporal_query (str): Natural language temporal expression
        username (str): Username (not used but required for tool interface)

    Returns:
        Dict containing temporal information
    """
    return get_temporal_info(temporal_query)