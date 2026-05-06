"""
MEGAN Intent Classifier
=======================
Classifies user prompts into one of MEGAN's execution modes without needing an LLM.
Returns both a mode and a structured intent that the smart planner can act on.
"""
import re
from typing import Dict, Any, Tuple
from dataclasses import dataclass

class ExecutionMode:
    CONVERSATION = "conversation"
    EXECUTION    = "execution"
    BUILDER      = "builder"
    AUTONOMOUS   = "autonomous"
    RESEARCH     = "research"

@dataclass
class Intent:
    mode: str
    task_type: str      # fine-grained type: create_file, read_file, run_command, etc.
    entities: Dict[str, Any]  # extracted values like filename, command, location, etc.
    raw_prompt: str
    confidence: float   # 0-1

# ──────────────────────────────────────────────
# Pattern sets — order matters (most specific first)
# ──────────────────────────────────────────────

_FILE_CREATE = [
    r"create\s+(?:a\s+)?(?:python\s+)?(?:script|file|document|txt|markdown|report)\s+(?:named?\s+)?['\"]?(?P<name>[\w\-\.\s]+?)['\"]?(?:\s+(?:with|that|and|containing|to)\s+(?:content|text|code|prints?|say)\s+['\"]?(?P<content>.+?)['\"]?)?$",
    r"write\s+(?:a\s+)?(?:file|script)\s+(?:called?\s+|named?\s+)?['\"]?(?P<name>[\w\-\.\s]+?)['\"]?",
    r"(?:make|generate|produce)\s+(?:a\s+)?(?:file|script)\s+(?:named?\s+)?['\"]?(?P<name>[\w\-\.\s]+?)['\"]?",
    r"save\s+(?:a?\s*file|report|document)\s+(?:called?\s+|named?\s+|as\s+)?['\"]?(?P<name>[\w\-\.\s]+?)['\"]?",
]

_FILE_READ = [
    r"read\s+(?:the\s+)?(?:contents?\s+of\s+|file\s+)?['\"]?(?P<name>[\w\-\.\s/]+\.\w+)['\"]?",
    r"open\s+(?:the\s+)?(?:file\s+)?['\"]?(?P<name>[\w\-\.\s/]+\.\w+)['\"]?",
    r"show\s+(?:me\s+)?(?:the\s+)?(?:contents?\s+of\s+)?['\"]?(?P<name>[\w\-\.\s/]+\.\w+)['\"]?",
    r"print\s+(?:the\s+)?(?:contents?\s+of\s+)?['\"]?(?P<name>[\w\-\.\s/]+\.\w+)['\"]?",
    r"display\s+(?:the\s+)?(?:contents?\s+of\s+)?['\"]?(?P<name>[\w\-\.\s/]+\.\w+)['\"]?",
    r"view\s+(?:the\s+)?(?:file\s+)?['\"]?(?P<name>[\w\-\.\s/]+\.\w+)['\"]?",
    r"what(?:'s|\s+is)\s+in\s+(?:the\s+)?(?:file\s+)?['\"]?(?P<name>[\w\-\.\s/]+\.\w+)['\"]?",
]

_LIST_DIR = [
    r"list\s+(?:all\s+)?(?:the\s+)?files?",
    r"show\s+(?:all\s+)?(?:the\s+)?files?",
    r"what(?:'s|\s+files?\s+are)\s+in\s+(?:my\s+)?(?:directory|folder|sandbox|workspace)",
    r"ls\b",
    r"dir\b",
]

_RUN_COMMAND_PATTERNS = [
    (r"(?:check|show|get)\s+(?:my\s+)?(?:python|py)\s+version", "python --version"),
    (r"(?:check|show|get)\s+(?:my\s+)?(?:node|nodejs|node\.js)\s+version", "node -v"),
    (r"(?:check|show|get)\s+(?:my\s+)?npm\s+version", "npm --version"),
    (r"(?:check|show|get)\s+(?:my\s+)?git\s+(?:status|log)", "git status"),
    (r"(?:show|get|check)\s+(?:the\s+)?(?:date|time)\b", "date"),
    (r"(?:who\s+am\s+i|current\s+user|whoami)", "whoami"),
    (r"(?:system\s+info|uname)", "uname -a"),
    (r"(?:run|execute)\s+(?:the\s+)?(?:command\s+)?['\"]?(?P<cmd>(?:ls|dir|echo|pwd|git|npm|python|pip|node|date|whoami|uname)[^'\"]*)['\"]?", None),
]

