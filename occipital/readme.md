# Occipital

**Status: Production Ready - Visual Processing & Screenshot Testing**

The Occipital module provides comprehensive visual processing and screenshot testing capabilities for Tatlock. Named after the brain's occipital lobe responsible for visual processing, this module enables automated UI testing, visual regression detection, and visual content analysis.

## ✅ **Core Features**

### 🖼️ **Screenshot Testing System**
- **Headless Browser Testing**: Automated screenshot capture using Playwright
- **Multi-Viewport Testing**: Desktop (1920x1080), tablet (768x1024), and mobile (375x667) viewport testing
- **Visual Regression Detection**: Compare screenshots against baselines with configurable thresholds
- **Component Testing**: Test specific UI components and layouts
- **Navigation Layout Testing**: Verify navigation docking behavior and responsive design
- **HTML Reports**: Generate comprehensive test reports with visual comparisons

### 🔍 **Visual Analysis**
- **Image Comparison**: Pixel-perfect screenshot comparison with difference detection
- **Layout Analysis**: Detect layout changes, aspect ratio differences, and size variations
- **Baseline Management**: Automatic baseline creation, updates, and versioning
- **Difference Detection**: Generate difference images for failed tests with highlighting
- **Similarity Metrics**: Calculate similarity percentages and difference statistics

### 🛠️ **Tool Integration**
- **LLM Tools**: Screenshot capture and file analysis tools for the AI agent
- **API Endpoints**: RESTful endpoints for screenshot capture and file retrieval
- **User Storage**: Per-user temporary storage for screenshots and analysis results
- **Session Management**: Secure session-based access to user files

### 📸 **URL Screenshot Service**
- **Webpage Capture**: Take full-page screenshots from any URL
- **User Storage Integration**: Save screenshots to user-specific short-term storage
- **File Analysis**: Basic image analysis and metadata extraction
- **Session Management**: Track screenshots by session ID for context

## 🏗️ **Architecture**

### **Core Components**

#### **WebsiteTester** (`website_tester.py`)
```python
from occipital.website_tester import WebsiteTester

# Initialize tester
tester = WebsiteTester(base_url="http://localhost:8000")

# Run full test suite
results = await tester.run_full_test_suite()

# Test specific page
screenshot = await tester.capture_page_screenshot("/admin", "admin_page", "desktop")

# Test navigation layout
nav_results = await tester.test_navigation_layout()

# Take screenshot from URL (for LLM tools)
screenshot_path = await tester.take_screenshot_from_url("https://example.com", "output.png")
```

#### **VisualAnalyzer** (`visual_analyzer.py`)
```python
from occipital.visual_analyzer import VisualAnalyzer

# Initialize analyzer
analyzer = VisualAnalyzer()

# Compare screenshots
comparison = analyzer.compare_screenshots("current.png", "baseline.png", threshold=0.95)

# Run regression tests
regression_results = analyzer.run_visual_regression_tests(screenshot_results)

# Generate reports
report_path = analyzer.generate_regression_report(regression_results)

# Analyze layout changes
layout_analysis = analyzer.analyze_layout_changes("current.png", "baseline.png")
```

#### **URL Screenshot Service** (`take_screenshot_from_url_tool.py`)
```python
from occipital.take_screenshot_from_url_tool import execute_take_screenshot_from_url, analyze_screenshot_file

# Take screenshot from URL
result = await execute_take_screenshot_from_url(
    url="https://example.com",
    session_id="user_request_123",
    username="jeroen"
)

# Analyze screenshot file
analysis = analyze_screenshot_file(
    session_id="user_request_123",
    original_prompt="Show me the homepage",
    username="jeroen"
)
```

#### **ScreenshotTestRunner** (`run_tests.py`)
```python
from occipital.run_tests import ScreenshotTestRunner

# Initialize runner
runner = ScreenshotTestRunner()

# Run complete test suite
results = await runner.run_complete_test_suite(update_baselines=True)

# Test specific page
page_results = await runner.test_specific_page("/admin", "admin_page", ["desktop", "tablet"])

# Test navigation docking
nav_results = await runner.test_navigation_docking()
```

## 🚀 **Usage**

### **Command Line Interface**

#### **Run Complete Test Suite**
```bash
# Run all tests
python -m occipital.run_tests

# Update baselines
python -m occipital.run_tests --update-baselines

# Test specific page
python -m occipital.run_tests --test-page /admin --page-name admin_page

# Test only navigation layout
python -m occipital.run_tests --navigation-only

# Use different server URL
python -m occipital.run_tests --url http://localhost:9000
```

