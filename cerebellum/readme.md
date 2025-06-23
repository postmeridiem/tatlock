# Cerebellum

**Status: Production Ready - External API Tools Implemented**

The Cerebellum module provides external API integration and procedural tools for Tatlock. Named after the brain's cerebellum responsible for coordination and procedural memory, this module handles web search, weather forecasting, and will support future procedural automation features.

## Core Features
- **Web Search Tool**: Google Custom Search API integration
- **Weather Tool**: OpenWeather API integration for forecasts
- **Error Handling**: Graceful handling of API failures
- **Rate Limiting**: Respectful API usage with configurable limits

## Configuration
Required environment variables:
- `GOOGLE_API_KEY` and `GOOGLE_CSE_ID` for web search
- `OPENWEATHER_API_KEY` for weather data

## Integration
- **Cortex**: Execute external API calls through tools
- **Stem**: Tool registration and dispatch
- **Hippocampus**: Store procedural patterns (future)

## Standards & Patterns
All coding and tool standards are defined in [developer.md](../developer.md). Refer to it for:
- Tool implementation patterns
- Error handling and logging
- API key management
- Security considerations

## See Also
- [Developer Guide](../developer.md) – All standards and patterns
- [Module Docs](../README.md)
