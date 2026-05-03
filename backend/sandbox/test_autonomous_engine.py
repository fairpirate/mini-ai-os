import asyncio
import sys
import os
import time

# Add backend to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.schemas import Task, TaskStatus, Plan, Step, RiskLevel
from app.engine.executor import execute_task, add_task, tasks_db

# Create mock async tool to test the executor
from app.engine.tools.base import AsyncTool
from app.engine.tools.registry import tool_registry
from pydantic import BaseModel

class MockParams(BaseModel):
    fail_first: bool = False

class MockTool(AsyncTool):
    name = "mock_tool"
    description = "A mock tool for testing."
    risk_level = RiskLevel.LOW
    schema = MockParams
    
    def __init__(self):
        self.call_count = 0

    async def execute(self, params: dict) -> str:
        self.call_count += 1
        await asyncio.sleep(0.5) # Simulate long running task
        if params.get("fail_first") and self.call_count == 1:
            raise Exception("Simulated failure on first try!")
        return f"Mock tool executed successfully on attempt {self.call_count}"

# Register mock tool
mock = MockTool()
tool_registry._tools["mock_tool"] = mock # Force inject

async def main():
    print("Testing Autonomous Engine...")
    
    # Create a plan with dependencies and simulated failure
    plan = Plan(
        type="plan",
        steps=[
            Step(
                id=1,
                action="mock_tool",
                params={"fail_first": False},
                risk=RiskLevel.LOW,
                description="Step 1: No dependencies",
                dependencies=[]
            ),
            Step(
                id=2,
                action="mock_tool",
                params={"fail_first": True}, # This will fail once, then retry
                risk=RiskLevel.LOW,
                description="Step 2: Depends on Step 1. Fails once.",
                dependencies=[1],
                max_retries=3
            ),
            Step(
                id=3,
                action="mock_tool",
                params={"fail_first": False},
                risk=RiskLevel.LOW,
                description="Step 3: Depends on Step 2",
                dependencies=[2]
            )
        ]
    )
    
    task = Task(
        id="test_task_1",
        status=TaskStatus.PENDING,
        plan=plan,
        created_at=time.time(),
        updated_at=time.time()
    )
    
    add_task(task)
    
    print("Starting execution loop...")
    await execute_task("test_task_1")
    
    print("\nFinal Task Status:", tasks_db["test_task_1"].status)
    for result in tasks_db["test_task_1"].results:
        print(f"Result for step {result['step_id']}: {result['status']} -> {result['output']}")

if __name__ == "__main__":
    asyncio.run(main())
