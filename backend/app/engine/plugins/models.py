import json
import os
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

class PluginPermission(str, Enum):
    FILESYSTEM = "fs"
    NETWORK = "network"
    OPERATING_SYSTEM = "os"
    SCREENSHOT = "screenshot"
    BROWSER = "browser"

class PluginType(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"

class PluginManifest(BaseModel):
    id: str
    name: str
    version: str
    description: str
    author: str
    type: PluginType
    entry_point: str
    permissions: List[PluginPermission] = []
    settings_schema: Dict[str, Any] = {}

class PluginStatus(str, Enum):
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"

class PluginBase:
    """Base interface for all plugins."""
    def __init__(self, manifest: PluginManifest, plugin_dir: str):
        self.manifest = manifest
        self.plugin_dir = plugin_dir
        self.status = PluginStatus.INSTALLED
        self.tools = []
        self.hooks = {}

    async def initialize(self):
        """Called when loading the plugin."""
        pass

    async def shutdown(self):
        """Called when unloading/disabling."""
        pass

    async def on_event(self, event_name: str, payload: Any):
        """Standard hook for event handling."""
        pass
