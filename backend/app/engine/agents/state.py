from typing import Annotated, Dict, List, Any, Optional, TypedDict
from langchain_core.messages import BaseMessage
import operator

def append_messages(left: list[BaseMessage], right: list[BaseMessage]) -> list[BaseMessage]:
    return left + right

def update_dict(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    # Update dictionary, useful for shared memory
    left_copy = left.copy() if left else {}
    if right:
        left_copy.update(right)
    return left_copy

def extend_list(left: List[Any], right: List[Any]) -> List[Any]:
    if not left:
        left = []
    if not right:
        return left
    return left + right

class AgentState(TypedDict):
    """
    Represents the shared state of the multi-agent system in LangGraph.
    """
    # Communication and message history
    messages: Annotated[List[BaseMessage], append_messages]
    
    # Cross-agent shared memory
    shared_memory: Annotated[Dict[str, Any], update_dict]
    
    # Task delegation and prioritization queue
    task_queue: Annotated[List[Dict[str, Any]], extend_list]
    
    # Current task being processed
    current_task: Optional[Dict[str, Any]]
    
    # Error tracking for retry logic
    errors: Annotated[List[str], extend_list]
    
    # Current agent assigned to the next step
    next_agent: str