_SEARCH_WEB = [
    r"(?:search|look\s+up|google|find|research)\s+(?:the\s+)?(?:web\s+for\s+|for\s+|about\s+|online\s+for\s+)?(?:the\s+)?(?:latest\s+)?(?P<query>.+)",
    r"what(?:'s|\s+is)\s+(?:the\s+)?(?:latest|current)\s+(?:news|info|information|update)\s+(?:on|about|regarding)\s+(?P<query>.+)",
]

_GET_WEATHER = [
    r"(?:what(?:'s|\s+is)|how(?:'s|\s+is)|get|check|tell\s+me)\s+(?:the\s+)?weather(?:\s+like)?\s+(?:in|at|for)\s+(?P<location>.+)",
    r"(?:what(?:'s|\s+is)|how(?:'s|\s+is))\s+it\s+(?:like|going)\s+(?:outside|weather)\s+in\s+(?P<location>.+)",
    r"weather\s+in\s+(?P<location>.+)",
]

_INSTAGRAM = [
    r"post\s+(?:a\s+)?(?:photo|image|picture|pic)?\s*(?:to\s+)?instagram\s+(?:with\s+(?:the\s+)?caption\s+)?['\"]?(?P<caption>.+?)['\"]?$",
    r"(?:share|upload)\s+(?:to\s+)?instagram\s+['\"]?(?P<caption>.+?)['\"]?",
    r"instagram\s+post\s+['\"]?(?P<caption>.+?)['\"]?",
]

_DEPLOY = [
    r"deploy\s+(?:the\s+)?(?:app|application|website|site)",
    r"push\s+to\s+(?:production|prod|cloud|heroku|vercel|netlify)",
    r"launch\s+(?:the\s+)?(?:app|application|website|site)",
    r"release\s+(?:the\s+)?(?:app|version)",
]

_RESEARCH = [
    r"research\s+(?P<topic>.+)",
    r"(?:give\s+me|create|generate|write)\s+(?:a\s+)?(?:detailed\s+)?(?:report|summary|analysis)\s+(?:on|about|of|regarding)\s+(?P<topic>.+)",
    r"(?:study|explore|investigate)\s+(?P<topic>.+)",
    r"(?:collect|gather|compile)\s+(?:information|data|info)\s+(?:on|about|regarding)\s+(?P<topic>.+)",
]

_BUILDER = [
    r"(?:create|build|generate|add|make)\s+(?:a\s+)?(?:new\s+)?(?:tool|plugin|agent|module|capability|feature|function)\s+(?:that\s+|to\s+|for\s+|which\s+)?(?P<description>.+)",
    r"(?:i\s+need|i\s+want)\s+(?:a\s+)?(?:new\s+)?(?:tool|plugin|agent|module|capability)\s+(?:that\s+|to\s+|for\s+|which\s+)?(?P<description>.+)",
    r"extend\s+(?:yourself|your\s+capabilities?|megan)\s+(?:to\s+|with\s+)?(?P<description>.+)",
    r"teach\s+(?:yourself|megan)\s+(?:how\s+to\s+)?(?P<description>.+)",
]

_GREETING = [
    r"^(?:hello|hi|hey|howdy|greetings|good\s+(?:morning|afternoon|evening)|sup|what'?s\s+up)\b",
    r"^(?:how\s+are\s+you|how\s+do\s+you\s+do)\b",
]

_HELP = [
    r"^(?:help|what\s+can\s+you\s+do|what\s+are\s+your\s+capabilities|what\s+tools)",
]

_PYTHON_SCRIPT_AND_RUN = [
    r"create\s+(?:a\s+)?python\s+script\s+that\s+(?P<description>.+?)\s+and\s+run\s+(?:it|the\s+script)",
    r"(?:write|make|generate)\s+(?:a\s+)?python\s+(?:script|file)\s+(?:that\s+|to\s+)(?P<description>.+?)\s+(?:and\s+run|then\s+run|and\s+execute)\s+(?:it|the\s+script)",
]


