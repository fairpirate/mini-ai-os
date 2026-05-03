import json
import httpx
import time
from typing import List, Dict, AsyncGenerator, Optional
from ..core.config import settings
from ..core.logging import logger
from ..core.metrics import metrics_service
from .personality import personality_manager

class OllamaService:
    """
    AI Service for connecting FastAPI with local models via Ollama.
    Supports streaming, context memory, and system personality switching.
    """
    
    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.default_model = settings.MODEL_NAME
        self.failure_count = 0
        self.max_failures = 3
        self.last_failure_time = 0

    def _get_system_prompt(self, mode: str) -> str:
        # Use dynamic personality prompt instead of hardcoded ones
        prompt = personality_manager.get_system_prompt()
        
        # Inject tool support if in jarvis mode (default for tools)
        if mode == "jarvis":
            from .tools.registry import tool_registry
            tools = tool_registry.list_tools()
            if tools:
                tools_json = json.dumps(tools, indent=2)
                prompt += f"\n\nYou have access to the following tools:\n{tools_json}\n\nTo use a tool, YOU MUST output EXACTLY one JSON object and NOTHING else. Format:\n{{\n  \"type\": \"tool_call\",\n  \"tool\": \"tool_name\",\n  \"params\": {{ ... }}\n}}"
        elif mode == "planner":
            # Override for specialized agent modes if needed
            prompt = "You are the Task Orchestrator. Your job is to break down a user's goal into a logical list of subtasks. Output ONLY a valid JSON list of objects with a 'description' field."
        
        return prompt

    def _optimize_history(self, history: List[Dict[str, str]], max_messages: int = 10) -> List[Dict[str, str]]:
        if not history:
            return []
        return history[-max_messages:]

    async def send_prompt(self, prompt: str, history: Optional[List[Dict[str, str]]] = None, mode: str = "jarvis") -> str:
        # Check circuit breaker
        if self.failure_count >= self.max_failures:
            if time.time() - self.last_failure_time < 30: # 30s timeout
                return "System Alert: Neural link is currently unstable. Circuit breaker active. Please wait 30 seconds."
            else:
                self.failure_count = 0 # Reset after timeout

        start_time = time.time()
        messages = [{"role": "system", "content": self._get_system_prompt(mode)}]
        if history:
            messages.extend(self._optimize_history(history))
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.default_model,
            "messages": messages,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload, timeout=120.0)
                response.raise_for_status()
                data = response.json()
                content = data.get("message", {}).get("content", "").strip()
                
                # Record performance
                latency = time.time() - start_time
                token_count = len(content.split()) * 1.3
                metrics_service.record_ai_performance(latency, token_count)
                
                # Reset failures on success
                self.failure_count = 0
                return content
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            logger.error(f"Ollama generation error: {e}", exc_info=True)
            return "I apologize, sir. My local neural network is currently experiencing a high-load failure."

    async def stream_response(self, prompt: str, history: Optional[List[Dict[str, str]]] = None, mode: str = "jarvis") -> AsyncGenerator[str, None]:
        start_time = time.time()
        token_count = 0
        messages = [{"role": "system", "content": self._get_system_prompt(mode)}]
        if history:
            messages.extend(self._optimize_history(history))
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.default_model,
            "messages": messages,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload, timeout=60.0) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            chunk = data.get("message", {}).get("content", "")
                            if chunk:
                                token_count += 1
                                yield chunk
                
                # Record performance
                latency = time.time() - start_time
                metrics_service.record_ai_performance(latency, token_count)
        except Exception as e:
            logger.error(f"Ollama stream error: {e}", exc_info=True)
            yield "\n[System Fault: Stream interrupted.]"

# Singleton instance
ai_service = OllamaService()
