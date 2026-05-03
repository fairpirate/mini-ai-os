import subprocess
import os
import sys
from pydantic import BaseModel, Field
from typing import Dict, Any
from ..tools.base import AsyncTool, RiskLevel
from ...core.logging import logger

class OpenAppSchema(BaseModel):
    app_name: str = Field(..., description="Name of the application to open (e.g., 'Calculator', 'Terminal')")

class OpenAppTool(AsyncTool):
    name = "open_app"
    description = "Opens a native application on the host OS."
    risk_level = RiskLevel.MEDIUM
    schema = OpenAppSchema

    async def execute(self, params: Dict[str, Any]) -> str:
        app_name = params["app_name"]
        try:
            if sys.platform == "darwin": # macOS
                subprocess.run(["open", "-a", app_name], check=True)
            elif sys.platform == "win32": # Windows
                os.startfile(app_name)
            else: # Linux
                subprocess.Popen([app_name])
            return f"Successfully opened {app_name}."
        except Exception as e:
            logger.error(f"Failed to open app {app_name}: {e}")
            return f"Error opening {app_name}: {e}"

class CreateFileSchema(BaseModel):
    path: str = Field(..., description="Relative path in the sandbox to create the file.")
    content: str = Field(..., description="Text content to write to the file.")

class CreateFileTool(AsyncTool):
    name = "create_file"
    description = "Creates a file in the workspace sandbox with the given content."
    risk_level = RiskLevel.MEDIUM
    schema = CreateFileSchema

    async def execute(self, params: Dict[str, Any]) -> str:
        sandbox_dir = "sandbox"
        os.makedirs(sandbox_dir, exist_ok=True)
        
        file_path = os.path.join(sandbox_dir, params["path"])
        # Prevent path traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(sandbox_dir)):
            return "Error: Cannot create files outside the sandbox directory."
            
        try:
            with open(file_path, "w") as f:
                f.write(params["content"])
            return f"Created file {params['path']} successfully."
        except Exception as e:
            return f"Error creating file: {e}"

def register_tools(registry):
    registry.register(OpenAppTool())
    registry.register(CreateFileTool())
