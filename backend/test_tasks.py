"""
Quick targeted test for MEGAN — tests the 6 README tasks.
Runs synchronously and waits longer for execution.
"""
import requests
import time
import json

BASE = "http://localhost:8000"

TASKS = [
    ("Create a Python script that prints 'Hello AI OS' and run it.", True),
    ("List the files in my directory and check my python version.", True),
    ("Read the contents of hello.py.", True),
    ("Search the web for the latest news on AI.", True),
    ("Post a photo to Instagram with the caption 'Working on my AI OS'.", True),
    ("What is the weather like in New York?", True),
]

def run(prompt, expect_plan):
    print(f"\n{'='*60}")
    print(f"TASK: {prompt}")
    print(f"{'='*60}")

    r = requests.post(f"{BASE}/plan", json={"prompt": prompt})
    if r.status_code != 200:
        print(f"  ✗ Plan request failed: {r.status_code} {r.text}")
        return

    data = r.json()

    if "plan" not in data:
        print(f"  → Chat response: {data.get('message', data)}")
        return

    task_id = data["id"]
    steps = data["plan"]["steps"]
    print(f"  ✓ Plan generated ({len(steps)} steps):")
    for s in steps:
        print(f"     [{s['id']}] {s['action']}({json.dumps(s['params'])}) → {s['description']}")

    # Approve
    r2 = requests.post(f"{BASE}/approve/{task_id}")
    if r2.status_code != 200:
        print(f"  ✗ Approve failed: {r2.status_code}")
        return
    print(f"  ✓ Approved. Waiting for execution...")

    # Poll for up to 30s
    for i in range(30):
        time.sleep(1)
        r3 = requests.get(f"{BASE}/tasks/{task_id}")
        td = r3.json()
        status = td.get("status", "?")
        if status and status.upper() in ("COMPLETED", "FAILED"):
            print(f"  ✓ Status: {status.upper()}")
            for res in td.get("results", []):
                icon = "✓" if res["status"] == "success" else "✗"
                print(f"     [{res['step_id']}] {icon} {res['action']}: {res['output'][:200]}")
            return
        if (i+1) % 5 == 0:
            print(f"     ... still waiting ({i+1}s) — status: {status}")

    print(f"  ✗ Timed out after 30s.")


if __name__ == "__main__":
    print("\n🤖 MEGAN Autonomous AI OS — Task Verification\n")
    for prompt, expect in TASKS:
        run(prompt, expect)
    print("\n✅ All tests complete.\n")
