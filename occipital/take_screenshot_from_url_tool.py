"""
occipital/take_screenshot_from_url_tool.py

Screenshot and analysis tools for capturing and analyzing website screenshots.
"""

import logging
from typing import Optional
from hippocampus.user_database import get_user_image_path
from occipital.website_tester import WebsiteTester
from playwright.sync_api import sync_playwright

# Set up logging for this module
logger = logging.getLogger(__name__)


async def execute_take_screenshot_from_url(url: str, session_id: str, username: str = "admin") -> dict:
    """
    Take a full-page screenshot of a webpage and save it to the user's shortterm storage.
    
    Args:
        url (str): The URL of the webpage to capture as a screenshot.
        session_id (str): A unique session identifier for this screenshot. Use a descriptive name or timestamp.
        username (str): The username whose storage to use. Defaults to "admin".
        
    Returns:
        dict: Status and file information or error details.
    """
    try:
        # Get the file path for this user/session
        file_path = get_user_image_path(username, session_id, ext="png")
        
        # Take the screenshot
        tester = WebsiteTester(username=username)
        await tester.take_screenshot_from_url(url, file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "session_id": session_id,
            "url": url,
            "message": f"Screenshot saved successfully for session {session_id}"
        }
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        return {
            "success": False,
            "error": str(e),
            "session_id": session_id,
            "url": url
        }


def sync_take_screenshot(url: str, file_path: str, cookies: dict = None, wait_for_timeout: int = 5000) -> dict:
    """
    Takes a screenshot of a URL and saves it to a file.

    Args:
        url: The URL to take a screenshot of.
        file_path: The path to save the screenshot to.
        cookies: A dictionary of cookies to set in the browser context.
        wait_for_timeout: The time in milliseconds to wait before taking the screenshot.

    Returns:
        A dictionary with the status of the operation.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(viewport={'width': 2000, 'height': 1080})
            if cookies:
                context.add_cookies([{"name": k, "value": v, "domain": "localhost", "path": "/"} for k, v in cookies.items()])
            page = context.new_page()
            page.goto(url, wait_until='networkidle')
            if wait_for_timeout > 0:
                page.wait_for_timeout(wait_for_timeout)
            
            page.screenshot(path=file_path, full_page=True)
                
            browser.close()
        return {"status": "success", "file_path": file_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def analyze_screenshot_file(session_id: str, original_prompt: Optional[str], username: str = "admin") -> dict:
    """
    Analyze a screenshot file stored in the user's shortterm storage.
    
    Args:
        session_id (str): The session ID of the file to analyze (same as used when taking screenshot).
        original_prompt (Optional[str]): The original user prompt that led to this file being created, for context in analysis.
        username (str): The username whose storage to use. Defaults to "admin".
        
    Returns:
        dict: Analysis results or error details.
    """
    try:
        import os
        
        # Get the file path
        file_path = get_user_image_path(username, session_id, ext="png")
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found for session {session_id}",
                "session_id": session_id
            }
        
        # For now, we'll provide a basic analysis
        # In the future, this could integrate with computer vision APIs
        file_size = os.path.getsize(file_path)
        
        analysis = {
            "file_path": file_path,
            "file_size_bytes": file_size,
            "file_type": "PNG image",
            "session_id": session_id,
            "analysis_summary": f"Image file captured for session {session_id}. File size: {file_size} bytes.",
            "insights": [
                "This appears to be a webpage screenshot",
                "The image is stored in PNG format",
                f"Original prompt context: {original_prompt}",
                "For detailed image analysis, consider using computer vision APIs"
            ],
            "recommendations": [
                "The screenshot has been successfully captured and stored",
                "You can now analyze the visual content manually",
                "Consider the original prompt context when interpreting the image"
            ]
        }
        
        return {
            "success": True,
            "analysis": analysis,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error analyzing file: {e}")
        return {
            "success": False,
            "error": str(e),
            "session_id": session_id
        }