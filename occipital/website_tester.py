"""
Website Testing Module

Provides headless browser website testing capabilities for Tatlock UI components.
Uses Playwright for reliable cross-browser testing, visual regression testing, and website analysis.
"""

import asyncio
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install")
    Browser = None
    Page = None
    BrowserContext = None

logger = logging.getLogger(__name__)


class WebsiteTester:
    """
    Headless browser website testing for Tatlock UI components.
    
    Provides methods to capture screenshots of different pages and components,
    compare them for visual regression testing, analyze website behavior,
    and generate comprehensive test reports.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 username: str = "admin",
                 browser_type: str = "chromium",
                 screenshot_dir: str = None,
                 baseline_dir: str = None,
                 comparison_dir: str = None,
                 report_dir: str = None):
        """
        Initialize the website tester.
        
        Args:
            base_url: Base URL of the Tatlock application
            username: Username for user-specific storage
            browser_type: Browser to use (chromium, firefox, webkit)
            screenshot_dir: Optional custom screenshot directory
            baseline_dir: Optional custom baseline directory
            comparison_dir: Optional custom comparison directory
            report_dir: Optional custom report directory
        """
        self.base_url = base_url
        self.username = username
        self.browser_type = browser_type
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Create user-specific or custom directories
        self.user_base_dir = Path("hippocampus") / "shortterm" / username / "website_tester"
        self.screenshot_dir = Path(screenshot_dir) if screenshot_dir else self.user_base_dir / "screenshots"
        self.baseline_dir = Path(baseline_dir) if baseline_dir else self.user_base_dir / "baselines"
        self.comparison_dir = Path(comparison_dir) if comparison_dir else self.user_base_dir / "comparisons"
        self.report_dir = Path(report_dir) if report_dir else self.user_base_dir / "reports"
        
        # Create all directories
        for directory in [self.screenshot_dir, self.baseline_dir, self.comparison_dir, self.report_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Test configurations
        self.viewports = {
            'desktop': {'width': 1920, 'height': 1080},
            'tablet': {'width': 768, 'height': 1024},
            'mobile': {'width': 375, 'height': 667}
        }
        
        # Pages to test
        self.test_pages = [
            {'path': '/login', 'name': 'login_page'},
            {'path': '/profile', 'name': 'profile_page'},
            {'path': '/admin', 'name': 'admin_page'},
            {'path': '/chat', 'name': 'debug_console'},
        ]
    
    async def start_browser(self):
        """Start the headless browser."""
        if not Browser:
            raise ImportError("Playwright not available")
            
        self.playwright = await async_playwright().start()
        self.browser = await getattr(self.playwright, self.browser_type).launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
        logger.info(f"Started {self.browser_type} browser")
    
    async def stop_browser(self):
        """Stop the browser and cleanup."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        
        logger.info("Stopped browser")
    
    async def login_user(self, username: str = "admin", password: str = "admin"):
        """Login as a test user."""
        if not self.page:
            raise RuntimeError("Browser not started")
        
        await self.page.goto(f"{self.base_url}/login")
        await self.page.fill('input[name="username"]', username)
        await self.page.fill('input[name="password"]', password)
        await self.page.click('button[type="submit"]')
        
        # Wait for login to complete
        await self.page.wait_for_url(f"{self.base_url}/profile")
        logger.info(f"Logged in as {username}")
    
    async def capture_page_screenshot(self, path: str, name: str, 
                                    viewport: str = 'desktop') -> str:
        """
        Capture a screenshot of a specific page.
        
        Args:
            path: URL path to capture
            name: Name for the screenshot file
            viewport: Viewport size (desktop, tablet, mobile)
            
        Returns:
            Path to the captured screenshot
        """
        if not self.page:
            raise RuntimeError("Browser not started")
        
        # Set viewport
        viewport_size = self.viewports[viewport]
        await self.page.set_viewport_size(viewport_size)
        
        # Navigate to page
        url = f"{self.base_url}{path}"
        await self.page.goto(url, wait_until='networkidle')
        
        # Wait for page to fully load
        await asyncio.sleep(2)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{viewport}_{timestamp}.png"
        filepath = self.screenshot_dir / filename
        
        # Capture screenshot
        await self.page.screenshot(path=str(filepath), full_page=True)
        
        logger.info(f"Captured screenshot: {filepath}")
        return str(filepath)
    
    async def capture_component_screenshot(self, path: str, selector: str, 
                                         name: str, viewport: str = 'desktop') -> str:
        """
        Capture a screenshot of a specific component.
        
        Args:
            path: URL path to navigate to
            selector: CSS selector for the component
            name: Name for the screenshot file
            viewport: Viewport size (desktop, tablet, mobile)
            
        Returns:
            Path to the captured screenshot
        """
        if not self.page:
            raise RuntimeError("Browser not started")
        
        # Set viewport
        viewport_size = self.viewports[viewport]
        await self.page.set_viewport_size(viewport_size)
        
        # Navigate to page
        url = f"{self.base_url}{path}"
        await self.page.goto(url, wait_until='networkidle')
        
        # Wait for component to be available
        await self.page.wait_for_selector(selector)
        await asyncio.sleep(1)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{viewport}_{timestamp}.png"
        filepath = self.screenshot_dir / filename
        
        # Capture component screenshot
        element = await self.page.query_selector(selector)
        if element:
            await element.screenshot(path=str(filepath))
        
        logger.info(f"Captured component screenshot: {filepath}")
        return str(filepath)
    
    async def run_full_test_suite(self, login: bool = True) -> Dict[str, List[str]]:
        """
        Run the complete website test suite.
        
        Args:
            login: Whether to login before testing
            
        Returns:
            Dictionary with test results organized by test name
        """
        logger.info("Starting full website test suite...")
        
        try:
            await self.start_browser()
            
            if login:
                await self.login_user()
            
            results = {}
            
            # Test each page at each viewport
            for page_config in self.test_pages:
                page_path = page_config['path']
                page_name = page_config['name']
                
                page_results = []
                for viewport in self.viewports.keys():
                    try:
                        screenshot_path = await self.capture_page_screenshot(
                            page_path, page_name, viewport
                        )
                        page_results.append(screenshot_path)
                        logger.info(f"Captured {page_name} at {viewport} viewport")
                    except Exception as e:
                        logger.error(f"Failed to capture {page_name} at {viewport}: {e}")
                        page_results.append(None)
                
                results[page_name] = page_results
            
            return results
            
        finally:
            await self.stop_browser()
    
    async def test_navigation_layout(self) -> Dict[str, str]:
        """
        Test navigation layout and docking behavior.
        
        Returns:
            Dictionary with navigation test results
        """
        logger.info("Testing navigation layout...")
        
        try:
            await self.start_browser()
            await self.login_user()
            
            results = {}
            
            # Test navigation at different viewports
            for viewport in self.viewports.keys():
                try:
                    # Test admin page navigation
                    screenshot_path = await self.capture_component_screenshot(
                        '/admin', '.sidebar-nav', f'nav_admin_{viewport}', viewport
                    )
                    results[f'admin_nav_{viewport}'] = screenshot_path
                    
                    # Test chat page navigation
                    screenshot_path = await self.capture_component_screenshot(
                        '/chat', '.chat-sidepane', f'nav_chat_{viewport}', viewport
                    )
                    results[f'chat_nav_{viewport}'] = screenshot_path
                    
                    logger.info(f"Tested navigation layout at {viewport} viewport")
                    
                except Exception as e:
                    logger.error(f"Failed to test navigation at {viewport}: {e}")
                    results[f'nav_{viewport}'] = None
            
            return results
            
        finally:
            await self.stop_browser()
    
    def generate_test_report(self, results: Dict[str, List[str]]) -> str:
        """
        Generate an HTML test report from the test results.
        
        Args:
            results: Dictionary with test results
            
        Returns:
            Path to the generated HTML report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"test_report_{timestamp}.html"
        report_path = self.report_dir / report_filename
        
        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Website Test Report - {timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; text-align: center; margin-bottom: 30px; }}
                .test-section {{ margin-bottom: 30px; border: 1px solid #ddd; border-radius: 5px; padding: 15px; }}
                .test-title {{ font-size: 18px; font-weight: bold; color: #444; margin-bottom: 15px; }}
                .viewport-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }}
                .viewport-item {{ text-align: center; }}
                .viewport-label {{ font-weight: bold; color: #666; margin-bottom: 10px; }}
                img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }}
                .timestamp {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Website Test Report</h1>
                <div class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        """
        
        for test_name, screenshots in results.items():
            html_content += f"""
                <div class="test-section">
                    <div class="test-title">{test_name.replace('_', ' ').title()}</div>
                    <div class="viewport-grid">
            """
            
            viewports = list(self.viewports.keys())
            for i, viewport in enumerate(viewports):
                screenshot_path = screenshots[i] if i < len(screenshots) else None
                
                if screenshot_path and os.path.exists(screenshot_path):
                    # Convert to relative path for HTML
                    relative_path = os.path.relpath(screenshot_path, self.screenshot_dir)
                    html_content += f"""
                        <div class="viewport-item">
                            <div class="viewport-label">{viewport.title()}</div>
                            <img src="{relative_path}" alt="{test_name} - {viewport}">
                            <div style="font-size: 12px; color: #666; margin-top: 5px;">{relative_path}</div>
                        </div>
                    """
                else:
                    html_content += f"""
                        <div class="viewport-item">
                            <div class="viewport-label">{viewport.title()}</div>
                            <div style="color: #999; font-style: italic;">Screenshot not available</div>
                        </div>
                    """
            
            html_content += """
                    </div>
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        # Write the report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Generated test report: {report_path}")
        return str(report_path)
    
    async def take_screenshot_from_url(self, url: str, output_path: str) -> str:
        """
        Take a screenshot from any URL and save it to the specified path.
        
        Args:
            url: The URL to capture
            output_path: Path where to save the screenshot
            
        Returns:
            Path to the saved screenshot
        """
        logger.info(f"Taking screenshot from URL: {url}")
        
        try:
            await self.start_browser()
            
            # Navigate to the URL
            await self.page.goto(url, wait_until='networkidle')
            
            # Wait for page to fully load
            await asyncio.sleep(3)
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Take screenshot
            await self.page.screenshot(path=output_path, full_page=True)
            
            logger.info(f"Screenshot saved to: {output_path}")
            return output_path
            
        finally:
            await self.stop_browser()


async def main():
    """Main function for testing the website tester."""
    tester = WebsiteTester()
    
    # Run full test suite
    results = await tester.run_full_test_suite()
    
    # Generate report
    report_path = tester.generate_test_report(results)
    print(f"Test report generated: {report_path}")
    
    # Test navigation layout
    nav_results = await tester.test_navigation_layout()
    print(f"Navigation tests completed: {len(nav_results)} tests")


if __name__ == "__main__":
    asyncio.run(main()) 