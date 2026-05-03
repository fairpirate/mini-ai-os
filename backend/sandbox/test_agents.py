import asyncio
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.engine.agents.runner import run_agentic_workflow

async def main():
    print("Testing Multi-Agent Workflow...")
    prompt = "I need you to research LangGraph, write a simple script for it, and then check the code."
    
    async for output in run_agentic_workflow(prompt):
        print(output, end="")

if __name__ == "__main__":
    asyncio.run(main())
