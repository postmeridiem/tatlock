# Occipital

**Status: Production Ready - Visual Processing & Screenshot Testing**

The Occipital module provides comprehensive visual processing and screenshot testing capabilities for Tatlock. Named after the brain's occipital lobe responsible for visual processing, this module enables automated UI testing, visual regression detection, and visual content analysis.

## Core Features
- **Screenshot Testing**: Automated screenshot capture using Playwright
- **Visual Regression Detection**: Compare screenshots against baselines
- **Multi-Viewport Testing**: Desktop, tablet, and mobile viewport testing
- **Tool Integration**: Screenshot capture and file analysis tools for the AI agent
- **URL Screenshot Service**: Take screenshots from any URL

## Architecture
- **WebsiteTester**: Automated screenshot capture and testing
- **VisualAnalyzer**: Image comparison and regression detection
- **URL Screenshot Service**: Webpage capture for LLM tools

## Integration
- **Cortex**: Provide visual processing tools for the agent
- **Hippocampus**: Store screenshots in user short-term storage
- **Stem**: Tool registration and user authentication

## Standards & Patterns
All coding and tool standards are defined in [developer.md](../developer.md). Refer to it for:
- Tool implementation patterns
- Error handling and logging
- User context management
- Security considerations

## See Also
- [Developer Guide](../developer.md) – All standards and patterns
- [Module Docs](../README.md)