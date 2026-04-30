import logging
import time
from typing import List, Dict, Any
from ..models.schemas import Task, TaskStatus, Step
from ..tools.base import registry

# In-memory storage for MVP
tasks_db: Dict[str, Task] = {}

async def execute_task(task_id: str):
    task = tasks_db.get(task_id)
    if not task:
        return

    task.status = TaskStatus.EXECUTING
    task.updated_at = time.time()
    task.results = []

    for step in task.plan.steps:
        tool = registry.get_tool(step.action)
        step_result = {
            "step_id": step.id,
            "action": step.action,
            "status": "success",
            "output": ""
        }

        if not tool:
            step_result["status"] = "error"
            step_result["output"] = f"Tool '{step.action}' not found."
            task.results.append(step_result)
            break

        if not tool.validate(step.params):
            step_result["status"] = "error"
            step_result["output"] = f"Validation failed for tool '{step.action}'."
            task.results.append(step_result)
            break

        try:
            output = tool.execute(step.params)
            step_result["output"] = output
        except Exception as e:
            step_result["status"] = "error"
            step_result["output"] = str(e)
            task.results.append(step_result)
            break
        
        task.results.append(step_result)

    if all(res["status"] == "success" for res in task.results):
        task.status = TaskStatus.COMPLETED
    else:
        task.status = TaskStatus.FAILED
    
    task.updated_at = time.time()
    logging.info(f"Task {task_id} execution finished with status {task.status}")

def get_all_tasks() -> List[Task]:
    return list(tasks_db.values())

def get_task(task_id: str) -> Task:
    return tasks_db.get(task_id)

def add_task(task: Task):
    tasks_db[task.id] = task
