from typing import AsyncGenerator, Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage
from .orchestrator import agent_graph
from .state import AgentState
from ...core.logging import logger


async def run_agentic_workflow(
    prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
    client_id: Optional[str] = None,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Executes the LangGraph multi-agent workflow, yielding structured
    update dicts so the caller can stream them over WebSocket or stdout.

    Each yielded dict has shape:
        {"agent": str, "text": str, "done": bool}
    """
    messages = []
    if history:
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=prompt))

    initial_state: AgentState = {
        "messages": messages,
        "shared_memory": {},
        "task_queue": [],
        "current_task": None,
        "errors": [],
        "next_agent": "planner",
    }

    try:
        async for output in agent_graph.astream(initial_state, stream_mode="updates"):
            for node_name, state_update in output.items():
                logger.info(f"Agent '{node_name}' finished execution.")

                # Pull the last message this agent emitted, if any
                if "messages" in state_update and state_update["messages"]:
                    last_msg = state_update["messages"][-1].content
                else:
                    last_msg = "Task processed."

                yield {
                    "agent": node_name,
                    "text": last_msg,
                    "done": False,
                }

        # Signal completion
        yield {"agent": "system", "text": "", "done": True}

    except Exception as e:
        logger.error(f"Error in multi-agent workflow: {e}", exc_info=True)
        yield {"agent": "system", "text": f"[System Fault: {str(e)}]", "done": True}
