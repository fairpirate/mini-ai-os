from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"

class Step(BaseModel):
    id: int
    action: str
    params: Dict[str, Any]
    risk: RiskLevel
    description: str

class Plan(BaseModel):
    type: str = "plan"
    steps: List[Step]

class ChatResponse(BaseModel):
    type: str = "chat"
    message: str

class Task(BaseModel):
    id: str
    status: TaskStatus
    plan: Plan
    results: List[Dict[str, Any]] = []
    created_at: float
    updated_at: float

class ApproveRequest(BaseModel):
    task_id: str
