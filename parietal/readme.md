# parietal

**Status: Active Development - Hardware Monitoring & Performance Analysis**

The parietal module provides hardware monitoring, system information, and performance benchmarking capabilities for Tatlock. It serves as the system's "sensory cortex" for monitoring hardware resources and analyzing performance.

## Current Implementation

### Hardware Monitoring (`hardware.py`)
The parietal module provides comprehensive system and hardware information monitoring:

#### System Information
- **Operating System**: Detailed OS information (Linux/macOS)
- **CPU Information**: Cores, frequency, usage statistics, load averages
- **Memory Status**: RAM and swap memory usage, availability
- **Disk Space**: Partition information, usage statistics
- **Network Statistics**: Bytes sent/received, connection information
- **System Uptime**: Process count, system health status

#### Performance Benchmarking
- **LLM Benchmark**: Test response times for simple responses, complex reasoning, and tool calling
- **Tools Benchmark**: Test performance of various tools (personal variables, memory recall, weather, web search)
- **Comprehensive Benchmark**: Combined analysis with system resource correlation
- **Performance Grading**: Automatic performance assessment (Excellent/Good/Fair/Poor)
- **Bottleneck Identification**: Identify performance bottlenecks and provide recommendations

### API Endpoints

#### System Information
- `GET /parietal/system-info` - Get comprehensive system and hardware information
  - Returns CPU, memory, disk, network, and process information
  - Includes real-time usage statistics and system health data

#### Performance Benchmarking
- `POST /parietal/benchmark` - Run comprehensive benchmark (LLM + Tools + System Analysis)
- `POST /parietal/benchmark/llm` - Run LLM-specific benchmark tests
- `POST /parietal/benchmark/tools` - Run tool-specific benchmark tests

### Debug Console Integration
The parietal module is fully integrated into the debug console with:

#### System Info Section
- **Real-time Metrics Tiles**: CPU, RAM, disk, uptime, and network usage
- **Live-updating Charts**: CPU and RAM usage graphs with time-series data
- **System Health Monitoring**: Automatic health checks and warnings
- **Raw System Data**: Complete system information in JSON format

#### Benchmark Section
- **Comprehensive Benchmark**: Full system performance analysis
- **LLM Benchmark**: Test AI model response times and capabilities
- **Tools Benchmark**: Test tool execution performance
- **Performance Analysis**: Automatic grading and recommendations
- **Bottleneck Detection**: Identify performance issues and solutions

### Features

#### Real-time Monitoring
- **10-second polling** for system metrics
- **Live-updating charts** with 60-point history
- **Automatic health checks** with warnings and recommendations
- **Cross-platform support** (Linux and macOS)

#### Performance Analysis
- **Response time measurement** for LLM interactions
- **Tool execution timing** for all available tools
- **System resource correlation** with performance
- **Actionable recommendations** for optimization

#### Data Visualization
- **Interactive charts** using Chart.js
- **Color-coded performance grades**
- **Time-series data** for trend analysis
- **Responsive design** for all screen sizes

## Technical Implementation

### Hardware Monitoring
```python
from parietal.hardware import get_comprehensive_system_info

# Get complete system information
system_info = get_comprehensive_system_info()
```

### Benchmarking
```python
from parietal.hardware import run_comprehensive_benchmark

# Run full performance analysis
results = run_comprehensive_benchmark()
```

### API Usage
```bash
# Get system information
curl -X GET http://localhost:8000/parietal/system-info

# Run comprehensive benchmark
curl -X POST http://localhost:8000/parietal/benchmark
```

## Integration Points

- **cortex**: Provide system performance context for decision making
- **stem**: Access system information and performance data
- **debug console**: Real-time monitoring and analysis interface
- **admin interface**: System health and performance monitoring

## Data Models

### System Information
- **CPU Data**: Usage percentages, core information, frequency data
- **Memory Data**: RAM and swap usage, availability statistics
- **Disk Data**: Partition information, usage percentages
- **Network Data**: Bytes transferred, connection statistics
- **Process Data**: Total process count, system load

### Benchmark Results
- **LLM Performance**: Response times, model information, test results
- **Tool Performance**: Execution times, success rates, error information
- **System Analysis**: Overall performance grade, bottlenecks, recommendations
- **Historical Data**: Time-series performance tracking

## Future Development

### Planned Spatial Features
The parietal module will expand to include spatial reasoning and environmental monitoring:

#### Spatial Reasoning
- **Spatial Awareness**: Understand spatial relationships and directions
- **Navigation Support**: Help with location-based queries and directions
- **Spatial Problem Solving**: Assist with spatial reasoning tasks
- **Geographic Context**: Understand geographic and location-based information

#### Sensory Integration
- **Multi-Modal Processing**: Integrate information from multiple senses
- **Context Awareness**: Understand environmental and situational context
- **Sensory Memory**: Process and store sensory information
- **Environmental Monitoring**: Track and respond to environmental changes

#### Environmental Monitoring
- **Home Sensors**: Process temperature, light, and other sensor data
- **Weather Integration**: Combine weather data with spatial context
- **Environmental Context**: Understand the agent's physical environment
- **Location Services**: Provide location-aware services and information

### Development Roadmap
1. **Current**: Hardware monitoring and performance analysis ✅
2. **Phase 1**: Location services and basic spatial awareness
3. **Phase 2**: Advanced spatial reasoning and environmental integration
4. **Phase 3**: Predictive analysis and adaptive responses

## Use Cases

### Current Use Cases
- **System Monitoring**: Real-time hardware resource monitoring
- **Performance Analysis**: Benchmark LLM and tool performance
- **Debug Console**: Visual system information and performance data
- **Health Monitoring**: Automatic system health checks and alerts

### Future Use Cases
- **Location-based Services**: Provide location-aware information and assistance
- **Navigation Support**: Help with directions and route planning
- **Environmental Monitoring**: Monitor and respond to environmental changes
- **Spatial Problem Solving**: Assist with spatial reasoning and planning tasks
- **Context-aware Responses**: Provide responses based on environmental context

## Privacy and Security

### Current Implementation
- **System Data Only**: No personal or sensitive data collection
- **Local Processing**: All monitoring and analysis done locally
- **No External Transmission**: System data stays within the application

### Future Considerations
- **Location Privacy**: Secure handling of location information
- **Sensor Data Protection**: Protect sensitive environmental data
- **User Consent**: Clear consent for location and environmental tracking
- **Data Minimization**: Collect only necessary spatial and environmental data
- **Anonymization**: Protect user privacy in spatial and environmental data
