# Parietal

**Status: Production Ready - Hardware Monitoring & Performance Analysis**

The Parietal module provides hardware monitoring, system information, and performance benchmarking capabilities for Tatlock. Named after the brain's parietal lobe responsible for spatial awareness and sensory integration, this module serves as the system's "sensory cortex" for monitoring hardware resources and analyzing performance.

## Core Features

- **Hardware Monitoring**: CPU, memory, disk, network, and system information
- **Performance Benchmarking**: LLM and tool performance testing
- **Real-time Metrics**: Live system monitoring with charts and alerts
- **Debug Console Integration**: Visual system information and performance data

## API Endpoints

- `GET /parietal/system-info` - Get comprehensive system information
- `POST /parietal/benchmark` - Run comprehensive benchmark
- `POST /parietal/benchmark/llm` - Run LLM-specific benchmark
- `POST /parietal/benchmark/tools` - Run tool-specific benchmark

## Integration

- **Cortex**: Provide system performance context for decision making
- **Stem**: Access system information and performance data
- **Debug Console**: Real-time monitoring and analysis interface

## Standards & Patterns

All coding and performance standards are defined in [AGENTS.md](../AGENTS.md). Refer to it for:

- Logging and error handling
- Database operations
- Security considerations

## See Also

- [Developer Guide](../AGENTS.md) – All standards and patterns
- [Module Docs](../README.md)
