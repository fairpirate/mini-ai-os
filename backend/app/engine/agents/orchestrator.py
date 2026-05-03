from langgraph.graph import StateGraph, END
from typing import Literal
from .state import AgentState
from .nodes import (
    planner_agent,
    executor_agent,
    research_agent,
    coding_agent,
    vision_agent,
    memory_agent,
    security_agent
)

def route_next(state: AgentState) -> Literal["executor", "planner", "research", "coding", "vision", "memory", "security", "__end__"]:
    """
    Dynamically route based on the 'next_agent' state variable.
    """
    next_agent = state.get("next_agent", "END")
    if next_agent == "END":
        return END
    return next_agent

def build_graph() -> StateGraph:
    """
    Builds the multi-agent LangGraph workflow.
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", planner_agent)
    workflow.add_node("executor", executor_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("coding", coding_agent)
    workflow.add_node("vision", vision_agent)
    workflow.add_node("memory", memory_agent)
    workflow.add_node("security", security_agent)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Define conditional edges based on router
    agents = ["planner", "executor", "research", "coding", "vision", "memory", "security"]
    for agent in agents:
        workflow.add_conditional_edges(
            agent,
            route_next,
            {
                "executor": "executor",
                "planner": "planner",
                "research": "research",
                "coding": "coding",
                "vision": "vision",
                "memory": "memory",
                "security": "security",
                END: END
            }
        )
        
    return workflow

# Compile the graph
agent_graph = build_graph().compile()
