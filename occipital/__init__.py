"""
Occipital module for visual processing and website testing.

This module provides comprehensive visual analysis and website testing capabilities
for Tatlock, including screenshot capture, visual regression testing, and layout analysis.
"""

from .website_tester import WebsiteTester
from .visual_analyzer import VisualAnalyzer

__all__ = ['WebsiteTester', 'VisualAnalyzer'] 