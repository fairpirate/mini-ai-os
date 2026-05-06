import logging
import time
import asyncio
from typing import List, Dict, Any, Set
from ..models.schemas import Task, TaskStatus, Step
from .tools.registry import tool_registry
from ..core.logging import logger

# In-memory storage for MVP
tasks_db: Dict[str, Task] = {}

async def _broadcast_task_update(task: Task):
    """Broadcasts a task snapshot to all connected WebSocket clients."""
    try:
        from ..ws.manager import manager
        payload = {
            "id": task.id,
            "status": task.status.value,
            "plan": {
                "steps": [
                    {
                        "id": s.id,
                        "action": s.action,
                        "description": s.description,
                        "status": s.status.value,
                        "attempts": s.attempts,
                    }
                    for s in task.plan.steps
                ]
            },
            "results": task.results,
        }
        await manager.broadcast({"event": "task_update", "payload": payload})
    except Exception as e:
        logger.warning(f"Failed to broadcast task update: {e}")

async def execute_task(task_id: str):
    """
    Autonomous execution engine with dependency analysis, retries, and HITL support.
    """
    task = tasks_db.get(task_id)
    if not task:
        return

    task.status = TaskStatus.EXECUTING
    task.updated_at = time.time()
    task.results = []

    # Broadcast that execution has started
    await _broadcast_task_update(task)

    # Map step IDs for quick access
    steps_map: Dict[int, Step] = {s.id: s for s in task.plan.steps}
    
    # Execution state tracking
    completed_steps: Set[int] = set()
    failed_steps: Set[int] = set()
    running_steps: Set[int] = set()
    
    logger.info(f"Starting autonomous execution for task {task_id}")

    while True:
        progress_made = False
        
        for step in task.plan.steps:
            if step.id in completed_steps or step.id in failed_steps or step.id in running_steps:
                continue

            # Check dependencies, ignoring any that don't exist in the plan to handle LLM hallucinations
            valid_deps = [dep for dep in step.dependencies if dep in steps_map]
            deps_met = all(dep in completed_steps for dep in valid_deps)
            
            if deps_met:
                running_steps.add(step.id)
                progress_made = True
                
                # Execute step (in a real system, we'd spawn asyncio.create_task here for parallelism)
                # For safety and predictable logging in this engine, we run sequentially among unblocked
                step.status = TaskStatus.EXECUTING
                
                tool = tool_registry.get_tool(step.action)
                step_result = {
                    "step_id": step.id,
                    "action": step.action,
                    "status": "success",
                    "output": ""
                }

                if not tool:
                    step.error_message = f"Tool '{step.action}' not found."
                    step.status = TaskStatus.FAILED
                    
                elif not tool.validate_params(step.params):
                    step.error_message = f"Validation failed for tool '{step.action}'."
                    step.status = TaskStatus.FAILED
                    
                else:
                    try:
                        # CRITICAL FIX: Awaiting the async tool execution
                        logger.info(f"Executing step {step.id} via {step.action}")
                        output = await tool.execute(step.params)
                        step_result["output"] = output
                        step.status = TaskStatus.COMPLETED
                    except Exception as e:
                        logger.error(f"Error in step {step.id}: {e}", exc_info=True)
                        step.error_message = str(e)
                        step.status = TaskStatus.FAILED

                # Handle Retries and State
                if step.status == TaskStatus.FAILED:
                    step.attempts += 1
                    if step.attempts < step.max_retries:
                        logger.warning(f"Step {step.id} failed. Retrying ({step.attempts}/{step.max_retries})...")
                        step.status = TaskStatus.PENDING
                        running_steps.remove(step.id)
                    else:
                        logger.error(f"Step {step.id} failed after {step.max_retries} attempts. Escalating.")
                        failed_steps.add(step.id)
                        running_steps.remove(step.id)
                        step_result["status"] = "error"
                        step_result["output"] = step.error_message
                        task.results.append(step_result)
                else:
                    completed_steps.add(step.id)
                    running_steps.remove(step.id)
                    task.results.append(step_result)

                # Broadcast step-level update
                await _broadcast_task_update(task)
        
        # Check termination conditions
        if failed_steps:
            logger.error("Execution halted due to failed dependencies. Human intervention required.")
            task.status = TaskStatus.FAILED
            break
            
        if len(completed_steps) == len(task.plan.steps):
            logger.info("All steps completed successfully.")
            task.status = TaskStatus.COMPLETED
            break
            
        if not progress_made and not running_steps:
            logger.error("Deadlock detected: No steps can be executed. Check circular dependencies.")
            task.status = TaskStatus.FAILED
            break
            
        # Yield to event loop for long-running task support
        await asyncio.sleep(0.1)

    task.updated_at = time.time()
    logger.info(f"Task {task_id} execution finished with status {task.status}")
    # Final broadcast for terminal state
    await _broadcast_task_update(task)

def get_all_tasks() -> List[Task]:
    return list(tasks_db.values())

def get_task(task_id: str) -> Task:
    return tasks_db.get(task_id)

def add_task(task: Task):
    tasks_db[task.id] = task