def classify(prompt: str) -> Intent:
    """
    Classify a user prompt into a structured MEGAN Intent.
    """
    text = prompt.strip()
    lower = text.lower()

    # 1. Python script + run
    for pat in _PYTHON_SCRIPT_AND_RUN:
        m = re.search(pat, lower, re.IGNORECASE)
        if m:
            desc = m.group("description") if "description" in m.groupdict() else "print('Hello')"
            # Map description to actual code
            code = _desc_to_python_code(desc)
            filename = "script.py"
            return Intent(
                mode=ExecutionMode.EXECUTION,
                task_type="python_script_and_run",
                entities={"name": filename, "content": code, "cmd": f"python sandbox/{filename}"},
                raw_prompt=text,
                confidence=0.95,
            )

    # 2. Research
    for pat in _RESEARCH:
        m = re.search(pat, lower, re.IGNORECASE)
        if m:
            topic = m.group("topic") if "topic" in m.groupdict() else lower
            return Intent(
                mode=ExecutionMode.RESEARCH,
                task_type="research",
                entities={"topic": topic.strip(), "query": topic.strip()},
                raw_prompt=text,
                confidence=0.9,
            )

    # 3. Builder / self-upgrade
    for pat in _BUILDER:
        m = re.search(pat, lower, re.IGNORECASE)
        if m:
            desc = m.group("description") if "description" in m.groupdict() else ""
            return Intent(
                mode=ExecutionMode.BUILDER,
                task_type="build_tool",
                entities={"description": desc.strip()},
                raw_prompt=text,
                confidence=0.88,
            )

    # 4. File create
    for pat in _FILE_CREATE:
        m = re.search(pat, lower, re.IGNORECASE)
        if m:
            name = (m.group("name") if "name" in m.groupdict() and m.group("name") else "new_file.txt").strip()
            content = (m.group("content") if "content" in m.groupdict() and m.group("content") else "").strip()
            if not content:
                content = _infer_file_content(lower, name)
            return Intent(
                mode=ExecutionMode.EXECUTION,
                task_type="create_file",
                entities={"name": name, "content": content},
                raw_prompt=text,
                confidence=0.9,
            )

    # 5. File read
    for pat in _FILE_READ:
        m = re.search(pat, lower, re.IGNORECASE)
        if m:
            name = (m.group("name") if "name" in m.groupdict() and m.group("name") else "").strip()
            return Intent(
                mode=ExecutionMode.EXECUTION,
                task_type="read_file",
                entities={"name": name or "file.txt"},
                raw_prompt=text,
                confidence=0.9,
            )

    # 6. List directory
    for pat in _LIST_DIR:
        if re.search(pat, lower, re.IGNORECASE):
            return Intent(
                mode=ExecutionMode.EXECUTION,
                task_type="list_directory",
                entities={},
                raw_prompt=text,
                confidence=0.9,
            )

    # 7. Weather
    for pat in _GET_WEATHER:
        m = re.search(pat, lower, re.IGNORECASE)
        if m:
            location = (m.group("location") if "location" in m.groupdict() and m.group("location") else "").strip()
            return Intent(
                mode=ExecutionMode.EXECUTION,
                task_type="get_weather",
                entities={"location": location or "your city"},
                raw_prompt=text,
                confidence=0.9,
            )

    # 8. Instagram
    for pat in _INSTAGRAM:
        m = re.search(pat, lower, re.IGNORECASE)
        if m:
            caption = (m.group("caption") if "caption" in m.groupdict() and m.group("caption") else text).strip()
            return Intent(
                mode=ExecutionMode.EXECUTION,
                task_type="post_instagram",
                entities={"caption": caption, "image_url": ""},
                raw_prompt=text,
                confidence=0.9,
            )

    # 9. Deploy
    for pat in _DEPLOY:
        if re.search(pat, lower, re.IGNORECASE):
            return Intent(
                mode=ExecutionMode.EXECUTION,
                task_type="deploy_app",
                entities={},
                raw_prompt=text,
                confidence=0.9,
            )

    # 10. Run command
    for pat, default_cmd in _RUN_COMMAND_PATTERNS:
        m = re.search(pat, lower, re.IGNORECASE)
        if m:
            if default_cmd:
                cmd = default_cmd
            else:
                cmd = m.group("cmd").strip() if "cmd" in m.groupdict() and m.group("cmd") else "ls"
            return Intent(
                mode=ExecutionMode.EXECUTION,
                task_type="run_command",
                entities={"cmd": cmd},
                raw_prompt=text,
                confidence=0.85,
            )

    # 11. Multi-step: list + python version
    if ("list" in lower or "files" in lower) and ("python" in lower and "version" in lower):
        return Intent(
            mode=ExecutionMode.EXECUTION,
            task_type="multi_step",
            entities={"steps": ["list_directory", "run_command_python_version"]},
            raw_prompt=text,
            confidence=0.85,
        )

    # 12. Search web
    for pat in _SEARCH_WEB:
        m = re.search(pat, lower, re.IGNORECASE)
        if m:
            query = (m.group("query") if "query" in m.groupdict() and m.group("query") else text).strip()
            # Remove trailing question marks / filler
            query = re.sub(r'\s*\?$', '', query).strip()
            return Intent(
                mode=ExecutionMode.EXECUTION,
                task_type="search_web",
                entities={"query": query},
                raw_prompt=text,
                confidence=0.85,
            )

    # 13. Greeting
    for pat in _GREETING:
        if re.search(pat, lower, re.IGNORECASE):
            return Intent(
                mode=ExecutionMode.CONVERSATION,
                task_type="greeting",
                entities={},
                raw_prompt=text,
                confidence=0.95,
            )

    # 14. Help
    for pat in _HELP:
        if re.search(pat, lower, re.IGNORECASE):
            return Intent(
                mode=ExecutionMode.CONVERSATION,
                task_type="help",
                entities={},
                raw_prompt=text,
                confidence=0.95,
            )

    # 15. Generic question (likely conversation)
    question_words = ["what", "who", "where", "when", "why", "how", "is", "are", "can", "does", "do", "will", "would", "could", "should"]
    if any(lower.startswith(w) for w in question_words) and "?" in text:
        return Intent(
            mode=ExecutionMode.CONVERSATION,
            task_type="question",
            entities={},
            raw_prompt=text,
            confidence=0.7,
        )

    # Default: treat as conversation
    return Intent(
        mode=ExecutionMode.CONVERSATION,
        task_type="unknown",
        entities={},
        raw_prompt=text,
        confidence=0.4,
    )


