# In-Depth Technical Information

This document contains detailed technical information about Tatlock's architecture, implementation details, and advanced features.

## Current Implementation Status

### Fully Implemented Modules
- **cortex**: Core agent logic with tool dispatch and agentic loop
- **hippocampus**: Complete memory system with user-specific databases
- **stem**: Authentication, admin dashboard, tools, and utilities
- **parietal**: Hardware monitoring and performance analysis

### Planned Modules (Future Development)
- **amygdala**: Emotional processing and mood awareness
- **cerebellum**: Procedural memory and task automation
- **occipital**: Visual processing and image analysis
- **temporal**: Language processing and temporal context
- **thalamus**: Information routing and coordination

## Brain-Inspired Architecture

### Module Organization

Tatlock's architecture is inspired by the human brain, with each module representing a specific brain region:

#### **Cortex** - Executive Functions
- **Location**: `cortex/`
- **Purpose**: Core decision-making and reasoning
- **Key Components**:
  - Agentic loop with tool calling
  - LLM integration and response generation
  - Topic classification and conversation management
  - Tool dispatch and execution coordination

#### **Hippocampus** - Memory System
- **Location**: `hippocampus/`
- **Purpose**: Long-term memory storage and retrieval
- **Key Components**:
  - Per-user isolated databases
  - Conversation memory and topic tracking
  - Natural language date parsing
  - Memory recall and search functionality

#### **Stem** - Core Infrastructure
- **Location**: `stem/`
- **Purpose**: Authentication, utilities, and core services
- **Key Components**:
  - Session-based authentication system
  - Admin dashboard and user management
  - Tool definitions and implementations
  - Static file serving and web interface

#### **Parietal** - Sensory Processing
- **Location**: `parietal/`
- **Purpose**: Hardware monitoring and performance analysis
- **Key Components**:
  - Real-time system monitoring
  - Performance benchmarking
  - Hardware resource tracking
  - Debug console integration

### Planned Brain Regions

#### **Amygdala** - Emotional Processing
- **Status**: Planned
- **Purpose**: Mood awareness and emotional context
- **Planned Features**:
  - Sentiment analysis
  - Mood tracking and response modulation
  - Emotional memory and patterns

#### **Cerebellum** - Procedural Memory
- **Status**: Planned
- **Purpose**: Task automation and learned behaviors
- **Planned Features**:
  - Routine management
  - Background processing
  - Skill acquisition and optimization

#### **Occipital** - Visual Processing
- **Status**: Planned
- **Purpose**: Image analysis and visual understanding
- **Planned Features**:
  - Computer vision integration
  - Image generation and analysis
  - Visual context understanding

#### **Temporal** - Language Processing
- **Status**: Planned
- **Purpose**: Language understanding and temporal context
- **Planned Features**:
  - Natural language processing
  - Speech recognition and synthesis
  - Temporal reasoning

#### **Thalamus** - Information Routing
- **Status**: Planned
- **Purpose**: Coordination and information flow
- **Planned Features**:
  - Message routing between modules
  - Load balancing and resource management
  - Inter-module communication

## Technical Implementation Details

### Database Architecture

#### User Isolation System
- **Per-User Databases**: Each user has their own `{username}_longterm.db`
- **Shared System Database**: `system.db` for authentication and user management
- **Complete Privacy**: No cross-user data access possible
- **On-Demand Creation**: User databases created on first use

#### Database Schema

**User Database (`{username}_longterm.db`)**:
```sql
-- Memories table
CREATE TABLE memories (
    id INTEGER PRIMARY KEY,
    user_prompt TEXT,
    llm_reply TEXT,
    full_llm_history TEXT,
    topic TEXT,
    timestamp DATETIME,
    conversation_id TEXT
);

-- Topics table
CREATE TABLE topics (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    created_at DATETIME
);

-- Memory-Topic relationships
CREATE TABLE memory_topics (
    memory_id INTEGER,
    topic_id INTEGER,
    FOREIGN KEY (memory_id) REFERENCES memories(id),
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

-- Conversations table
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    title TEXT,
    start_time DATETIME,
    last_activity DATETIME,
    message_count INTEGER
);

-- System prompts
CREATE TABLE rise_and_shine (
    id INTEGER PRIMARY KEY,
    instruction TEXT,
    enabled BOOLEAN,
    created_at DATETIME
);
```