#### **Programmatic Usage**
```python
import asyncio
from occipital.run_tests import ScreenshotTestRunner

async def main():
    runner = ScreenshotTestRunner()
    
    # Run complete test suite
    results = await runner.run_complete_test_suite()
    
    # Check results
    summary = results['summary']
    print(f"Success rate: {summary['success_rate']:.1f}%")
    
    if summary['failed_regression_tests'] > 0:
        print(f"⚠️  {summary['failed_regression_tests']} tests failed!")
    else:
        print("✅ All tests passed!")

asyncio.run(main())
```

### **LLM Tool Integration**

The Occipital module provides tools for the AI agent to capture and analyze visual content:

#### **Screenshot Tool**
```python
# Tool: screenshot_from_url
# Captures a screenshot from any URL and saves it to user's short-term storage
{
    "name": "screenshot_from_url",
    "description": "Take a screenshot of a webpage and save it to the user's short-term storage",
    "parameters": {
        "url": "The URL to capture",
        "session_id": "Unique session identifier",
        "username": "Username for storage location"
    }
}
```

#### **File Analysis Tool**
```python
# Tool: analyze_file
# Analyzes files in user's short-term storage, including image interpretation
{
    "name": "analyze_file",
    "description": "Analyze a file stored in the user's short-term storage",
    "parameters": {
        "filename": "Name of the file to analyze",
        "username": "Username for storage location"
    }
}
```

## 🌐 **API Endpoints**

### **Screenshot Capture**
```http
POST /hippocampus/shortterm/screenshot
Content-Type: application/json

{
    "url": "https://example.com",
    "session_id": "user_request_123"
}
```

### **File Retrieval**
```http
GET /hippocampus/shortterm/files/get?session_id=user_request_123
Authorization: Bearer <session_token>
```

## 📁 **Directory Structure**

### **User-Specific Storage**
```
hippocampus/shortterm/{username}/website_tester/
├── screenshots/          # Current test screenshots
├── baselines/           # Baseline images for comparison
├── comparisons/         # Difference images and reports
└── reports/            # Test reports and analysis
```

### **Test Organization**
- **Screenshots**: Current test results organized by page and viewport
- **Baselines**: Reference images for regression testing
- **Comparisons**: Visual difference analysis and reports
- **Reports**: HTML test reports with visual comparisons

## 🧪 **Testing**

### **Unit Tests**
```bash
# Run occipital-specific tests
python -m pytest tests/test_occipital_screenshot.py -v
```

### **Integration Tests**
```bash
# Test screenshot functionality
python -c "from occipital.take_screenshot_from_url_tool import execute_take_screenshot_from_url; print('Screenshot service imported successfully')"
```

## 📈 **Performance Considerations**

- **Parallel Testing**: Concurrent screenshot capture for multiple viewports
- **Image Optimization**: Efficient image processing and comparison algorithms
- **Storage Management**: Automatic cleanup of old test artifacts
- **Memory Usage**: Optimized image handling to prevent memory bloat

## 🔒 **Security Considerations**

- **URL Validation**: Validate URLs before screenshot capture
- **File Access Control**: Secure access to user-specific files
- **Session Management**: Proper session-based authentication
- **Input Sanitization**: Validate all input parameters

## ⚠️ **Error Handling**

- **Browser Failures**: Graceful handling of Playwright browser issues
- **Network Errors**: Retry logic for network connectivity problems
- **File System Errors**: Proper error handling for file operations
- **Memory Issues**: Handle large screenshot files efficiently

## 🔮 **Future Enhancements**

### **Planned Features**
- **Video Recording**: Capture video recordings of UI interactions
- **Accessibility Testing**: Automated accessibility compliance testing
- **Performance Testing**: Visual performance metrics and analysis
- **Cross-Browser Testing**: Support for multiple browser engines
- **Mobile Device Testing**: Real mobile device testing capabilities

### **Advanced Analysis**
- **OCR Integration**: Text extraction from screenshots
- **Object Detection**: Automated UI element detection and validation
- **Color Analysis**: Color scheme and contrast analysis
- **Layout Validation**: Automated layout consistency checking

## 📚 **Related Documentation**

- **[README.md](../README.md)** - General overview and installation
- **[developer.md](../developer.md)** - Developer guide and practices
- **[moreinfo.md](../moreinfo.md)** - In-depth technical information
- **[cortex/readme.md](../cortex/readme.md)** - Core agent logic documentation
- **[hippocampus/readme.md](../hippocampus/readme.md)** - Memory system documentation
- **[stem/readme.md](../stem/readme.md)** - Core utilities and infrastructure