import asyncio
from typing import Callable, Any, Dict
from ..core.logging import logger

class BackgroundTaskManager:
    """Manages an async queue for executing AI tasks and background operations."""
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_running = False
        self._worker_task = None
        self.active_tasks: Dict[str, str] = {}

    async def start(self):
        """Starts the background worker loop."""
        self.is_running = True
        self._worker_task = asyncio.create_task(self._worker_loop())
        logger.info("Background Task Manager started.")

    async def stop(self):
        """Stops the background worker loop safely."""
        self.is_running = False
        if self._worker_task:
            self._worker_task.cancel()
        logger.info("Background Task Manager stopped.")

    async def add_task(self, task_id: str, func: Callable, *args, **kwargs):
        """Add a task to the execution queue."""
        await self.queue.put((task_id, func, args, kwargs))
        self.active_tasks[task_id] = "queued"
        logger.info(f"Task {task_id} queued.")

    async def _worker_loop(self):
        while self.is_running:
            try:
                task_id, func, args, kwargs = await self.queue.get()
                self.active_tasks[task_id] = "running"
                logger.info(f"Executing task {task_id}...")
                
                # Execute the function
                if asyncio.iscoroutinefunction(func):
                    await func(*args, **kwargs)
                else:
                    func(*args, **kwargs)
                    
                self.active_tasks[task_id] = "completed"
                logger.info(f"Task {task_id} completed.")
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.active_tasks[task_id] = "failed"
                logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)

task_manager = BackgroundTaskManager()