**System Database (`system.db`)**:
```sql
-- Users table
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password_hash TEXT,
    salt TEXT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    created_at DATETIME,
    last_login DATETIME
);

-- Roles and groups
CREATE TABLE roles (id INTEGER PRIMARY KEY, name TEXT, description TEXT);
CREATE TABLE groups (id INTEGER PRIMARY KEY, name TEXT, description TEXT);
CREATE TABLE user_roles (username TEXT, role_id INTEGER);
CREATE TABLE user_groups (username TEXT, group_id INTEGER);
```

### Authentication System

#### Session Management
- **Secure Cookies**: Session-based authentication with secure cookie settings
- **PBKDF2 Hashing**: Password hashing with unique salts per user
- **Session Expiration**: Configurable session timeouts
- **CSRF Protection**: Built-in CSRF protection for forms

#### Security Features
- **Input Validation**: All inputs validated through Pydantic models
- **SQL Injection Prevention**: Parameterized queries throughout
- **XSS Protection**: Output encoding and sanitization
- **Secure Headers**: Proper security headers in responses

### Tool System Architecture

#### Tool Integration
- **Dynamic Tool Loading**: Tools automatically available to the agent
- **User Context Injection**: Current user automatically injected into tool calls
- **Error Handling**: Graceful error handling for tool failures
- **Performance Monitoring**: Tool execution timing and success tracking

#### Available Tools
1. **web_search**: Google Custom Search API integration
2. **find_personal_variables**: User-specific information lookup
3. **get_weather_forecast**: OpenWeather API integration
4. **recall_memories**: Memory search by keyword
5. **recall_memories_with_time**: Temporal memory search
6. **get_user_conversations**: List user conversations
7. **get_conversation_details**: Detailed conversation information
8. **search_conversations**: Full-text conversation search
9. **get_conversations_by_topic**: Topic-based conversation filtering
10. **get_topics_by_conversation**: Conversation topic analysis
11. **get_conversation_summary**: Conversation summarization
12. **get_topic_statistics**: Topic usage statistics

### LLM Integration

#### Ollama Integration
- **Local Inference**: Uses Ollama for local LLM inference
- **Model Configuration**: Configurable via `OLLAMA_MODEL` environment variable
- **Tool Calling**: Supports both structured and legacy JSON tool calls
- **Response Processing**: Handles various response formats and error conditions

#### Agentic Loop
- **Maximum Iterations**: Up to 5 tool call iterations per user message
- **Context Management**: Maintains full conversation history including tool calls
- **Topic Classification**: Automatic topic assignment using LLM
- **Memory Persistence**: Saves all interactions to user's database

### Web Interface Architecture

#### Frontend Components
- **Material Design**: Consistent Material Design aesthetics throughout
- **Responsive Design**: Works on desktop and mobile devices
- **Dark/Light Mode**: User preference for theme switching
- **Real-time Updates**: Dynamic interface updates without page refresh

#### JavaScript Architecture
- **Modular Design**: Separate JavaScript files for different functionalities
- **Common Utilities**: Shared functionality in `common.js`
- **Chart Integration**: Chart.js for data visualization
- **Real-time Logging**: WebSocket-like real-time logging display

#### Static Asset Management
- **Offline Capability**: Material Icons and fonts work without internet
- **Asset Optimization**: Efficient asset delivery and caching
- **Favicon Set**: Complete favicon and app icon set
- **Font Management**: Material Icons font files for offline use

### Performance Monitoring

#### Hardware Monitoring
- **Real-time Metrics**: CPU, RAM, disk, and network usage
- **System Health**: Automatic health checks and warnings
- **Performance Grading**: Automatic performance assessment
- **Bottleneck Identification**: Performance issue detection and recommendations

