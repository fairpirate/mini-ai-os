import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .state import AgentState
from ..ollama import ai_service
from ..tools.registry import tool_registry

async def planner_agent(state: AgentState) -> Dict[str, Any]:
    """
    Analyzes the user's request and breaks it down into subtasks.
    """
    messages = state.get("messages", [])
    if not messages:
        return {"next_agent": "executor"}
        
    last_msg = messages[-1].content
    prompt = f"Break down this request into subtasks for a multi-agent system. Format as a JSON list of tasks. Request: {last_msg}"
    
    # We use ai_service directly
    response = await ai_service.send_prompt(prompt, mode="planner")
    
    try:
        # Assuming the model returns JSON
        tasks = json.loads(response)
        if isinstance(tasks, list):
            return {"task_queue": tasks, "next_agent": "executor"}
    except json.JSONDecodeError:
        # Fallback if not proper JSON
        return {"task_queue": [{"description": response}], "next_agent": "executor"}
    
    return {"next_agent": "executor"}

async def executor_agent(state: AgentState) -> Dict[str, Any]:
    """
    Executes the next task in the queue or delegates it.
    """
    queue = state.get("task_queue", [])
    if not queue:
        return {"next_agent": "END"}
        
    current_task = queue[0]
    # In a full implementation, we'd route based on task description.
    # For now, let's route everything through specific agents based on keywords
    # or just do basic execution.
    
    desc = current_task.get("description", "").lower()
    
    if "research" in desc or "search" in desc:
        return {"current_task": current_task, "next_agent": "research", "task_queue": queue[1:]}
    elif "code" in desc or "file" in desc:
        return {"current_task": current_task, "next_agent": "coding", "task_queue": queue[1:]}
    elif "vision" in desc or "image" in desc:
        return {"current_task": current_task, "next_agent": "vision", "task_queue": queue[1:]}
    elif "memory" in desc or "remember" in desc:
        return {"current_task": current_task, "next_agent": "memory", "task_queue": queue[1:]}
    
    # Generic execution
    prompt = f"Execute this task: {desc}"
    response = await ai_service.send_prompt(prompt, mode="jarvis")
    
    return {
        "messages": [AIMessage(content=response)],
        "task_queue": queue[1:], # Pop the task
        "next_agent": "executor" # Loop back
    }

async def research_agent(state: AgentState) -> Dict[str, Any]:
    """Handles research and browsing."""
    task = state.get("current_task", {}).get("description", "Research")
    prompt = f"Research the following: {task}"
    response = await ai_service.send_prompt(prompt, mode="jarvis")
    return {"messages": [AIMessage(content=f"Research output: {response}")], "next_agent": "executor"}

async def coding_agent(state: AgentState) -> Dict[str, Any]:
    """Handles coding tasks."""
    task = state.get("current_task", {}).get("description", "Code")
    prompt = f"Write code for: {task}"
    response = await ai_service.send_prompt(prompt, mode="coder")
    return {"messages": [AIMessage(content=f"Code output: {response}")], "next_agent": "executor"}

async def vision_agent(state: AgentState) -> Dict[str, Any]:
    """Handles image and vision tasks."""
    task = state.get("current_task", {}).get("description", "Analyze image")
    
    import os
    from ..plugins.vision_tools import TakeScreenshotTool, LocateUIElementTool
    from ..vision.service import vision_service
    from PIL import Image
    
    screenshot_tool = TakeScreenshotTool()
    locator_tool = LocateUIElementTool()
    
    tmp_img = os.path.join(os.path.dirname(__file__), "../../../sandbox/agent_screenshot.png")
    os.makedirs(os.path.dirname(tmp_img), exist_ok=True)
    
    screenshot_result = await screenshot_tool.execute({"save_path": tmp_img})
    if "Error" in screenshot_result:
        return {"messages": [AIMessage(content=f"Vision output: {screenshot_result}")], "next_agent": "executor"}
    
    task_lower = task.lower()
    
    if "find" in task_lower or "locate" in task_lower or "where" in task_lower:
        result = await locator_tool.execute({
            "image_path": tmp_img,
            "description": task,
            "annotate_output_path": os.path.join(os.path.dirname(tmp_img), "agent_annotated.png")
        })
    else:
        # General analysis: extract text and let the LLM reason
        try:
            if not os.path.exists(tmp_img):
                raise FileNotFoundError(f"Screenshot file not found at {tmp_img}")
                
            image = Image.open(tmp_img)
            text = vision_service.extract_text(image)
            prompt = f"The user asked: '{task}'. Here is the OCR text extracted from the current screen: {text}"
            result = await ai_service.send_prompt(prompt, mode="jarvis")
        except Exception as e:
            result = f"Error analyzing image: {str(e)}"
            
    return {"messages": [AIMessage(content=f"Vision output: {result}")], "next_agent": "executor"}

async def memory_agent(state: AgentState) -> Dict[str, Any]:
    """Handles long-term memory access (ChromaDB)."""
    task = state.get("current_task", {}).get("description", "Memory access")
    prompt = f"Retrieve/Store memory for: {task}"
    response = await ai_service.send_prompt(prompt, mode="jarvis")
    return {"messages": [AIMessage(content=f"Memory output: {response}")], "next_agent": "executor"}

async def security_agent(state: AgentState) -> Dict[str, Any]:
    """Reviews actions for security."""
    # This could run parallel to executor or as a pre-check
    task = state.get("current_task", {}).get("description", "Review task")
    prompt = f"Review this for security risks: {task}"
    response = await ai_service.send_prompt(prompt, mode="jarvis")
    # Store security clearance in shared memory
    return {"shared_memory": {"last_security_review": response}, "next_agent": "executor"}
