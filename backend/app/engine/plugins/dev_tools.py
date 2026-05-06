import asyncio
from pydantic import BaseModel, Field
from typing import Dict, Any
from ..tools.base import AsyncTool, RiskLevel
from ...core.logging import logger

class RunCommandSchema(BaseModel):
    cmd: str = Field(..., description="The shell command to execute.")

class RunCommandTool(AsyncTool):
    name = "run_command"
    description = "Executes a shell command. THIS IS HIGH RISK AND REQUIRES APPROVAL."
    risk_level = RiskLevel.HIGH
    schema = RunCommandSchema

    async def execute(self, params: Dict[str, Any]) -> str:
        import os
        cmd = params["cmd"]
        # Normalise: if cmd references sandbox/X, strip prefix since we CWD into sandbox
        cmd = cmd.replace("sandbox/", "")
        sandbox_dir = os.path.abspath("sandbox")
        os.makedirs(sandbox_dir, exist_ok=True)
        try:
            logger.info(f"Executing shell command (cwd=sandbox): {cmd}")
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=sandbox_dir,
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
    registry.register(RunCommandTool())