def _desc_to_python_code(description: str) -> str:
    """Turn a natural language description into basic Python code."""
    desc_lower = description.lower()
    if "hello" in desc_lower:
        msg = "Hello AI OS" if "ai os" in desc_lower else "Hello World"
        return f"print('{msg}')"
    if "fibonacci" in desc_lower:
        return "a, b = 0, 1\nfor _ in range(10):\n    print(a)\n    a, b = b, a + b"
    if "factorial" in desc_lower:
        return "import math\nprint(math.factorial(10))"
    if "date" in desc_lower or "time" in desc_lower:
        return "from datetime import datetime\nprint(datetime.now())"
    return f"# Task: {description}\nprint('Task executed successfully')"


def _infer_file_content(lower: str, name: str) -> str:
    """Infer content based on filename and prompt context."""
    ext = name.rsplit(".", 1)[-1] if "." in name else "txt"
    if ext == "py":
        return "# Auto-generated Python script\nprint('Hello from MEGAN!')"
    if ext in ("md", "markdown"):
        return f"# {name.replace('.md', '').replace('-', ' ').title()}\n\nAuto-generated by MEGAN AI OS.\n"
    if ext in ("html", "htm"):
        return "<html><body><h1>Hello from MEGAN!</h1></body></html>"
    if ext == "json":
        return '{"generated_by": "MEGAN AI OS", "content": "auto-generated"}'
    return f"Content generated by MEGAN AI OS for: {name}"