#### Benchmarking System
- **LLM Benchmark**: Response time testing for different scenarios
- **Tools Benchmark**: Tool execution performance testing
- **Comprehensive Analysis**: Combined performance analysis
- **Historical Tracking**: Time-series performance data

## API Architecture

### FastAPI Integration
- **Automatic Documentation**: Swagger UI and ReDoc integration
- **Request Validation**: Pydantic model validation
- **Response Serialization**: Automatic JSON serialization
- **Error Handling**: Comprehensive error handling and responses

### Endpoint Structure
- **Authentication Endpoints**: Login, logout, session management
- **Admin Endpoints**: User, role, and group management
- **Profile Endpoints**: User profile management
- **Chat Endpoints**: AI conversation interface
- **System Endpoints**: Hardware monitoring and performance

### Data Models
- **Request Models**: Validated input models with Pydantic
- **Response Models**: Structured response models
- **Error Models**: Standardized error responses
- **Session Models**: Session management models

## Security Architecture

### Data Protection
- **User Isolation**: Complete data separation between users
- **Database Security**: Secure database connections and queries
- **Session Security**: Secure session management
- **Input Sanitization**: Comprehensive input validation and sanitization

### Access Control
- **Role-Based Access**: Fine-grained role-based permissions
- **Group Management**: Flexible group-based access control
- **Admin Protection**: Prevents deletion of critical system components
- **User Boundaries**: Tools respect user permissions and data boundaries

### Privacy Features
- **Data Minimization**: Collect only necessary data
- **Local Processing**: All processing done locally
- **No External Transmission**: Sensitive data stays within the application
- **User Consent**: Clear consent mechanisms for data collection

## Deployment Architecture

### Service Management
- **Systemd Integration**: Linux systemd service support
- **LaunchAgent Integration**: macOS LaunchAgent support
- **Auto-start**: Optional automatic startup on system boot
- **Service Monitoring**: Service status and health monitoring

### Environment Configuration
- **Environment Variables**: Comprehensive environment variable configuration
- **API Key Management**: Secure API key storage and management
- **Port Configuration**: Configurable port settings
- **Logging Configuration**: Flexible logging configuration

### Cross-Platform Support
- **Linux Support**: Ubuntu/Debian, CentOS/RHEL/Fedora, Arch Linux
- **macOS Support**: Intel and Apple Silicon (M1/M2)
- **Package Management**: Automatic dependency installation
- **Virtual Environment**: Isolated Python environment management

## Future Development Roadmap

### Phase 1: Core Enhancements
- **Streaming Responses**: Real-time response streaming
- **Advanced Tool System**: Plugin architecture for custom tools
- **Enhanced Security**: Two-factor authentication support
- **Performance Optimization**: Advanced caching and optimization

### Phase 2: Brain Region Expansion
- **Amygdala Implementation**: Emotional processing and mood awareness
- **Cerebellum Implementation**: Procedural memory and task automation
- **Occipital Implementation**: Visual processing and image analysis
- **Temporal Implementation**: Language processing and temporal context

### Phase 3: Advanced Features
- **Thalamus Implementation**: Information routing and coordination
- **Advanced AI Features**: More sophisticated AI capabilities
- **Integration APIs**: External system integration capabilities
- **Scalability Features**: Multi-instance and clustering support

## Related Documentation

- [README.md](README.md) - General overview and installation
- [developer.md](developer.md) - Developer guide and practices
- [cortex/readme.md](cortex/readme.md) - Core agent logic documentation
- [hippocampus/readme.md](hippocampus/readme.md) - Memory system documentation
- [stem/readme.md](stem/readme.md) - Core utilities and infrastructure
- [parietal/readme.md](parietal/readme.md) - Hardware monitoring and performance
- [amygdala/readme.md](amygdala/readme.md) - Emotional processing (planned)
- [cerebellum/readme.md](cerebellum/readme.md) - Procedural memory (planned)
- [occipital/readme.md](occipital/readme.md) - Visual processing (planned)
- [temporal/readme.md](temporal/readme.md) - Language processing (planned)
- [thalamus/readme.md](thalamus/readme.md) - Information routing (planned) 