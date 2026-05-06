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

class ReadFileTool(Tool):
    name = "read_file"
    description = "Reads the content of a file in the sandbox."
    risk_level = RiskLevel.LOW

    def validate(self, params: Dict[str, Any]) -> bool:
        return "name" in params

    def execute(self, params: Dict[str, Any]) -> str:
        name = params["name"]
        sandbox_dir = "sandbox"
        file_path = os.path.join(sandbox_dir, name)
        
        if not os.path.exists(file_path):
            return f"Error: File '{name}' does not exist."
        
        try:
            with open(file_path, "r") as f:
                content = f.read()
            return f"Content of '{name}':\n\n{content}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

class ListDirectoryTool(Tool):
    name = "list_directory"
    description = "Lists all files in the sandbox environment."
    risk_level = RiskLevel.LOW

    def validate(self, params: Dict[str, Any]) -> bool:
        return True

    def execute(self, params: Dict[str, Any]) -> str:
        sandbox_dir = "sandbox"
        if not os.path.exists(sandbox_dir):
            os.makedirs(sandbox_dir)
        
        files = os.listdir(sandbox_dir)
        if not files:
            return "The sandbox is currently empty."
        
        return "Files in sandbox:\n" + "\n".join([f"- {f}" for f in files])

class SearchWebTool(Tool):
    name = "search_web"
    description = "Searches the web for information (Mocked)."
    risk_level = RiskLevel.LOW

    def validate(self, params: Dict[str, Any]) -> bool:
        return "query" in params

    def execute(self, params: Dict[str, Any]) -> str:
        query = params["query"]
        # In a real app, this would use Google Search API, Brave Search, etc.
        return f"Top search results for '{query}':\n1. Wikipedia: Information about {query}\n2. News: Latest updates on {query}\n3. Official Website for {query}"

class GetWeatherTool(Tool):
    name = "get_weather"
    description = "Gets the current weather for a location (Mocked)."
    risk_level = RiskLevel.LOW

    def validate(self, params: Dict[str, Any]) -> bool:
        return "location" in params

    def execute(self, params: Dict[str, Any]) -> str:
        location = params["location"]
        return f"The current weather in {location} is 72°F (22°C) with clear skies."

class RunCommandTool(Tool):
    name = "run_command"
    description = "Runs a shell command (allowlisted)."
    risk_level = RiskLevel.HIGH
    
    # Expanded allowlist
    ALLOWLIST = [
        "ls", "dir", "echo", "pwd", "git status", "git log", 
        "npm --version", "python --version", "python", "pip list", "node -v",
        "date", "whoami", "uname -a"
    ]

    def validate(self, params: Dict[str, Any]) -> bool:
        cmd = params.get("cmd", "")
        if not cmd: return False
        base_cmd = cmd.split(" ")[0]
        # Check if the command starts with an allowlisted base command
        return any(cmd.strip() == a or cmd.startswith(a + " ") for a in self.ALLOWLIST)

    def execute(self, params: Dict[str, Any]) -> str:
        cmd = params["cmd"]
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            output = result.stdout if result.returncode == 0 else result.stderr
            return output if output else "[No output]"
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
registry.register(ReadFileTool())
registry.register(ListDirectoryTool())
registry.register(SearchWebTool())
registry.register(GetWeatherTool())
registry.register(RunCommandTool())
registry.register(DeployAppTool())
registry.register(PostInstagramTool())
