# Parietal

**Status: Production Ready - Hardware Monitoring & Performance Analysis**

The Parietal module provides hardware monitoring, system information, and performance benchmarking capabilities for Tatlock. Named after the brain's parietal lobe responsible for spatial awareness and sensory integration, this module serves as the system's "sensory cortex" for monitoring hardware resources and analyzing performance.

## Core Features

- **Hardware Monitoring**: CPU, memory, disk, network, and system information
- **Performance Benchmarking**: LLM and tool performance testing
- **Hardware Classification**: Automatic LLM model selection based on system capabilities
- **Real-time Metrics**: Live system monitoring with charts and alerts
- **Debug Console Integration**: Visual system information and performance data

## API Endpoints

- `GET /parietal/system-info` - Get comprehensive system information
- `GET /parietal/hardware/classification` - Get hardware classification and recommended model
- `POST /parietal/benchmark` - Run comprehensive benchmark
- `POST /parietal/benchmark/llm` - Run LLM-specific benchmark
- `POST /parietal/benchmark/tools` - Run tool-specific benchmark

## Integration

- **Cortex**: Provide system performance context for decision making
- **Config**: Automatic model selection based on hardware classification
- **Installer**: Hardware-dependent model downloads during installation
- **Stem**: Access system information and performance data
- **Debug Console**: Real-time monitoring and analysis interface

## Hardware Classification

The `classify_hardware_performance()` function provides automatic LLM model selection:

### Performance Tiers

- **High Performance**: 8GB+ RAM, 4+ CPU cores, non-Apple Silicon → `gemma3-cortex:latest`
- **Medium Performance**: 4-8GB RAM, 2-4 CPU cores, or Apple Silicon → `mistral:7b`
- **Low Performance**: <4GB RAM or limited CPU → `gemma2:2b`

### Key Features

- **Apple Silicon Optimization**: M1/M2 systems automatically use Mistral for compatibility
- **Tool Calling Focus**: All selected models support function calling for agent capabilities
- **Fallback Safety**: Robust error handling with safe defaults
- **Installation Integration**: Installer automatically downloads optimal model

## Standards & Patterns

All coding and performance standards are defined in [AGENTS.md](../AGENTS.md). Refer to it for:

- Logging and error handling
- Database operations
- Security considerations

## See Also

- [Developer Guide](../AGENTS.md) – All standards and patterns
- [Module Docs](../README.md)
