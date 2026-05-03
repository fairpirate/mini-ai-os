from fastapi import APIRouter
from pydantic import BaseModel
from ...core.config import settings
from ...engine.queue import task_manager

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str
    active_tasks: int

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check endpoint."""
    return HealthResponse(
        status="online",
        version=settings.VERSION,
        active_tasks=len([t for t, s in task_manager.active_tasks.items() if s == "running"])
    )

@router.get("/status")
async def system_status():
    """Returns general status and config."""
    return {
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "model": settings.MODEL_NAME,
        "queue_size": task_manager.queue.qsize()
    }
