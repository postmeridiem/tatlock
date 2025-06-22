"""
Website Test Runner

Main script for running comprehensive website tests and visual regression analysis.
Combines WebsiteTester and VisualAnalyzer for complete visual testing workflow.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List

from .website_tester import WebsiteTester
from .visual_analyzer import VisualAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:\t  %(name)s - %(message)s %(asctime)s'
)
logger = logging.getLogger(__name__)


class ScreenshotTestRunner:
    """
    Main test runner that orchestrates website testing and visual analysis.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", username: str = "admin"):
        """
        Initialize the test runner.
        
        Args:
            base_url: Base URL of the Tatlock application
            username: Username for user-specific storage
        """
        self.base_url = base_url
        self.username = username
        self.tester = WebsiteTester(base_url=base_url, username=username)
        self.analyzer = VisualAnalyzer(username=username)
    
    async def run_complete_test_suite(self, update_baselines: bool = False) -> Dict:
        """
        Run the complete test suite including screenshots and regression analysis.
        
        Args:
            update_baselines: Whether to update baseline screenshots
            
        Returns:
            Dictionary with complete test results
        """
        logger.info("Starting complete screenshot test suite...")
        
        # Step 1: Capture screenshots
        logger.info("Step 1: Capturing screenshots...")
        screenshot_results = await self.tester.run_full_test_suite()
        
        # Step 2: Run visual regression tests
        logger.info("Step 3: Running visual regression tests...")
        regression_results = self.analyzer.run_visual_regression_tests(screenshot_results)
        
        # Step 3: Update baselines if requested
        if update_baselines:
            logger.info("Step 3: Updating baselines...")
            self._update_baselines(screenshot_results)
        
        # Step 4: Generate reports
        logger.info("Step 4: Generating reports...")
        screenshot_report = self.tester.generate_test_report(screenshot_results)
        regression_report = self.analyzer.generate_regression_report(regression_results)
        
        # Step 5: Test navigation layout specifically
        logger.info("Step 5: Testing navigation layout...")
        nav_results = await self.tester.test_navigation_layout()
        
        return {
            'screenshot_results': screenshot_results,
            'regression_results': regression_results,
            'navigation_results': nav_results,
            'screenshot_report': screenshot_report,
            'regression_report': regression_report,
            'summary': self._generate_summary(screenshot_results, regression_results)
        }
    
    def _update_baselines(self, screenshot_results: Dict[str, List[str]]):
        """Update baseline screenshots."""
        for test_name, screenshots in screenshot_results.items():
            for screenshot_path in screenshots:
                # Extract viewport from filename
                filename = Path(screenshot_path).name
                viewport = 'desktop'
                if '_tablet_' in filename:
                    viewport = 'tablet'
                elif '_mobile_' in filename:
                    viewport = 'mobile'
                
                self.analyzer.update_baseline(screenshot_path, test_name, viewport)
    
    def _generate_summary(self, screenshot_results: Dict[str, List[str]], 
                         regression_results: Dict[str, Dict]) -> Dict:
        """Generate a summary of test results."""
        total_screenshots = sum(len(screenshots) for screenshots in screenshot_results.values())
        
        total_regression_tests = 0
        passed_regression_tests = 0
        failed_regression_tests = 0
        new_baselines = 0
        
        for test_results in regression_results.values():
            for result in test_results.values():
                total_regression_tests += 1
                if result.get('new_baseline'):
                    new_baselines += 1
                elif result.get('passed'):
                    passed_regression_tests += 1
                else:
                    failed_regression_tests += 1
        
        return {
            'total_screenshots': total_screenshots,
            'total_regression_tests': total_regression_tests,
            'passed_regression_tests': passed_regression_tests,
            'failed_regression_tests': failed_regression_tests,
            'new_baselines': new_baselines,
            'success_rate': (passed_regression_tests / total_regression_tests * 100) if total_regression_tests > 0 else 0
        }
    
    async def test_specific_page(self, page_path: str, page_name: str, 
                               viewports: List[str] = None) -> Dict:
        """
        Test a specific page at specified viewports.
        
        Args:
            page_path: URL path to test
            page_name: Name for the test
            viewports: List of viewports to test (desktop, tablet, mobile)
            
        Returns:
            Dictionary with test results
        """
        if viewports is None:
            viewports = ['desktop']
        
        logger.info(f"Testing specific page: {page_path}")
        
        try:
            await self.tester.start_browser()
            await self.tester.login_user()
            
            results = {}
            for viewport in viewports:
                try:
                    screenshot_path = await self.tester.capture_page_screenshot(
                        page_path, page_name, viewport
                    )
                    results[viewport] = screenshot_path
                except Exception as e:
                    logger.error(f"Failed to capture {page_name} at {viewport}: {e}")
                    results[viewport] = None
            
            return results
        
        finally:
            await self.tester.stop_browser()
    
    async def test_navigation_docking(self) -> Dict:
        """
        Test specifically for navigation docking behavior.
        
        Returns:
            Dictionary with navigation test results
        """
        logger.info("Testing navigation docking behavior...")
        return await self.tester.test_navigation_layout()


async def main():
    """Main function for running the test suite."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Tatlock screenshot tests')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='Base URL of Tatlock application')
    parser.add_argument('--username', default='admin',
                       help='Username for user-specific storage')
    parser.add_argument('--update-baselines', action='store_true',
                       help='Update baseline screenshots')
    parser.add_argument('--test-page', help='Test specific page (e.g., /admin)')
    parser.add_argument('--page-name', help='Name for specific page test')
    parser.add_argument('--navigation-only', action='store_true',
                       help='Test only navigation layout')
    
    args = parser.parse_args()
    
    # Check if server is running
    import requests
    try:
        response = requests.get(args.url, timeout=5)
        if response.status_code != 200:
            logger.warning(f"Server responded with status {response.status_code}")
    except requests.exceptions.RequestException:
        logger.error(f"Cannot connect to server at {args.url}")
        logger.error("Please start the Tatlock server first: python main.py")
        sys.exit(1)
    
    runner = ScreenshotTestRunner(base_url=args.url, username=args.username)
    
    try:
        if args.navigation_only:
            # Test only navigation
            results = await runner.test_navigation_docking()
            print(f"Navigation tests completed: {len(results)} screenshots")
            
        elif args.test_page:
            # Test specific page
            if not args.page_name:
                args.page_name = args.test_page.replace('/', '').replace('-', '_')
            
            results = await runner.test_specific_page(args.test_page, args.page_name)
            print(f"Page test completed: {len(results)} screenshots")
            
        else:
            # Run complete test suite
            results = await runner.run_complete_test_suite(update_baselines=args.update_baselines)
            
            summary = results['summary']
            print("\n" + "="*50)
            print("SCREENSHOT TEST SUMMARY")
            print("="*50)
            print(f"Total Screenshots: {summary['total_screenshots']}")
            print(f"Regression Tests: {summary['total_regression_tests']}")
            print(f"Passed: {summary['passed_regression_tests']}")
            print(f"Failed: {summary['failed_regression_tests']}")
            print(f"New Baselines: {summary['new_baselines']}")
            print(f"Success Rate: {summary['success_rate']:.1f}%")
            print("="*50)
            print(f"Screenshot Report: {results['screenshot_report']}")
            print(f"Regression Report: {results['regression_report']}")
            print("="*50)
            
            if summary['failed_regression_tests'] > 0:
                print(f"\n⚠️  {summary['failed_regression_tests']} visual regression tests failed!")
                print("Check the regression report for details.")
                sys.exit(1)
            else:
                print("\n✅ All visual regression tests passed!")
    
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 