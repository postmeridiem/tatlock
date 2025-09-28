"""
stem/dynamic_tools.py

Dynamic tool loading system for Tatlock.
Supports modular tool architecture with plugin-style loading for external tool sources.
"""

import importlib
import logging
import sqlite3
import os
import sys
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class ToolMetadata:
    """Metadata for a dynamically loaded tool."""
    key: str
    description: str
    module_path: str
    function_name: str
    enabled: bool
    is_core: bool
    source: str  # 'built-in', 'plugin', 'external'
    version: Optional[str] = None
    author: Optional[str] = None
    dependencies: List[str] = None

class DynamicToolRegistry:
    """
    Registry for dynamically loading and managing tools.
    Supports built-in tools, plugins, and external tool packages.
    """

    def __init__(self):
        self._loaded_tools: Dict[str, Callable] = {}
        self._tool_metadata: Dict[str, ToolMetadata] = {}
        self._module_cache: Dict[str, Any] = {}
        self._plugin_paths: List[Path] = []

        # Core tools that are always loaded
        self._core_tools = set()

    def initialize(self, database_path: str = "hippocampus/system.db"):
        """Initialize the tool registry from database and discover plugins."""
        self._load_tool_metadata_from_db(database_path)
        self._discover_plugin_directories()
        self._load_core_tools()

    def _load_tool_metadata_from_db(self, db_path: str):
        """Load tool metadata from the database."""
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT tool_key, description, module, function_name, enabled
                FROM tools
            """)

            for row in cursor.fetchall():
                metadata = ToolMetadata(
                    key=row['tool_key'],
                    description=row['description'],
                    module_path=row['module'],
                    function_name=row['function_name'],
                    enabled=bool(row['enabled']),
                    is_core=self._is_core_tool(row['tool_key']),
                    source='built-in'
                )
                self._tool_metadata[row['tool_key']] = metadata

                if metadata.is_core:
                    self._core_tools.add(row['tool_key'])

            conn.close()
            logger.info(f"Loaded metadata for {len(self._tool_metadata)} tools from database")

        except Exception as e:
            logger.error(f"Error loading tool metadata from database: {e}")

    def _is_core_tool(self, tool_key: str) -> bool:
        """Check if a tool is a core tool."""
        # Import here to avoid circular imports
        try:
            from hippocampus.database import CORE_TOOLS
            return tool_key in CORE_TOOLS
        except ImportError:
            # Fallback core tools list
            core_tools = [
                'recall_memories',
                'recall_memories_with_time',
                'find_personal_variables',
                'get_temporal_info'
            ]
            return tool_key in core_tools

    def _discover_plugin_directories(self):
        """Discover plugin directories for external tools."""
        # Brain-region distributed plugin architecture
        plugin_dirs = [
            Path("cortex/plugins"),          # Reasoning and decision-making plugins
            Path("hippocampus/plugins"),     # Memory and learning plugins
            Path("cerebellum/plugins"),      # External API and skill plugins
            Path("parietal/plugins"),        # System monitoring and hardware plugins
            Path("occipital/plugins"),       # Visual processing plugins
            Path("temporal/plugins"),        # Language and voice plugins
            Path("stem/plugins"),            # Core system and authentication plugins
            Path.home() / ".tatlock" / "plugins",  # User plugins
        ]

        # Add environment variable paths
        if 'TATLOCK_PLUGIN_PATHS' in os.environ:
            for path in os.environ['TATLOCK_PLUGIN_PATHS'].split(':'):
                plugin_dirs.append(Path(path))

        for plugin_dir in plugin_dirs:
            if plugin_dir.exists():
                self._plugin_paths.append(plugin_dir)
                self._discover_plugins_in_directory(plugin_dir)

    def _discover_plugins_in_directory(self, plugin_dir: Path):
        """Discover and register plugins in a directory."""
        for plugin_path in plugin_dir.iterdir():
            if plugin_path.is_dir():
                manifest_file = plugin_path / "tool_manifest.json"
                if manifest_file.exists():
                    self._load_plugin_manifest(plugin_path, manifest_file)

    def _load_plugin_manifest(self, plugin_path: Path, manifest_file: Path):
        """Load a plugin from its manifest file."""
        try:
            with open(manifest_file) as f:
                manifest = json.load(f)

            for tool_def in manifest.get('tools', []):
                metadata = ToolMetadata(
                    key=tool_def['key'],
                    description=tool_def['description'],
                    module_path=f"{plugin_path.name}.{tool_def['module']}",
                    function_name=tool_def['function'],
                    enabled=tool_def.get('enabled', True),
                    is_core=tool_def.get('is_core', False),
                    source='plugin',
                    version=manifest.get('version'),
                    author=manifest.get('author'),
                    dependencies=tool_def.get('dependencies', [])
                )

                self._tool_metadata[tool_def['key']] = metadata

                # Add plugin path to sys.path for importing
                if str(plugin_path.parent) not in sys.path:
                    sys.path.insert(0, str(plugin_path.parent))

            logger.info(f"Loaded plugin: {manifest.get('name')} v{manifest.get('version')}")

        except Exception as e:
            logger.error(f"Error loading plugin manifest {manifest_file}: {e}")

    def _load_core_tools(self):
        """Pre-load all core tools."""
        for tool_key in self._core_tools:
            self.get_tool(tool_key)

    def get_tool(self, tool_key: str) -> Optional[Callable]:
        """
        Get a tool by key, loading it dynamically if not already loaded.

        Args:
            tool_key: The tool identifier

        Returns:
            The tool function or None if not found
        """
        # Return cached tool if already loaded
        if tool_key in self._loaded_tools:
            return self._loaded_tools[tool_key]

        # Load tool if metadata exists
        if tool_key in self._tool_metadata:
            return self._load_tool(tool_key)

        logger.warning(f"Tool '{tool_key}' not found in registry")
        return None

    def _load_tool(self, tool_key: str) -> Optional[Callable]:
        """Load a specific tool function."""
        metadata = self._tool_metadata[tool_key]

        if not metadata.enabled:
            logger.debug(f"Tool '{tool_key}' is disabled")
            return None

        try:
            # Load module if not cached
            if metadata.module_path not in self._module_cache:
                module = importlib.import_module(metadata.module_path)
                self._module_cache[metadata.module_path] = module
            else:
                module = self._module_cache[metadata.module_path]

            # Get function from module
            if hasattr(module, metadata.function_name):
                tool_function = getattr(module, metadata.function_name)
                self._loaded_tools[tool_key] = tool_function
                logger.debug(f"Loaded tool: {tool_key} from {metadata.module_path}")
                return tool_function
            else:
                logger.error(f"Function '{metadata.function_name}' not found in module '{metadata.module_path}'")
                return None

        except Exception as e:
            logger.error(f"Error loading tool '{tool_key}': {e}")
            return None

    def get_available_tools(self, enabled_only: bool = True) -> List[str]:
        """Get list of available tool keys."""
        if enabled_only:
            return [key for key, meta in self._tool_metadata.items() if meta.enabled]
        return list(self._tool_metadata.keys())

    def get_core_tools(self) -> List[str]:
        """Get list of core tool keys."""
        return list(self._core_tools)

    def get_tool_metadata(self, tool_key: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool."""
        return self._tool_metadata.get(tool_key)

    def reload_tool(self, tool_key: str) -> bool:
        """Reload a specific tool (useful for development)."""
        if tool_key not in self._tool_metadata:
            return False

        metadata = self._tool_metadata[tool_key]

        # Remove from caches
        self._loaded_tools.pop(tool_key, None)
        if metadata.module_path in self._module_cache:
            importlib.reload(self._module_cache[metadata.module_path])

        # Reload
        return self._load_tool(tool_key) is not None

    def install_external_tool_pack(self, source_path: str, target_dir: str = "plugins") -> bool:
        """
        Install an external tool pack.

        Args:
            source_path: Path to tool pack (local directory or git repo)
            target_dir: Directory to install to

        Returns:
            True if successful
        """
        try:
            target_path = Path(target_dir)
            target_path.mkdir(exist_ok=True)

            # This is a placeholder for future implementation
            # Would handle git cloning, copying files, dependency resolution, etc.
            logger.info(f"Tool pack installation from {source_path} would go here")
            return True

        except Exception as e:
            logger.error(f"Error installing tool pack: {e}")
            return False

    def get_tool_info(self) -> Dict[str, Any]:
        """Get comprehensive information about all tools."""
        return {
            "total_tools": len(self._tool_metadata),
            "enabled_tools": len([m for m in self._tool_metadata.values() if m.enabled]),
            "core_tools": len(self._core_tools),
            "loaded_tools": len(self._loaded_tools),
            "plugin_paths": [str(p) for p in self._plugin_paths],
            "tools_by_source": {
                source: len([m for m in self._tool_metadata.values() if m.source == source])
                for source in ['built-in', 'plugin', 'external']
            }
        }

# Global registry instance
tool_registry = DynamicToolRegistry()

def get_tool_function(tool_key: str) -> Optional[Callable]:
    """
    Get a tool function by key (main interface for agent).

    Args:
        tool_key: Tool identifier

    Returns:
        Tool function or None
    """
    return tool_registry.get_tool(tool_key)

def initialize_tool_system(database_path: str = "hippocampus/system.db"):
    """Initialize the dynamic tool system."""
    tool_registry.initialize(database_path)

def get_available_tool_keys(enabled_only: bool = True) -> List[str]:
    """Get list of available tool keys."""
    return tool_registry.get_available_tools(enabled_only)

def is_tool_loaded(tool_key: str) -> bool:
    """Check if a tool is currently loaded."""
    return tool_key in tool_registry._loaded_tools