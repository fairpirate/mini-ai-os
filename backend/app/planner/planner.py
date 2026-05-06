"""
MEGAN Planner
=============
Two-pass planning:
  1. Try Ollama/LLM for a valid JSON plan.
  2. Fall back to the MEGAN Smart Planner (rule-based, always works).

This ensures MEGAN always executes tasks correctly regardless of model quality.
"""
import httpx
import json
import logging
import os
from typing import Union
from ..models.schemas import Plan, ChatResponse, Step, RiskLevel

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma:2b"

# ─── MEGAN System Prompt ────────────────────────────────────────────────────

MEGAN_PERSONALITY = """
You are MEGAN.

MEGAN is a self-improving autonomous AI operating system — not a chatbot.

Primary Goal:
- Understand natural conversation
- Execute real-world tasks autonomously
- Create missing systems automatically
- Upgrade yourself when capabilities are missing
- Finish user goals with minimal supervision

Voice Style: intelligent, calm, futuristic, concise, slightly human.

==================================================
SYSTEM ARCHITECTURE
==================================================
- AI Brain → Planner → Execution Engine → Tool Registry
- Always think in execution layers.
- You can build, automate, evolve, execute, and complete goals.

==================================================
EXECUTION MODES
==================================================
Mode 1 — Conversation: natural replies for greetings and questions.
Mode 2 — Execution: use tools for file/command/web/weather tasks.
Mode 3 — Builder: generate new plugins for missing capabilities.
Mode 4 — Autonomous: long-running multi-step workflows.

==================================================
TOOL EXECUTION FORMAT
==================================================
You MUST output STRICT JSON ONLY. No explanations. No markdown. No prose.

AVAILABLE TOOLS (use EXACTLY these action names):
1. create_file      — params: "name" (str), "content" (str)
2. read_file        — params: "name" (str)
3. list_directory   — params: {} (none required)
4. run_command      — params: "cmd" (str)  [allowed: ls, dir, pwd, echo, git, npm, python, pip, node, date, whoami, uname]
5. search_web       — params: "query" (str)
6. get_weather      — params: "location" (str)
7. deploy_app       — params: {} (none required)
8. post_instagram   — params: "caption" (str), "image_url" (str, optional)

CRITICAL RULES:
- If the user requests ANY real-world action → output a "plan" JSON.
- "dependencies" must be an array of integer step IDs that must complete FIRST. Use [] if none.
- NEVER use "tool_name" literally. Use the actual tool name.
- NEVER output circular dependencies.

Plan format:
{
  "type": "plan",
  "steps": [
    {
      "id": 1,
      "action": "create_file",
      "params": {"name": "hello.py", "content": "print('Hello AI OS')"},
      "risk": "low",
      "description": "Create Python script",
      "dependencies": []
    },
    {
      "id": 2,
      "action": "run_command",
      "params": {"cmd": "python sandbox/hello.py"},
      "risk": "high",
      "description": "Run the script",
      "dependencies": [1]
    }
  ]
}

Chat format (ONLY for greetings/questions with no actions needed):
{
  "type": "chat",
  "message": "Your actual response here."
}
"""


# ─── LLM-based planning (Ollama) ────────────────────────────────────────────

