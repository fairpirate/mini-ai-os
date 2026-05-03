from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel

class RiskLevel(str, Enum):
    LOW = "LOW"       # No side effects, safe (e.g., getting time, searching web)
    MEDIUM = "MEDIUM" # Minor side effects, recoverable (e.g., creating a file in sandbox)
    HIGH = "HIGH"     # Dangerous, requires explicit approval (e.g., running shell commands)

class AsyncTool(ABC):
    """
    Base class for all asynchronous AI tools.
    Enforces a strict schema and risk level for the Execution Engine.
    """
    name: str
    description: str
    risk_level: RiskLevel
    schema: BaseModel # Pydantic model defining expected inputs

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> str:
        """Executes the tool with the provided, validated parameters."""
        pass
        
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validates input against the defined Pydantic schema."""
        try:
            self.schema(**params)
            return True
        except Exception:
            return False
