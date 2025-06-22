"""
Visual Analyzer Module

Provides visual analysis capabilities for screenshots and UI components.
Includes image comparison, visual regression detection, and layout analysis.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

try:
    from PIL import Image, ImageChops, ImageStat
    import numpy as np
except ImportError:
    print("PIL/Pillow not installed. Run: pip install Pillow")
    Image = None
    ImageChops = None
    ImageStat = None

logger = logging.getLogger(__name__)


class VisualAnalyzer:
    """
    Visual analysis tools for screenshot testing and comparison.
    
    Provides methods to compare screenshots, detect visual regressions,
    analyze layout changes, and generate visual analysis reports.
    """
    
    def __init__(self, username: str = "admin",
                 baseline_dir: str = None,
                 comparison_dir: str = None,
                 report_dir: str = None):
        """
        Initialize the visual analyzer.
        
        Args:
            username: Username for user-specific storage
            baseline_dir: Optional custom baseline directory
            comparison_dir: Optional custom comparison directory
            report_dir: Optional custom report directory
        """
        self.username = username
        
        # Create user-specific or custom directories
        self.user_base_dir = Path("hippocampus") / "shortterm" / username / "website_tester"
        self.baseline_dir = Path(baseline_dir) if baseline_dir else self.user_base_dir / "baselines"
        self.comparison_dir = Path(comparison_dir) if comparison_dir else self.user_base_dir / "comparisons"
        self.report_dir = Path(report_dir) if report_dir else self.user_base_dir / "reports"
        
        # Create directories
        for directory in [self.baseline_dir, self.comparison_dir, self.report_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def compare_screenshots(self, current_path: str, baseline_path: str, 
                          threshold: float = 0.95) -> Dict[str, any]:
        """
        Compare two screenshots and detect differences.
        
        Args:
            current_path: Path to current screenshot
            baseline_path: Path to baseline screenshot
            threshold: Similarity threshold (0-1)
            
        Returns:
            Dictionary with comparison results
        """
        if not Image:
            raise ImportError("PIL/Pillow not available")
        
        try:
            # Load images
            current_img = Image.open(current_path)
            baseline_img = Image.open(baseline_path)
            
            # Ensure same size
            if current_img.size != baseline_img.size:
                baseline_img = baseline_img.resize(current_img.size)
            
            # Convert to RGB if needed
            if current_img.mode != 'RGB':
                current_img = current_img.convert('RGB')
            if baseline_img.mode != 'RGB':
                baseline_img = baseline_img.convert('RGB')
            
            # Calculate difference
            diff = ImageChops.difference(current_img, baseline_img)
            
            # Calculate similarity metrics
            stat = ImageStat.Stat(diff)
            mean_diff = sum(stat.mean) / len(stat.mean)
            max_diff = max(stat.extrema[0])
            
            # Calculate similarity percentage
            similarity = 1 - (mean_diff / 255)
            
            # Determine if test passed
            passed = similarity >= threshold
            
            # Save difference image if significant differences found
            diff_path = None
            if not passed:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                diff_filename = f"diff_{Path(current_path).stem}_{timestamp}.png"
                diff_path = str(self.comparison_dir / diff_filename)
                diff.save(diff_path)
            
            return {
                'passed': passed,
                'similarity': similarity,
                'mean_diff': mean_diff,
                'max_diff': max_diff,
                'threshold': threshold,
                'diff_path': diff_path,
                'current_path': current_path,
                'baseline_path': baseline_path
            }
            
        except Exception as e:
            logger.error(f"Error comparing screenshots: {e}")
            return {
                'passed': False,
                'error': str(e),
                'current_path': current_path,
                'baseline_path': baseline_path
            }
    
    def analyze_layout_changes(self, current_path: str, baseline_path: str) -> Dict[str, any]:
        """
        Analyze layout changes between screenshots.
        
        Args:
            current_path: Path to current screenshot
            baseline_path: Path to baseline screenshot
            
        Returns:
            Dictionary with layout analysis results
        """
        if not Image:
            raise ImportError("PIL/Pillow not available")
        
        try:
            # Load images
            current_img = Image.open(current_path)
            baseline_img = Image.open(baseline_path)
            
            # Basic layout analysis
            layout_analysis = {
                'current_size': current_img.size,
                'baseline_size': baseline_img.size,
                'size_changed': current_img.size != baseline_img.size,
                'aspect_ratio_current': current_img.size[0] / current_img.size[1],
                'aspect_ratio_baseline': baseline_img.size[0] / baseline_img.size[1],
                'aspect_ratio_changed': False
            }
            
            # Check aspect ratio changes
            current_ratio = layout_analysis['aspect_ratio_current']
            baseline_ratio = layout_analysis['aspect_ratio_baseline']
            ratio_diff = abs(current_ratio - baseline_ratio)
            layout_analysis['aspect_ratio_changed'] = ratio_diff > 0.01
            layout_analysis['aspect_ratio_diff'] = ratio_diff
            
            return layout_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing layout: {e}")
            return {'error': str(e)}
    
    def find_baseline_screenshot(self, test_name: str, viewport: str = 'desktop') -> Optional[str]:
        """
        Find the baseline screenshot for a test.
        
        Args:
            test_name: Name of the test
            viewport: Viewport size
            
        Returns:
            Path to baseline screenshot if found
        """
        # Look for baseline files
        pattern = f"{test_name}_{viewport}_*.png"
        baseline_files = list(self.baseline_dir.glob(pattern))
        
        if baseline_files:
            # Return the most recent baseline
            return str(max(baseline_files, key=lambda f: f.stat().st_mtime))
        
        return None
    
    def update_baseline(self, screenshot_path: str, test_name: str, viewport: str = 'desktop'):
        """
        Update the baseline screenshot.
        
        Args:
            screenshot_path: Path to new screenshot
            test_name: Name of the test
            viewport: Viewport size
        """
        if not os.path.exists(screenshot_path):
            raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")
        
        # Generate baseline filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        baseline_filename = f"{test_name}_{viewport}_{timestamp}.png"
        baseline_path = self.baseline_dir / baseline_filename
        
        # Copy screenshot to baseline
        import shutil
        shutil.copy2(screenshot_path, baseline_path)
        
        logger.info(f"Updated baseline: {baseline_path}")
    
    def run_visual_regression_tests(self, screenshot_results: Dict[str, List[str]], 
                                  threshold: float = 0.95) -> Dict[str, Dict]:
        """
        Run visual regression tests on screenshot results.
        
        Args:
            screenshot_results: Results from WebsiteTester
            threshold: Similarity threshold for tests
            
        Returns:
            Dictionary with regression test results
        """
        regression_results = {}
        
        for test_name, screenshots in screenshot_results.items():
            test_results = {}
            
            for screenshot_path in screenshots:
                # Extract viewport from filename
                filename = Path(screenshot_path).name
                viewport = 'desktop'
                if '_tablet_' in filename:
                    viewport = 'tablet'
                elif '_mobile_' in filename:
                    viewport = 'mobile'
                
                # Find baseline
                baseline_path = self.find_baseline_screenshot(test_name, viewport)
                
                if baseline_path:
                    # Compare with baseline
                    comparison = self.compare_screenshots(screenshot_path, baseline_path, threshold)
                    comparison['viewport'] = viewport
                    test_results[f"{test_name}_{viewport}"] = comparison
                else:
                    # No baseline found, mark as new
                    test_results[f"{test_name}_{viewport}"] = {
                        'passed': True,
                        'new_baseline': True,
                        'screenshot_path': screenshot_path,
                        'viewport': viewport
                    }
            
            regression_results[test_name] = test_results
        
        return regression_results
    
    def generate_regression_report(self, regression_results: Dict[str, Dict]) -> str:
        """
        Generate a visual regression test report.
        
        Args:
            regression_results: Results from run_visual_regression_tests
            
        Returns:
            Path to generated HTML report
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Count results
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        new_baselines = 0
        
        for test_results in regression_results.values():
            for result in test_results.values():
                total_tests += 1
                if result.get('new_baseline'):
                    new_baselines += 1
                elif result.get('passed'):
                    passed_tests += 1
                else:
                    failed_tests += 1
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tatlock Visual Regression Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .summary-item {{ 
                    background: #fff; 
                    padding: 15px; 
                    border-radius: 8px; 
                    border: 1px solid #ddd;
                    text-align: center;
                }}
                .passed {{ color: #28a745; }}
                .failed {{ color: #dc3545; }}
                .new {{ color: #17a2b8; }}
                .test-section {{ margin: 20px 0; border: 1px solid #ddd; border-radius: 8px; }}
                .test-header {{ background: #f8f9fa; padding: 15px; border-bottom: 1px solid #ddd; }}
                .test-result {{ padding: 15px; }}
                .screenshot-comparison {{ display: flex; gap: 20px; margin: 10px 0; }}
                .screenshot {{ flex: 1; }}
                .screenshot img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Tatlock Visual Regression Test Report</h1>
                <p>Generated: {timestamp}</p>
            </div>
            
            <div class="summary">
                <div class="summary-item">
                    <h3>Total Tests</h3>
                    <p style="font-size: 24px; font-weight: bold;">{total_tests}</p>
                </div>
                <div class="summary-item">
                    <h3 class="passed">Passed</h3>
                    <p style="font-size: 24px; font-weight: bold; color: #28a745;">{passed_tests}</p>
                </div>
                <div class="summary-item">
                    <h3 class="failed">Failed</h3>
                    <p style="font-size: 24px; font-weight: bold; color: #dc3545;">{failed_tests}</p>
                </div>
                <div class="summary-item">
                    <h3 class="new">New Baselines</h3>
                    <p style="font-size: 24px; font-weight: bold; color: #17a2b8;">{new_baselines}</p>
                </div>
            </div>
        """
        
        for test_name, test_results in regression_results.items():
            html += f"""
            <div class="test-section">
                <div class="test-header">
                    <h2>{test_name.replace('_', ' ').title()}</h2>
                </div>
            """
            
            for result_name, result in test_results.items():
                status_class = 'passed' if result.get('passed') else 'failed'
                status_text = 'PASSED' if result.get('passed') else 'FAILED'
                
                if result.get('new_baseline'):
                    status_class = 'new'
                    status_text = 'NEW BASELINE'
                
                html += f"""
                <div class="test-result">
                    <h3 class="{status_class}">{result_name.replace('_', ' ').title()} - {status_text}</h3>
                """
                
                if result.get('new_baseline'):
                    html += f"""
                    <p>New baseline created: {result['screenshot_path']}</p>
                    """
                elif result.get('passed'):
                    html += f"""
                    <p>Similarity: {result.get('similarity', 0):.2%}</p>
                    <p>Mean difference: {result.get('mean_diff', 0):.2f}</p>
                    """
                else:
                    html += f"""
                    <p>Similarity: {result.get('similarity', 0):.2%} (threshold: {result.get('threshold', 0):.2%})</p>
                    <p>Mean difference: {result.get('mean_diff', 0):.2f}</p>
                    <p>Max difference: {result.get('max_diff', 0)}</p>
                    """
                    
                    if result.get('diff_path'):
                        html += f"""
                        <div class="screenshot-comparison">
                            <div class="screenshot">
                                <h4>Current</h4>
                                <img src="{result['current_path']}" alt="Current">
                            </div>
                            <div class="screenshot">
                                <h4>Baseline</h4>
                                <img src="{result['baseline_path']}" alt="Baseline">
                            </div>
                            <div class="screenshot">
                                <h4>Difference</h4>
                                <img src="{result['diff_path']}" alt="Difference">
                            </div>
                        </div>
                        """
                
                html += "</div>"
            
            html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        # Save report
        report_path = self.comparison_dir / f"regression_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_path, 'w') as f:
            f.write(html)
        
        logger.info(f"Generated regression report: {report_path}")
        return str(report_path)


def main():
    """Main function for running visual analysis."""
    analyzer = VisualAnalyzer()
    
    print("Visual Analyzer initialized")
    print(f"Baseline directory: {analyzer.baseline_dir}")
    print(f"Comparison directory: {analyzer.comparison_dir}")


if __name__ == "__main__":
    main() 