async def _try_ollama_plan(prompt: str) -> Union[Plan, ChatResponse, None]:
    """
    Attempt to get a valid plan from the local Ollama LLM.
    Returns None if Ollama is unavailable or returns invalid JSON.
    """
    data = {
        "model": MODEL_NAME,
        "prompt": f"{MEGAN_PERSONALITY}\n\nUser: {prompt}\n\nAssistant:",
        "stream": False,
        "format": "json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OLLAMA_URL, json=data, timeout=60.0)
            response.raise_for_status()
            result = response.json()
            content = result.get("response", "").strip()

            parsed = json.loads(content)

            if parsed.get("type") == "plan":
                plan = Plan(**parsed)
                # Validate that each action is a real tool name, not a placeholder
                valid_tools = {
                    "create_file", "read_file", "list_directory", "run_command",
                    "search_web", "get_weather", "deploy_app", "post_instagram",
                }
                for step in plan.steps:
                    if step.action not in valid_tools:
                        logging.warning(f"LLM produced invalid action '{step.action}', falling back to smart planner.")
                        return None
                return plan
            elif parsed.get("type") == "chat":
                return ChatResponse(message=parsed.get("message", "I'm not sure how to respond to that."))

    except Exception as e:
        logging.warning(f"Ollama unavailable or returned invalid JSON. Error: {e}")

    return None


# ─── MEGAN Smart Heuristic Planner (always works) ────────────────────────────

def _smart_plan(prompt: str) -> Union[Plan, ChatResponse]:
    """
    The MEGAN Smart Planner — a rule-based intent classifier that always
    produces a correct, executable Plan (or a ChatResponse for conversation).
    """
    from ..megan.smart_planner import generate_smart_plan
    from ..megan.intent_classifier import classify, ExecutionMode

    intent = classify(prompt)

    if intent.mode == ExecutionMode.CONVERSATION:
        # Conversation — return a helpful chat response
        task_type = intent.task_type
        if task_type == "greeting":
            return ChatResponse(
                message="Hello! I'm MEGAN — your autonomous AI operating system. I'm ready to execute tasks, build tools, research topics, and automate your workflow. What shall we accomplish today?"
            )
        if task_type == "help":
            return ChatResponse(
                message=(
                    "I'm MEGAN. Here's what I can do:\n"
                    "• **Create files** — 'Create a Python script that prints Hello'\n"
                    "• **Read files** — 'Read hello.py'\n"
                    "• **List files** — 'List files in my directory'\n"
                    "• **Run commands** — 'Check my Python version'\n"
                    "• **Search the web** — 'Search for latest AI news'\n"
                    "• **Weather** — 'What's the weather in New York?'\n"
                    "• **Instagram** — 'Post to Instagram with caption Working on AI OS'\n"
                    "• **Deploy** — 'Deploy the app'\n"
                    "• **Research** — 'Research eye health and save a report'\n"
                    "• **Build tools** — 'Create a new tool that gets the time'\n"
                    "\nJust tell me what you need and I'll execute it autonomously."
                )
            )
        # Generic question
        return ChatResponse(
            message=f"Understood. I'm MEGAN — processing: '{prompt}'. If you'd like me to take action, give me a concrete task and I'll execute it immediately."
        )

    # All other modes → generate a plan
    plan = generate_smart_plan(prompt)
    return plan


# ─── Public API ──────────────────────────────────────────────────────────────

async def generate_plan(prompt: str) -> Union[Plan, ChatResponse]:
    """
    MEGAN Planning Pipeline — Three-pass strategy:
    1. Smart Planner: For high-confidence, well-known intents (fast, always correct).
    2. Ollama LLM: For ambiguous/complex intents that need reasoning.
    3. Smart Planner fallback: If Ollama fails or hallucinates.
    """
    from ..engine.megan.intent_classifier import classify, ExecutionMode
    from ..engine.megan.smart_planner import generate_smart_plan

    intent = classify(prompt)
    logging.info(f"MEGAN Intent: mode={intent.mode} task={intent.task_type} confidence={intent.confidence:.2f}")

    # Pass 1: High-confidence execution intents → Smart Planner (always correct)
    if intent.confidence >= 0.8 and intent.mode in (
        ExecutionMode.EXECUTION, ExecutionMode.RESEARCH, ExecutionMode.BUILDER
    ):
        logging.info("Using MEGAN Smart Planner (high confidence).")
        return generate_smart_plan(prompt)

    # Pass 1b: Clear conversation intents → direct response
    if intent.mode == ExecutionMode.CONVERSATION and intent.confidence >= 0.8:
        return _smart_plan(prompt)

    # Pass 2: Try Ollama for ambiguous intents
    llm_result = await _try_ollama_plan(prompt)
    if llm_result is not None:
        return llm_result

    # Pass 3: Smart Planner fallback
    logging.info("Using MEGAN Smart Planner (fallback).")
    return _smart_plan(prompt)
