import os
import subprocess
from typing import Dict, Any
from .base import Tool, registry
from ..models.schemas import RiskLevel

class CreateFileTool(Tool):
    name = "create_file"
    description = "Creates a file with the given name and content."
    risk_level = RiskLevel.LOW

    def validate(self, params: Dict[str, Any]) -> bool:
        return "name" in params and "content" in params

    def execute(self, params: Dict[str, Any]) -> str:
        name = params["name"]
        content = params["content"]
        # In a real production app, we'd ensure this happens in a sandbox
        # For now, we'll just write to a 'sandbox' directory in the workspace
        sandbox_dir = "sandbox"
        if not os.path.exists(sandbox_dir):
            os.makedirs(sandbox_dir)
        
        file_path = os.path.join(sandbox_dir, name)
        with open(file_path, "w") as f:
            f.write(content)
        return f"File '{name}' created successfully at {file_path}."

class RunCommandTool(Tool):
    name = "run_command"
    description = "Runs a shell command (allowlisted)."
    risk_level = RiskLevel.HIGH
    
    # Simple allowlist for security
    ALLOWLIST = ["ls", "dir", "echo", "pwd", "git status", "npm --version", "python --version"]

    def validate(self, params: Dict[str, Any]) -> bool:
        cmd = params.get("cmd", "")
        base_cmd = cmd.split(" ")[0]
        return any(cmd.startswith(a) for a in self.ALLOWLIST)

    def execute(self, params: Dict[str, Any]) -> str:
        cmd = params["cmd"]
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Execution failed: {str(e)}"

class DeployAppTool(Tool):
    name = "deploy_app"
    description = "Deploys the application to a cloud provider (Stub)."
    risk_level = RiskLevel.HIGH

    def validate(self, params: Dict[str, Any]) -> bool:
        return True

    def execute(self, params: Dict[str, Any]) -> str:
        return "Deployment initiated (Mock). Application will be live at: https://demo-app.example.com"

class PostInstagramTool(Tool):
    name = "post_instagram"
    description = "Posts a caption and image to Instagram (Stub)."
    risk_level = RiskLevel.MEDIUM

    def validate(self, params: Dict[str, Any]) -> bool:
        return "caption" in params

    def execute(self, params: Dict[str, Any]) -> str:
        return f"Successfully posted to Instagram: '{params.get('caption')}'"

# Register tools
registry.register(CreateFileTool())
registry.register(RunCommandTool())
registry.register(DeployAppTool())
registry.register(PostInstagramTool())
