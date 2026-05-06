import requests
import time
import json

BASE_URL = "http://localhost:8000"

tasks = [
    "Create a Python script that prints 'Hello AI OS' and run it.",
    "List the files in my directory and check my python version.",
    "Read the contents of hello.py.",
    "Search the web for the latest news on AI.",
    "Post a photo to Instagram with the caption 'Working on my AI OS'.",
    "What is the weather like in New York?"
]

def test_task(prompt):
    print(f"\n--- Testing Task: '{prompt}' ---")
    try:
        # 1. Create plan
        print("1. Requesting plan...")
        res = requests.post(f"{BASE_URL}/plan", json={"prompt": prompt})
        if res.status_code != 200:
            print(f"Failed to create plan: {res.status_code} {res.text}")
            return
        
        data = res.json()
        if "plan" not in data:
            print("Response was not a plan (maybe a chat response):", data)
            return
            
        task_id = data["id"]
        print(f"Plan generated. Task ID: {task_id}")
        print("Plan details:", json.dumps(data["plan"], indent=2))
        
        # 2. Approve plan
        print("2. Approving plan...")
        res = requests.post(f"{BASE_URL}/approve/{task_id}")
        if res.status_code != 200:
            print(f"Failed to approve plan: {res.status_code} {res.text}")
            return
            
        print("Plan approved. Waiting for execution...")
        
        # 3. Poll for completion
        for _ in range(15):
            time.sleep(2)
            res = requests.get(f"{BASE_URL}/tasks/{task_id}")
            task_data = res.json()
            status = task_data.get("status")
            print(f"Status: {status}")
            if not status:
                print("Status: None")
                continue
            if status.upper() in ["COMPLETED", "FAILED"]:
                print("Execution result:", json.dumps(task_data.get("results", []), indent=2))
                break
        else:
            print("Execution timed out.")
            
    except Exception as e:
        print(f"Error testing task: {e}")

if __name__ == "__main__":
    for t in tasks:
        test_task(t)
