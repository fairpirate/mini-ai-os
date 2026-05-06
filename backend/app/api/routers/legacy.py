from fastapi import APIRouter, HTTPException
import asyncio
import uuid
import time
import os

from ...models.schemas import Task, TaskStatus, Union, ChatResponse
from ...planner.planner import generate_plan
from ...engine.executor import add_task, get_all_tasks, get_task, execute_task
from ...tools.implementations import registry
from ...core.logging import logger

router = APIRouter()

@router.post("/plan", response_model=Union[Task, ChatResponse])
async def create_plan(request: dict):
    user_prompt = request.get("prompt")
    if not user_prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    ai_response = await generate_plan(user_prompt)
    
    if isinstance(ai_response, ChatResponse):
        return ai_response
    
    # It's a plan, create a task
    task_id = str(uuid.uuid4())
    task = Task(
        id=task_id,
        status=TaskStatus.PENDING,
        plan=ai_response,
        created_at=time.time(),
        updated_at=time.time()
    )
    add_task(task)
    logger.info(f"Task created: {task_id} with {len(ai_response.steps)} steps")
    return task

@router.post("/approve/{task_id}")
async def approve_task(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != TaskStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Task is in status {task.status}")
    
    task.status = TaskStatus.APPROVED
    task.updated_at = time.time()
    
    # Schedule async execution on the running event loop
    asyncio.create_task(execute_task(task_id))
    logger.info(f"Task {task_id} approved and execution scheduled.")
    
    return {"message": "Task approved and execution started.", "task_id": task_id}

@router.get("/tasks")
async def list_tasks():
    return get_all_tasks()

@router.get("/tasks/{task_id}")
async def fetch_task(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/tools")
async def list_available_tools():
    return registry.list_tools()

@router.get("/files")
async def list_files():
    sandbox_dir = "sandbox"
    if not os.path.exists(sandbox_dir):
        return []
    
    files = []
    for filename in os.listdir(sandbox_dir):
        path = os.path.join(sandbox_dir, filename)
        if os.path.isfile(path):
            files.append({
                "name": filename,
                "size": os.path.getsize(path),
                "modified_at": os.path.getmtime(path)
            })
    return files
