"""
Test module for occipital screenshot testing functionality.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import shutil

from occipital.website_tester import WebsiteTester
from occipital.visual_analyzer import VisualAnalyzer
from occipital.run_tests import ScreenshotTestRunner


class TestWebsiteTester:
    """Test cases for WebsiteTester class."""
    
    def test_init(self):
        """Test WebsiteTester initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tester = WebsiteTester(screenshot_dir=f"{temp_dir}/screenshots")
            assert tester.base_url == "http://localhost:8000"
            assert tester.browser_type == "chromium"
            assert tester.screenshot_dir.exists()
            # Test custom initialization
            tester = WebsiteTester(
                base_url="http://test:9000",
                screenshot_dir=f"{temp_dir}/test_screenshots",
                browser_type="firefox"
            )
            assert tester.base_url == "http://test:9000"
            assert tester.browser_type == "firefox"
            assert "test_screenshots" in str(tester.screenshot_dir)
    
    def test_viewport_configurations(self):
        """Test viewport configurations."""
        tester = WebsiteTester()
        
        assert 'desktop' in tester.viewports
        assert 'tablet' in tester.viewports
        assert 'mobile' in tester.viewports
        
        assert tester.viewports['desktop']['width'] == 1920
        assert tester.viewports['desktop']['height'] == 1080
        assert tester.viewports['tablet']['width'] == 768
        assert tester.viewports['mobile']['width'] == 375
    
    def test_test_pages_configuration(self):
        """Test test pages configuration."""
        tester = WebsiteTester()
        
        expected_pages = ['login_page', 'profile_page', 'admin_page', 'debug_console']
        actual_pages = [page['name'] for page in tester.test_pages]
        
        assert all(page in actual_pages for page in expected_pages)
    
    @pytest.mark.asyncio
    async def test_start_browser_no_playwright(self):
        """Test browser start without Playwright."""
        with patch('occipital.website_tester.Browser', None):
            tester = WebsiteTester()
            with pytest.raises(ImportError, match="Playwright not available"):
                await tester.start_browser()
    
    @pytest.mark.asyncio
    async def test_login_user_no_browser(self):
        """Test login without browser started."""
        tester = WebsiteTester()
        with pytest.raises(RuntimeError, match="Browser not started"):
            await tester.login_user()
    
    def test_generate_test_report(self):
        """Test test report generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tester = WebsiteTester(screenshot_dir=f"{temp_dir}/screenshots", report_dir=f"{temp_dir}/reports")
            # Mock results
            results = {
                'login_page': ['/path/to/login_desktop_20240101_120000.png'],
                'admin_page': ['/path/to/admin_desktop_20240101_120000.png']
            }
            
            report_path = tester.generate_test_report(results)
            
            assert Path(report_path).exists()
            assert report_path.endswith('.html')
            
            # Check report content
            with open(report_path, 'r') as f:
                content = f.read()
                assert 'Website Test Report' in content or 'Tatlock Screenshot Test Report' in content
                assert 'Login Page' in content
                assert 'Admin Page' in content


class TestVisualAnalyzer:
    """Test cases for VisualAnalyzer class."""
    
    def test_init(self):
        """Test VisualAnalyzer initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = VisualAnalyzer(baseline_dir=f"{temp_dir}/test_baselines", comparison_dir=f"{temp_dir}/test_comparisons")
            assert "test_baselines" in str(analyzer.baseline_dir)
            assert "test_comparisons" in str(analyzer.comparison_dir)
    
    def test_find_baseline_screenshot_no_baseline(self):
        """Test finding baseline when none exists."""
        analyzer = VisualAnalyzer()
        
        baseline = analyzer.find_baseline_screenshot("nonexistent_test")
        assert baseline is None
    
    def test_update_baseline_file_not_found(self):
        """Test updating baseline with non-existent file."""
        analyzer = VisualAnalyzer()
        
        with pytest.raises(FileNotFoundError):
            analyzer.update_baseline("nonexistent_file.png", "test", "desktop")
    
    def test_run_visual_regression_tests_no_baselines(self):
        """Test visual regression tests with no baselines."""
        analyzer = VisualAnalyzer()
        
        # Mock screenshot results
        screenshot_results = {
            'login_page': ['/path/to/login_desktop_20240101_120000.png'],
            'admin_page': ['/path/to/admin_desktop_20240101_120000.png']
        }
        
        results = analyzer.run_visual_regression_tests(screenshot_results)
        
        assert 'login_page' in results
        assert 'admin_page' in results
        
        # All should be marked as new baselines
        for test_results in results.values():
            for result in test_results.values():
                assert result.get('new_baseline') is True
                assert result.get('passed') is True
    
    def test_generate_regression_report(self):
        """Test regression report generation."""
        analyzer = VisualAnalyzer()
        
        # Mock regression results
        regression_results = {
            'login_page': {
                'login_page_desktop': {
                    'passed': True,
                    'new_baseline': True,
                    'screenshot_path': '/path/to/screenshot.png'
                }
            }
        }
        
        report_path = analyzer.generate_regression_report(regression_results)
        
        assert Path(report_path).exists()
        assert report_path.endswith('.html')
        
        # Check report content
        with open(report_path, 'r') as f:
            content = f.read()
            assert 'Tatlock Visual Regression Test Report' in content
            assert 'Login Page' in content  # The title is converted to "Login Page"


class TestScreenshotTestRunner:
    """Test cases for ScreenshotTestRunner class."""
    
    def test_init(self):
        """Test ScreenshotTestRunner initialization."""
        runner = ScreenshotTestRunner()
        
        assert runner.base_url == "http://localhost:8000"
        assert isinstance(runner.tester, WebsiteTester)
        assert isinstance(runner.analyzer, VisualAnalyzer)
    
    def test_generate_summary(self):
        """Test summary generation."""
        runner = ScreenshotTestRunner()
        
        # Mock results
        screenshot_results = {
            'login_page': ['/path/to/login_desktop.png', '/path/to/login_tablet.png'],
            'admin_page': ['/path/to/admin_desktop.png']
        }
        
        regression_results = {
            'login_page': {
                'login_page_desktop': {'passed': True, 'new_baseline': False},
                'login_page_tablet': {'passed': False, 'new_baseline': False}
            },
            'admin_page': {
                'admin_page_desktop': {'passed': True, 'new_baseline': True}
            }
        }
        
        summary = runner._generate_summary(screenshot_results, regression_results)
        
        assert summary['total_screenshots'] == 3
        assert summary['total_regression_tests'] == 3
        assert summary['passed_regression_tests'] == 1  # Only one passed (not new baseline)
        assert summary['failed_regression_tests'] == 1
        assert summary['new_baselines'] == 1
        assert summary['success_rate'] == pytest.approx(33.33, rel=0.01)


@pytest.mark.asyncio
async def test_integration_without_playwright():
    """Test integration without Playwright installed."""
    with patch('occipital.website_tester.Browser', None):
        with pytest.raises(ImportError):
            tester = WebsiteTester()
            await tester.start_browser()


def test_directory_creation():
    """Test that directories are created properly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test WebsiteTester directory creation
        screenshot_dir = Path(temp_dir) / "screenshots"
        tester = WebsiteTester(screenshot_dir=str(screenshot_dir))
        assert screenshot_dir.exists()
        
        # Test VisualAnalyzer directory creation
        baseline_dir = Path(temp_dir) / "baselines"
        analyzer = VisualAnalyzer(baseline_dir=str(baseline_dir))
        assert baseline_dir.exists()


if __name__ == "__main__":
    pytest.main([__file__]) 