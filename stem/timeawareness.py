"""
stem/timeawareness.py

Date/time parsing helpers for natural language expressions in Tatlock project.
"""

import sqlite3
import os
from config import DATABASE_PATH
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import re

def parse_natural_date_range(text: str) -> tuple[str|None, str|None]:
    """
    Parse natural language date expressions and return (start_date, end_date) as YYYY-MM-DD strings.
    Returns (None, None) if no match.
    Args:
        text (str): The natural language date expression.
    Returns:
        tuple[str|None, str|None]: (start_date, end_date) in YYYY-MM-DD format, or (None, None) if not recognized.
    """
    text = text.lower().strip()
    today = date.today()

    if 'today' in text:
        return today.isoformat(), today.isoformat()
    if 'yesterday' in text:
        yest = today - timedelta(days=1)
        return yest.isoformat(), yest.isoformat()
    if 'tomorrow' in text:
        tomo = today + timedelta(days=1)
        return tomo.isoformat(), tomo.isoformat()
    if 'last week' in text:
        # Last week: previous Monday to previous Sunday
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=6)
        return start.isoformat(), end.isoformat()
    if 'this week' in text:
        # This week: this Monday to today
        start = today - timedelta(days=today.weekday())
        return start.isoformat(), today.isoformat()
    if 'last month' in text:
        first_this_month = today.replace(day=1)
        last_month = first_this_month - timedelta(days=1)
        start = last_month.replace(day=1)
        end = last_month
        return start.isoformat(), end.isoformat()
    if 'this month' in text:
        start = today.replace(day=1)
        return start.isoformat(), today.isoformat()
    # Patterns like 'on June 5', 'on 2023-06-05', 'from June 1 to June 7', etc.
    date_patterns = [
        (r'on (\w+ \d{1,2},? \d{4})', '%B %d, %Y'),
        (r'on (\w+ \d{1,2})', '%B %d'),
        (r'on (\d{4}-\d{2}-\d{2})', '%Y-%m-%d'),
        (r'from (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})', '%Y-%m-%d'),
    ]
    for pat, fmt in date_patterns:
        m = re.search(pat, text)
        if m:
            try:
                if 'from' in pat:
                    start = datetime.strptime(m.group(1), fmt).date()
                    end = datetime.strptime(m.group(2), fmt).date()
                    return start.isoformat(), end.isoformat()
                else:
                    d = datetime.strptime(m.group(1), fmt).date()
                    return d.isoformat(), d.isoformat()
            except Exception:
                continue
    return None, None 