import os
import importlib.util
import asyncio
import json
from typing import Dict, List, Optional
from .models import PluginManifest, PluginStatus, PluginType, PluginBase
from ..tools.registry import tool_registry
from ...core.logging import logger

class PluginManager:
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, PluginBase] = {}
        os.makedirs(self.plugins_dir, exist_ok=True)

    async def discover(self):
        """Scans the plugins directory for valid manifests."""
        logger.info(f"Scanning for plugins in {self.plugins_dir}...")
        for plugin_folder in os.listdir(self.plugins_dir):
            folder_path = os.path.join(self.plugins_dir, plugin_folder)
            if not os.path.isdir(folder_path):
                continue

            manifest_path = os.path.join(folder_path, "plugin.json")
            if not os.path.exists(manifest_path):
                continue

            try:
                with open(manifest_path, 'r') as f:
                    manifest_data = json.load(f)
                    manifest = PluginManifest(**manifest_data)
                    await self.load_plugin(manifest, folder_path)
            except Exception as e:
                logger.error(f"Failed to load plugin from {plugin_folder}: {e}")

    async def load_plugin(self, manifest: PluginManifest, path: str):
        """Loads a plugin into the system based on its type."""
        if manifest.type == PluginType.PYTHON:
            plugin = await self._load_python_plugin(manifest, path)
        elif manifest.type == PluginType.JAVASCRIPT:
            plugin = await self._load_js_plugin(manifest, path)
        else:
            raise ValueError(f"Unsupported plugin type: {manifest.type}")

        if plugin:
            self.plugins[manifest.id] = plugin
            logger.info(f"Plugin loaded: {manifest.name} (v{manifest.version})")
            await self.enable_plugin(manifest.id)

    async def _load_python_plugin(self, manifest: PluginManifest, path: str) -> Optional[PluginBase]:
        """Dynamically imports a Python plugin entry point."""
        entry_point_path = os.path.join(path, manifest.entry_point)
        if not os.path.exists(entry_point_path):
            logger.error(f"Entry point {manifest.entry_point} not found for {manifest.id}")
            return None

        try:
            # Dynamic import
            spec = importlib.util.spec_from_file_location(f"plugin_{manifest.id}", entry_point_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Expecting a 'create_plugin' function or a 'Plugin' class
            if hasattr(module, "Plugin"):
                plugin_instance = module.Plugin(manifest, path)
                await plugin_instance.initialize()
                return plugin_instance
            else:
                logger.error(f"Python plugin {manifest.id} missing 'Plugin' class.")
                return None
        except Exception as e:
            logger.error(f"Error loading Python plugin {manifest.id}: {e}", exc_info=True)
            return None

    async def _load_js_plugin(self, manifest: PluginManifest, path: str) -> Optional[PluginBase]:
        """
        Placeholder for JS plugin loader. 
        In a real implementation, this would use a Node.js bridge or WASM.
        """
        logger.warning(f"JS Plugin {manifest.id} detected. Native JS support is via Node.js bridge (Experimental).")
        # Logic would involve spawning a Node process and communicating via RPC
        return None

    async def enable_plugin(self, plugin_id: str):
        if plugin_id in self.plugins:
            plugin = self.plugins[plugin_id]
            # Register tools to the global registry
            for tool in plugin.tools:
                tool_registry.register(tool)
            plugin.status = PluginStatus.ENABLED
            logger.info(f"Plugin enabled: {plugin_id}")

    async def disable_plugin(self, plugin_id: str):
        if plugin_id in self.plugins:
            plugin = self.plugins[plugin_id]
            # Unregister tools (requires registry support for removal)
            # tool_registry.unregister_by_plugin(plugin_id)
            plugin.status = PluginStatus.DISABLED
            logger.info(f"Plugin disabled: {plugin_id}")

    async def broadcast_event(self, event_name: str, payload: Any):
        """Passes events to all enabled plugins."""
        for plugin in self.plugins.values():
            if plugin.status == PluginStatus.ENABLED:
                asyncio.create_task(plugin.on_event(event_name, payload))

# Singleton manager
plugin_manager = PluginManager()
