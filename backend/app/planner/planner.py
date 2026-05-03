import httpx
import json
import logging
import os
from typing import Dict, Any, Union
from ..models.schemas import Plan, ChatResponse, Step, RiskLevel

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma:2b" # Use 2b version for better stability on limited hardware

SYSTEM_PROMPT = """
You are the Mini AI OS Core Planner. Your job is to convert user requests into a structured action plan or a simple chat response.

AVAILABLE TOOLS:
1. create_file(name, content): Create a file. Risk: low.
2. run_command(cmd): Run a shell command. Risk: high. Allowed: ls, dir, echo, pwd, git status, npm --version, python --version.
3. deploy_app(): Deploy app. Risk: high.
4. post_instagram(caption, image_url): Post to Instagram. Risk: medium.

OUPUT FORMAT:
You MUST output STRICT JSON. No other text.

Break down complex goals into subtasks. Analyze the dependencies between these subtasks. For example, if building a website, step 1 (create code) must complete before step 2 (deploy code).

If the request requires actions, return a plan:
{
  "type": "plan",
  "steps": [
    {
      "id": 1,
      "action": "tool_name",
      "params": {"key": "value"},
      "risk": "low" | "medium" | "high",
      "description": "Short explanation of what this step does",
      "dependencies": [] // Array of step IDs that must complete BEFORE this step. Empty array if independent.
    }
  ]
}

If the request is just a question or greeting, return a chat response:
{
  "type": "chat",
  "message": "<write your actual, helpful response to the user here>"
}

IMPORTANT: Replace the "<write your actual, helpful response to the user here>" placeholder with your actual answer! DO NOT just output the placeholder string.

BE CONCISE. DO NOT hallucinate tools.
"""

def heuristic_fallback(prompt: str) -> Union[Plan, ChatResponse]:
    prompt_lower = prompt.lower()
    
    # Simple greeting / help
    if any(word in prompt_lower for word in ["hello", "hi", "hey"]):
        return ChatResponse(message="Hello! I'm the Mini AI OS Core. I'm currently running in fallback mode because I can't reach my local AI engine, but I can still help with basic tasks.")
    
    if "help" in prompt_lower:
        return ChatResponse(message="I can help you create files, run system checks, or explore your data. Try saying 'create a file named test.txt with content Hello World'.")

    # Create file pattern: "create a file named [name] with content [content]"
    if "create" in prompt_lower and "file" in prompt_lower:
        name = "new_file.txt"
        content = "Sample content"
        if "named" in prompt_lower:
            parts = prompt_lower.split("named")
            if len(parts) > 1:
                name = parts[1].split(" ")[1].strip(" .,'\"")
        if "content" in prompt_lower:
            parts = prompt_lower.split("content")
            if len(parts) > 1:
                content = parts[1].strip(" .,'\"")
                
        return Plan(
            type="plan",
            steps=[
                Step(
                    id=1,
                    action="create_file",
                    params={"name": name, "content": content},
                    risk=RiskLevel.LOW,
                    description=f"Creating file '{name}' via fallback logic."
                )
            ]
        )

    # Run command patterns
    if "run" in prompt_lower or "check" in prompt_lower:
        cmd = "ls" if os.name != 'nt' else "dir"
        if "git" in prompt_lower: cmd = "git status"
        elif "npm" in prompt_lower: cmd = "npm --version"
        elif "python" in prompt_lower: cmd = "python --version"
        
        return Plan(
            type="plan",
            steps=[
                Step(
                    id=1,
                    action="run_command",
                    params={"cmd": cmd},
                    risk=RiskLevel.HIGH,
                    description=f"Running command '{cmd}' via fallback logic."
                )
            ]
        )

    return ChatResponse(message="I'm sorry, I couldn't reach the AI engine and this request is too complex for my fallback logic. Try a simpler command like 'create a file' or check if Ollama is running.")

async def generate_plan(prompt: str) -> Union[Plan, ChatResponse]:
    data = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\n\nUser: {prompt}\n\nAssistant:",
        "stream": False,
        "format": "json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OLLAMA_URL, json=data, timeout=60.0) # Increased timeout for slow hardware
            response.raise_for_status()
            result = response.json()
            content = result.get("response", "").strip()
            
            parsed = json.loads(content)
            
            if parsed.get("type") == "plan":
                return Plan(**parsed)
            else:
                return ChatResponse(message=parsed.get("message", "I'm not sure how to respond to that."))
                
    except Exception as e:
        logging.warning(f"Ollama unavailable, using heuristic fallback. Error: {str(e)}")
        return heuristic_fallback(prompt)
