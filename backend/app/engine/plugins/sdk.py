from typing import Dict, Any, List, Callable, Coroutine
import asyncio
from .models import PluginBase, PluginManifest
from ..tools.base import AsyncTool, RiskLevel

class JARVISPlugin(PluginBase):
    """
    The developer-facing SDK base class.
    Provides helpers for tool registration and event hooks.
    """
    def __init__(self, manifest: PluginManifest, plugin_dir: str):
        super().__init__(manifest, plugin_dir)
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Register handlers marked with @on
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, "_hook_event"):
                event_name = getattr(attr, "_hook_event")
                if event_name not in self._event_handlers:
                    self._event_handlers[event_name] = []
                self._event_handlers[event_name].append(attr)

    def register_tool(self, tool: AsyncTool):
        """Adds a tool to the plugin's toolset."""
        self.tools.append(tool)

    @staticmethod
    def on(event_name: str):
        """Decorator for registering event handlers on class methods."""
        def decorator(func: Callable):
            func._hook_event = event_name
            return func
        return decorator

    async def on_event(self, event_name: str, payload: Any):
        """Executes all registered handlers for an event."""
        if event_name in self._event_handlers:
            for handler in self._event_handlers[event_name]:
                try:
                    if asyncio.iscoroutinefunction(handler) or asyncio.iscoroutine(handler):
                        await handler(payload)
                    else:
                        # Handle potential bound methods
                        res = handler(payload)
                        if asyncio.iscoroutine(res):
                            await res
                except Exception as e:
                    print(f"Error in plugin event handler ({self.manifest.id}): {e}")

# Helper for creating tools within plugins
class PluginTool(AsyncTool):
    def __init__(self, name: str, description: str, risk: RiskLevel, schema: Any, func: Callable):
        self.name = name
        self.description = description
        self.risk_level = risk
        self.schema = schema
        self._func = func

    async def execute(self, params: Dict[str, Any]) -> str:
        return await self._func(params)
