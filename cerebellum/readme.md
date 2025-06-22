# Cerebellum

**Status: Production Ready - External API Tools Implemented**

The Cerebellum module provides external API integration and procedural tools for Tatlock. Named after the brain's cerebellum responsible for coordination and procedural memory, this module handles web search, weather forecasting, and will support future procedural automation features.

## ✅ **Current Features**

### 🔍 **Web Search Tool**
- **Google Custom Search**: Integration with Google Custom Search JSON API
- **Query Processing**: Intelligent search query handling and formatting
- **Result Formatting**: Clean, structured search results with titles, links, and snippets
- **Error Handling**: Graceful handling of API failures and configuration issues
- **Rate Limiting**: Respectful API usage with configurable result limits

### 🌤️ **Weather Tool**
- **OpenWeather Integration**: Real-time weather data from OpenWeather API
- **Multi-City Support**: Weather forecasts for any city worldwide
- **Date Range Queries**: Flexible date range support for historical and future forecasts
- **Temperature Units**: Metric temperature units (Celsius) with configurable options
- **Comprehensive Data**: Temperature ranges, descriptions, and weather conditions

## 🛠️ **Implementation Details**

### **Web Search Tool** (`web_search_tool.py`)
```python
from cerebellum.web_search_tool import execute_web_search

# Perform a web search
result = execute_web_search("Python programming best practices")
```

**Features:**
- **API Key Validation**: Checks for required Google API keys
- **Error Recovery**: Handles network failures and API errors
- **Result Limiting**: Configurable number of results (default: 5)
- **Structured Output**: Consistent response format with status and data

### **Weather Tool** (`weather_tool.py`)
```python
from cerebellum.weather_tool import execute_get_weather_forecast

# Get weather forecast
result = execute_get_weather_forecast("Rotterdam", "2024-01-15", "2024-01-20")
```

**Features:**
- **Geocoding**: Automatic city name to coordinates conversion
- **Date Processing**: Flexible date range support with defaults
- **Data Aggregation**: Daily temperature ranges and weather descriptions
- **Error Handling**: Comprehensive error handling for API failures

## 🔧 **Configuration**

### **Required Environment Variables**
```bash
# Google Custom Search API
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id

# OpenWeather API
OPENWEATHER_API_KEY=your_openweather_api_key
```

### **API Setup Instructions**

#### **Google Custom Search**
1. **Create Google Cloud Project**: Visit [Google Cloud Console](https://console.cloud.google.com/)
2. **Enable Custom Search API**: Enable the Custom Search JSON API
3. **Create API Key**: Generate an API key in the Credentials section
4. **Create Custom Search Engine**: Visit [Programmable Search Engine](https://programmablesearchengine.google.com/)
5. **Configure Search Engine**: Set up search engine and get the Search Engine ID

#### **OpenWeather API**
1. **Create Account**: Sign up at [OpenWeather](https://openweathermap.org/api)
2. **Generate API Key**: Create a free API key in your account
3. **Configure Units**: API returns metric units by default

## 📊 **Tool Integration**

### **LLM Tool Registration**
Both tools are registered in `stem/tools.py` and available to the AI agent:

```python
# Tool definitions for LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Perform a web search using Google Custom Search API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to send to the search engine."
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "Get the weather forecast for a specific city and date range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name."},
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD). Optional."},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD). Optional."}
                },
                "required": ["city"],
            },
        },
    }
]
```

### **Error Handling**
Both tools follow the standardized error handling pattern:

```python
# Success response
{"status": "success", "data": results}

# Error response
{"status": "error", "message": "Error description"}
```

## 🔮 **Future Development**

### **Planned Features**
- **Procedural Memory**: Learn and execute repetitive tasks
- **Task Automation**: Handle scheduled and recurring activities
- **Skill Acquisition**: Develop and refine procedural skills
- **Behavioral Patterns**: Learn and replicate successful interaction patterns

### **Background Processing**
- **Async Tasks**: Handle long-running operations
- **Scheduled Jobs**: Manage time-based activities
- **Process Monitoring**: Track and manage ongoing operations
- **Task Queuing**: Manage task priorities and execution order

### **Learning and Adaptation**
- **Behavior Patterns**: Learn from repeated interactions
- **Efficiency Optimization**: Improve task execution over time
- **Error Recovery**: Handle and learn from procedural failures
- **Performance Tracking**: Monitor and optimize task performance

## 🔗 **Integration Points**

- **Cortex**: Execute learned procedures and routines
- **Hippocampus**: Store procedural memories and patterns
- **Temporal**: Process temporal aspects of routines
- **Thalamus**: Coordinate with other brain regions
- **Stem**: Access system tools and utilities

## 🧪 **Testing**

### **Unit Tests**
```bash
# Run cerebellum-specific tests
python -m pytest tests/test_cerebellum_tools.py -v
```

### **Integration Tests**
```bash
# Test tool integration with agent
python -c "from stem.tools import execute_web_search, execute_get_weather_forecast; print('Tools imported successfully')"
```

## 📈 **Performance Considerations**

- **API Rate Limiting**: Respectful API usage to avoid rate limits
- **Caching**: Consider implementing result caching for frequently requested data
- **Error Recovery**: Graceful degradation when external APIs are unavailable
- **Connection Pooling**: Efficient HTTP connection management

## 🔒 **Security Considerations**

- **API Key Management**: Secure storage and rotation of API keys
- **Input Validation**: Validate all user inputs before API calls
- **Error Information**: Avoid exposing sensitive information in error messages
- **Rate Limiting**: Implement client-side rate limiting to prevent abuse

## 📚 **Related Documentation**

- **[README.md](../README.md)** - General overview and installation
- **[developer.md](../developer.md)** - Developer guide and practices
- **[moreinfo.md](../moreinfo.md)** - In-depth technical information
- **[cortex/readme.md](../cortex/readme.md)** - Core agent logic documentation
- **[hippocampus/readme.md](../hippocampus/readme.md)** - Memory system documentation
- **[stem/readme.md](../stem/readme.md)** - Core utilities and infrastructure
- **[parietal/readme.md](../parietal/readme.md)** - Hardware monitoring and performance
