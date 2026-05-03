import importlib
import os
import pkgutil
from typing import Dict, Any, List
from .base import AsyncTool
from ...core.logging import logger

class PluginRegistry:
    """Dynamically loads and registers tool plugins from the plugins directory."""
    def __init__(self):
        self._tools: Dict[str, AsyncTool] = {}

    def register(self, tool: AsyncTool):
        if tool.name in self._tools:
            logger.warning(f"Tool {tool.name} is already registered. Overwriting.")
        self._tools[tool.name] = tool
        logger.info(f"Registered Tool: {tool.name} (Risk: {tool.risk_level})")

    def get_tool(self, name: str) -> AsyncTool:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "description": tool.description,
                "risk_level": tool.risk_level.value,
                "schema": tool.schema.schema() if tool.schema else {}
            }
            for name, tool in self._tools.items()
        ]

    def load_plugins(self, plugin_dir: str = "app.engine.plugins"):
        """Scans the plugin module directory and imports all tools."""
        try:
            module = importlib.import_module(plugin_dir)
            for _, name, is_pkg in pkgutil.iter_modules(module.__path__):
                if not is_pkg:
                    full_module_name = f"{plugin_dir}.{name}"
                    try:
                        plugin_module = importlib.import_module(full_module_name)
                        # We expect each plugin to have a 'register_tools(registry)' function
                        if hasattr(plugin_module, "register_tools"):
                            plugin_module.register_tools(self)
                    except Exception as e:
                        logger.error(f"Failed to load plugin {name}: {e}")
        except Exception as e:
            logger.error(f"Failed to load plugins directory: {e}")

# Global registry instance
tool_registry = PluginRegistry()
