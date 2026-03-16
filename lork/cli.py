import sys
import uuid
import json
from pathlib import Path

RUN_DIR = Path.home() / ".lork" / "runs"
RUN_DIR.mkdir(parents=True, exist_ok=True)


def run_workflow(path: str):
    workflow_path = Path(path)

    if not workflow_path.exists():
        print(f"❌ Workflow file not found: {workflow_path}")
        sys.exit(1)

    run_id = str(uuid.uuid4())

    agents = ["planner", "retriever", "writer"]

    run_data = {
        "run_id": run_id,
        "workflow": str(workflow_path),
        "status": "completed",
        "agents": agents
    }

    with open(RUN_DIR / f"{run_id}.json", "w") as f:
        json.dump(run_data, f, indent=2)

    print("🚀 LORk runtime starting")
    print(f"Workflow: {workflow_path}")
    print(f"Run ID: {run_id}")
    print("Execution complete")

    print(f"\nInspect with:\n  lork inspect run {run_id}")
    print(f"Replay with:\n  lork replay {run_id}")


def inspect_run(run_id: str):
    file = RUN_DIR / f"{run_id}.json"

    if not file.exists():
        print("Run not found")
        sys.exit(1)

    data = json.load(open(file))

    print("🔍 Run Timeline\n")

    for i, agent in enumerate(data["agents"], start=1):
        print(f"{i}. {agent:<12} ✔ completed")


def replay_run(run_id: str):
    file = RUN_DIR / f"{run_id}.json"

    if not file.exists():
        print("Run not found")
        sys.exit(1)

    data = json.load(open(file))

    print("⏪ Replaying run\n")
    print(f"Run ID: {run_id}")
    print()

    for agent in data["agents"]:
        print(f"Replaying agent: {agent}")

    print("\nReplay complete")


def serve():
    print("🌐 LORk control plane starting")
    print("API endpoint: http://localhost:8080")


def help():
    print(
"""
LORk AI Runtime

Commands:

  lork run <workflow.yaml>
  lork inspect run <run_id>
  lork replay <run_id>
  lork serve
"""
    )


def main():
    if len(sys.argv) < 2:
        help()
        return

    cmd = sys.argv[1]

    if cmd == "run":
        run_workflow(sys.argv[2])

    elif cmd == "inspect":
        inspect_run(sys.argv[3])

    elif cmd == "replay":
        replay_run(sys.argv[2])

    elif cmd == "serve":
        serve()

    else:
        help()


if __name__ == "__main__":
    main()
