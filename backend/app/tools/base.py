from abc import ABC, abstractmethod
from typing import Dict, Any, Type
from ..models.schemas import RiskLevel

class Tool(ABC):
    name: str
    description: str
    risk_level: RiskLevel

    @abstractmethod
    def validate(self, params: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> str:
        pass

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        return self._tools.get(name)

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        return {name: {"description": t.description, "risk": t.risk_level} for name, t in self._tools.items()}

# Global registry
registry = ToolRegistry()
