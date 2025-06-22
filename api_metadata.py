"""
api_metadata.py

FastAPI tags metadata configuration for Tatlock API documentation.
Contains module descriptions and external documentation links for all brain-inspired modules.
"""

# Define tags metadata for API documentation
tags_metadata = [
    {
        "name": "cerebellum",
        "description": "External API integration and procedural tools for Tatlock. Provides web search, weather forecasting, and procedural automation features.",
        "externalDocs": {
            "description": "Cerebellum Module Documentation",
            "url": "https://github.com/jeroenschweitzer/tatlock/blob/main/cerebellum/readme.md",
        },
    },
    {
        "name": "cortex",
        "description": "Core agent logic for Tatlock. Orchestrates all subsystems and handles chat interactions with comprehensive session-based authentication.",
        "externalDocs": {
            "description": "Cortex Module Documentation",
            "url": "https://github.com/jeroenschweitzer/tatlock/blob/main/cortex/readme.md",
        },
    },
    {
        "name": "hippocampus",
        "description": "Memory system for Tatlock. Manages persistent memory, databases, and long-term storage with user isolation and privacy.",
        "externalDocs": {
            "description": "Hippocampus Module Documentation",
            "url": "https://github.com/jeroenschweitzer/tatlock/blob/main/hippocampus/readme.md",
        },
    },
    {
        "name": "occipital",
        "description": "Visual processing and screenshot testing for Tatlock. Provides automated UI testing, visual regression detection, and visual content analysis.",
        "externalDocs": {
            "description": "Occipital Module Documentation",
            "url": "https://github.com/jeroenschweitzer/tatlock/blob/main/occipital/readme.md",
        },
    },
    {
        "name": "parietal",
        "description": "Hardware monitoring and performance analysis for Tatlock. Provides system information, performance benchmarking, and hardware resource monitoring.",
        "externalDocs": {
            "description": "Parietal Module Documentation",
            "url": "https://github.com/jeroenschweitzer/tatlock/blob/main/parietal/readme.md",
        },
    },
    {
        "name": "stem",
        "description": "Core infrastructure and authentication for Tatlock. Provides shared utilities, session-based authentication, admin dashboard, and static file serving.",
        "externalDocs": {
            "description": "Stem Module Documentation",
            "url": "https://github.com/jeroenschweitzer/tatlock/blob/main/stem/readme.md",
        },
    },
    {
        "name": "temporal",
        "description": "Voice processing and language understanding for Tatlock. Handles speech recognition, temporal context awareness, and auditory processing.",
        "externalDocs": {
            "description": "Temporal Module Documentation",
            "url": "https://github.com/jeroenschweitzer/tatlock/blob/main/temporal/readme.md",
        },
    },
    {
        "name": "admin",
        "description": "Administrative functions for Tatlock. Provides user management, role and group administration, system statistics, and admin dashboard interface.",
        "externalDocs": {
            "description": "Stem Module Documentation (Admin Functions)",
            "url": "https://github.com/jeroenschweitzer/tatlock/blob/main/stem/readme.md",
        },
    },
    {
        "name": "profile",
        "description": "User profile management for Tatlock. Provides self-service profile editing, password changes, and user information retrieval.",
        "externalDocs": {
            "description": "Stem Module Documentation (Profile Functions)",
            "url": "https://github.com/jeroenschweitzer/tatlock/blob/main/stem/readme.md",
        },
    },
    {
        "name": "api",
        "description": "Core API endpoints for Tatlock functionality.",
    },
    {
        "name": "html",
        "description": "HTML page endpoints for Tatlock web interface.",
    },
    {
        "name": "debug",
        "description": "Debug and testing endpoints for development.",
    },
    {
        "name": "root",
        "description": "Root and redirect endpoints.",
    },
] 