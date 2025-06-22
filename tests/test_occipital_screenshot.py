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
from occipital.take_screenshot_from_url_tool import execute_take_screenshot_from_url, analyze_screenshot_file


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


class TestTakeScreenshotFromURL:
    """Test the take_screenshot_from_url function."""
    
    @pytest.mark.asyncio
    async def test_successful_screenshot(self):
        """Test successful screenshot capture."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/test_screenshot.png"
            
            with patch('occipital.take_screenshot_from_url_tool.WebsiteTester') as mock_tester_class:
                mock_tester = Mock()
                mock_tester_class.return_value = mock_tester
                mock_tester.take_screenshot_from_url = AsyncMock()
                
                result = await execute_take_screenshot_from_url(
                    url="https://example.com",
                    session_id="test_session",
                    username="testuser"
                )
                
                assert result["success"] is True
                assert result["file_path"] == "/tmp/test_screenshot.png"
                assert result["session_id"] == "test_session"
                assert result["url"] == "https://example.com"
                assert "successfully" in result["message"]
                
                mock_get_path.assert_called_once_with("testuser", "test_session", ext="png")
                mock_tester_class.assert_called_once_with(username="testuser")
                mock_tester.take_screenshot_from_url.assert_called_once_with(
                    "https://example.com", "/tmp/test_screenshot.png"
                )
    
    @pytest.mark.asyncio
    async def test_screenshot_error_handling(self):
        """Test error handling during screenshot capture."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/test_screenshot.png"
            
            with patch('occipital.take_screenshot_from_url_tool.WebsiteTester') as mock_tester_class:
                mock_tester = Mock()
                mock_tester_class.return_value = mock_tester
                mock_tester.take_screenshot_from_url = AsyncMock(side_effect=Exception("Browser error"))
                
                result = await execute_take_screenshot_from_url(
                    url="https://example.com",
                    session_id="test_session",
                    username="testuser"
                )
                
                assert result["success"] is False
                assert result["error"] == "Browser error"
                assert result["session_id"] == "test_session"
                assert result["url"] == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_screenshot_with_default_username(self):
        """Test screenshot with default username."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/test_screenshot.png"
            
            with patch('occipital.take_screenshot_from_url_tool.WebsiteTester') as mock_tester_class:
                mock_tester = Mock()
                mock_tester_class.return_value = mock_tester
                mock_tester.take_screenshot_from_url = AsyncMock()
                
                result = await execute_take_screenshot_from_url(
                    url="https://example.com",
                    session_id="test_session"
                )
                
                assert result["success"] is True
                mock_get_path.assert_called_once_with("admin", "test_session", ext="png")
                mock_tester_class.assert_called_once_with(username="admin")


class TestAnalyzeScreenshotFile:
    """Test the analyze_screenshot_file function."""
    
    def test_successful_file_analysis(self):
        """Test successful file analysis."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/test_screenshot.png"
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=1024):
                    result = analyze_screenshot_file(
                        session_id="test_session",
                        original_prompt="Take a screenshot of example.com",
                        username="testuser"
                    )
                    
                    assert result["success"] is True
                    assert result["analysis"]["file_path"] == "/tmp/test_screenshot.png"
                    assert result["analysis"]["file_size_bytes"] == 1024
                    assert result["analysis"]["file_type"] == "PNG image"
                    assert result["analysis"]["session_id"] == "test_session"
                    assert "Image file captured" in result["analysis"]["analysis_summary"]
                    assert len(result["analysis"]["insights"]) > 0
                    assert len(result["analysis"]["recommendations"]) > 0
                    assert "Take a screenshot of example.com" in result["analysis"]["insights"][2]
                    
                    mock_get_path.assert_called_once_with("testuser", "test_session", ext="png")
    
    def test_file_not_found(self):
        """Test analysis when file doesn't exist."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/nonexistent.png"
            
            with patch('os.path.exists', return_value=False):
                result = analyze_screenshot_file(
                    session_id="test_session",
                    original_prompt="Take a screenshot",
                    username="testuser"
                )
                
                assert result["success"] is False
                assert "File not found" in result["error"]
                assert result["session_id"] == "test_session"
    
    def test_analysis_error_handling(self):
        """Test error handling during file analysis."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.side_effect = Exception("Path error")
            
            result = analyze_screenshot_file(
                session_id="test_session",
                original_prompt="Take a screenshot",
                username="testuser"
            )
            
            assert result["success"] is False
            assert result["error"] == "Path error"
            assert result["session_id"] == "test_session"
    
    def test_analysis_with_default_username(self):
        """Test analysis with default username."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/test_screenshot.png"
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=2048):
                    result = analyze_screenshot_file(
                        session_id="test_session",
                        original_prompt="Test prompt"
                    )
                    
                    assert result["success"] is True
                    assert result["analysis"]["file_size_bytes"] == 2048
                    mock_get_path.assert_called_once_with("admin", "test_session", ext="png")
    
    def test_analysis_with_empty_prompt(self):
        """Test analysis with empty original prompt."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/test_screenshot.png"
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=512):
                    result = analyze_screenshot_file(
                        session_id="test_session",
                        original_prompt="",
                        username="testuser"
                    )
                    
                    assert result["success"] is True
                    assert "Original prompt context: " in result["analysis"]["insights"][2]
    
    def test_analysis_with_none_prompt(self):
        """Test analysis with None original prompt."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/test_screenshot.png"
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=512):
                    result = analyze_screenshot_file(
                        session_id="test_session",
                        original_prompt=None,
                        username="testuser"
                    )
                    
                    assert result["success"] is True
                    assert "Original prompt context: None" in result["analysis"]["insights"][2]
    
    def test_analysis_with_large_file(self):
        """Test analysis with large file size."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/large_screenshot.png"
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=1048576):  # 1MB
                    result = analyze_screenshot_file(
                        session_id="test_session",
                        original_prompt="Large screenshot",
                        username="testuser"
                    )
                    
                    assert result["success"] is True
                    assert result["analysis"]["file_size_bytes"] == 1048576
                    assert "1048576 bytes" in result["analysis"]["analysis_summary"]
    
    def test_analysis_with_zero_size_file(self):
        """Test analysis with zero size file."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/empty_screenshot.png"
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=0):
                    result = analyze_screenshot_file(
                        session_id="test_session",
                        original_prompt="Empty screenshot",
                        username="testuser"
                    )
                    
                    assert result["success"] is True
                    assert result["analysis"]["file_size_bytes"] == 0
                    assert "0 bytes" in result["analysis"]["analysis_summary"]
    
    def test_analysis_insights_structure(self):
        """Test that analysis insights have the expected structure."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/test_screenshot.png"
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=1024):
                    result = analyze_screenshot_file(
                        session_id="test_session",
                        original_prompt="Test prompt",
                        username="testuser"
                    )
                    
                    insights = result["analysis"]["insights"]
                    assert len(insights) == 4
                    assert "webpage screenshot" in insights[0]
                    assert "PNG format" in insights[1]
                    assert "Original prompt context" in insights[2]
                    assert "computer vision APIs" in insights[3]
    
    def test_analysis_recommendations_structure(self):
        """Test that analysis recommendations have the expected structure."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/test_screenshot.png"
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=1024):
                    result = analyze_screenshot_file(
                        session_id="test_session",
                        original_prompt="Test prompt",
                        username="testuser"
                    )
                    
                    recommendations = result["analysis"]["recommendations"]
                    assert len(recommendations) == 3
                    assert "successfully captured" in recommendations[0]
                    assert "analyze the visual content" in recommendations[1]
                    assert "original prompt context" in recommendations[2]
    
    def test_analysis_with_special_characters_in_prompt(self):
        """Test analysis with special characters in the original prompt."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/test_screenshot.png"
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=1024):
                    special_prompt = "Take a screenshot of https://example.com?param=value&other=123"
                    result = analyze_screenshot_file(
                        session_id="test_session",
                        original_prompt=special_prompt,
                        username="testuser"
                    )
                    
                    assert result["success"] is True
                    assert special_prompt in result["analysis"]["insights"][2]
    
    def test_analysis_with_very_long_prompt(self):
        """Test analysis with very long original prompt."""
        with patch('occipital.take_screenshot_from_url_tool.get_user_image_path') as mock_get_path:
            mock_get_path.return_value = "/tmp/test_screenshot.png"
            
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=1024):
                    long_prompt = "A" * 1000  # Very long prompt
                    result = analyze_screenshot_file(
                        session_id="test_session",
                        original_prompt=long_prompt,
                        username="testuser"
                    )
                    
                    assert result["success"] is True
                    assert long_prompt in result["analysis"]["insights"][2]


if __name__ == "__main__":
    pytest.main([__file__]) 