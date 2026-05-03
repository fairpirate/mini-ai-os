import asyncio
from pydantic import BaseModel, Field
from typing import Dict, Any
from ..tools.base import AsyncTool, RiskLevel
from ...core.logging import logger

class RunTerminalCommandSchema(BaseModel):
    command: str = Field(..., description="The shell command to execute.")

class RunTerminalCommandTool(AsyncTool):
    name = "run_terminal_command"
    description = "Executes a shell command. THIS IS HIGH RISK AND REQUIRES APPROVAL."
    risk_level = RiskLevel.HIGH
    schema = RunTerminalCommandSchema

    async def execute(self, params: Dict[str, Any]) -> str:
        command = params["command"]
        try:
            logger.info(f"Executing shell command: {command}")
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            result = ""
            if stdout:
                result += f"Output:\n{stdout.decode()}\n"
            if stderr:
                result += f"Error:\n{stderr.decode()}\n"
                
            return result.strip() if result else "Command executed successfully with no output."
        except Exception as e:
            return f"Execution error: {e}"

def register_tools(registry):
    registry.register(RunTerminalCommandTool())
