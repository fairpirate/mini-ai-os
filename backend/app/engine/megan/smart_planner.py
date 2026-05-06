"""
MEGAN Smart Planner
===================
Converts a classified Intent into a valid Plan object with correct steps,
parameters, risk levels, and dependencies.

This runs as the definitive fallback when the Ollama LLM fails to produce
a valid JSON plan, ensuring MEGAN ALWAYS executes tasks correctly.
"""
from typing import List, Dict, Any
from ...models.schemas import Plan, Step, RiskLevel
from .intent_classifier import Intent, ExecutionMode, classify


def _step(
    sid: int,
    action: str,
    params: Dict[str, Any],
    risk: RiskLevel,
    description: str,
    dependencies: List[int] = None,
) -> Step:
    return Step(
        id=sid,
        action=action,
        params=params,
        risk=risk,
        description=description,
        dependencies=dependencies or [],
    )


def generate_smart_plan(prompt: str) -> Plan:
    """
    Main entry point — classify the prompt and build a Plan.
    """
    intent = classify(prompt)
    return _intent_to_plan(intent)


def _intent_to_plan(intent: Intent) -> Plan:
    t = intent.task_type
    e = intent.entities

    # ── Python script + run ──────────────────────────────────────────────
    if t == "python_script_and_run":
        name = e.get("name", "script.py")
        content = e.get("content", "print('Hello AI OS')")
        cmd = f"python sandbox/{name}"
        return Plan(steps=[
            _step(1, "create_file", {"name": name, "content": content},
                  RiskLevel.LOW, f"Create Python script '{name}'"),
            _step(2, "run_command",  {"cmd": cmd},
                  RiskLevel.HIGH, f"Execute '{cmd}'", [1]),
        ])

    # ── File create ─────────────────────────────────────────────────────
    if t == "create_file":
        return Plan(steps=[
            _step(1, "create_file",
                  {"name": e.get("name", "file.txt"), "content": e.get("content", "")},
                  RiskLevel.LOW, f"Create file '{e.get('name', 'file.txt')}'"),
        ])

    # ── File read ───────────────────────────────────────────────────────
    if t == "read_file":
        return Plan(steps=[
            _step(1, "read_file", {"name": e.get("name", "file.txt")},
                  RiskLevel.LOW, f"Read contents of '{e.get('name', 'file.txt')}'"),
        ])

    # ── List directory ──────────────────────────────────────────────────
    if t == "list_directory":
        return Plan(steps=[
            _step(1, "list_directory", {}, RiskLevel.LOW, "List all files in sandbox directory"),
        ])

    # ── Multi-step (list + python version) ───────────────────────────────
    if t == "multi_step":
        return Plan(steps=[
            _step(1, "list_directory", {}, RiskLevel.LOW, "List files in sandbox"),
            _step(2, "run_command",  {"cmd": "python --version"},
                  RiskLevel.HIGH, "Check Python version", [1]),
        ])

    # ── Run command ──────────────────────────────────────────────────────
    if t == "run_command":
        cmd = e.get("cmd", "ls")
        return Plan(steps=[
            _step(1, "run_command", {"cmd": cmd}, RiskLevel.HIGH, f"Run shell command: {cmd}"),
        ])

    # ── Search web ──────────────────────────────────────────────────────
    if t == "search_web":
        query = e.get("query", "AI latest news")
        report_name = f"research_{query[:30].replace(' ', '_').lower()}.md"
        return Plan(steps=[
            _step(1, "search_web",  {"query": query},
                  RiskLevel.LOW, f"Search the web for: {query}"),
            _step(2, "create_file",
                  {"name": report_name, "content": f"# Search: {query}\n\n(Results will be inserted by execution engine)"},
                  RiskLevel.LOW, "Save search results to file", [1]),
        ])

    # ── Get weather ─────────────────────────────────────────────────────
    if t == "get_weather":
        loc = e.get("location", "your city")
        return Plan(steps=[
            _step(1, "get_weather", {"location": loc},
                  RiskLevel.LOW, f"Get current weather in {loc}"),
        ])

    # ── Post instagram ──────────────────────────────────────────────────
    if t == "post_instagram":
        return Plan(steps=[
            _step(1, "post_instagram",
                  {"caption": e.get("caption", ""), "image_url": e.get("image_url", "")},
                  RiskLevel.MEDIUM, f"Post to Instagram: '{e.get('caption', '')[:40]}'"),
        ])

    # ── Deploy ──────────────────────────────────────────────────────────
    if t == "deploy_app":
        return Plan(steps=[
            _step(1, "deploy_app", {}, RiskLevel.HIGH, "Deploy application to cloud"),
        ])

    # ── Research ────────────────────────────────────────────────────────
    if t == "research":
        topic = e.get("topic", e.get("query", "the topic"))
        query = e.get("query", topic)
        report_name = f"research_{topic[:30].replace(' ', '_').lower()}.md"
        return Plan(steps=[
            _step(1, "search_web",  {"query": f"{query} research latest findings"},
                  RiskLevel.LOW, f"Search web for research on: {topic}"),
            _step(2, "search_web",  {"query": f"{query} guide facts overview"},
                  RiskLevel.LOW, f"Search secondary sources on: {topic}"),
            _step(3, "create_file",
                  {"name": report_name,
                   "content": _generate_report_template(topic)},
                  RiskLevel.LOW, f"Save research report as '{report_name}'", [1, 2]),
        ])

    # ── Builder ─────────────────────────────────────────────────────────
    if t == "build_tool":
        desc = e.get("description", "new capability")
        plugin_name = "custom_tool.py"
        code = _generate_plugin_stub(desc)
        return Plan(steps=[
            _step(1, "create_file",
                  {"name": f"plugins/{plugin_name}", "content": code},
                  RiskLevel.MEDIUM, f"Generate plugin code for: {desc}"),
        ])

    # ── Fallback: create a note about the task ──────────────────────────
    return Plan(steps=[
        _step(1, "create_file",
              {"name": "megan_task.txt", "content": f"MEGAN Task Log\n==============\nTask: {intent.raw_prompt}\nStatus: Queued for processing\n"},
              RiskLevel.LOW, "Log task for MEGAN processing"),
    ])


def _generate_report_template(topic: str) -> str:
    return f"""# Research Report: {topic.title()}
Generated by MEGAN AI OS
========================

## Executive Summary
Research on: {topic}

## Key Findings
(Search results will be compiled here)

## Sources
(Citations will be added automatically)

## Conclusion
MEGAN has collected and structured research on {topic}.
"""


def _generate_plugin_stub(description: str) -> str:
    func_name = description.replace(" ", "_").lower()[:30]
    class_name = "".join(w.capitalize() for w in description.split()[:3]) + "Tool"
    return f'''"""
Auto-generated MEGAN Plugin
Description: {description}
"""
import asyncio
from pydantic import BaseModel, Field
from typing import Dict, Any
from ...engine.tools.base import AsyncTool, RiskLevel


class {class_name}Schema(BaseModel):
    input: str = Field(..., description="Input for {description}")


class {class_name}(AsyncTool):
    name = "{func_name}"
    description = "{description}"
    risk_level = RiskLevel.LOW
    schema = {class_name}Schema

    async def execute(self, params: Dict[str, Any]) -> str:
        # TODO: Implement actual logic for: {description}
        return f"Executed: {description} with input: {{params.get('input', '')}}"


def register_tools(registry):
    registry.register({class_name}())
'''
