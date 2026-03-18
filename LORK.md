# LORK

> **Control Plane for AI Agents**


Containers → Kubernetes
Functions → Serverless
Agents → LORK


LORK is infrastructure for running, observing, and debugging autonomous AI systems in production. It introduces deterministic execution, event-sourced agent runs, and time-travel debugging for complex AI workflows — the primitives that production AI systems have always needed but never had.

---

## Why LORK Exists

AI agents behave like distributed systems. They call tools, query models, access APIs, and make multi-step decisions across long-running workflows. When something goes wrong, traditional debugging tools are useless — you can't `print` your way through a non-deterministic agent run.

LORK introduces the infrastructure primitives that make AI systems observable and reproducible:

- **Event-sourced execution** — every step is an immutable event
- **Deterministic replay** — re-execute any historical run from its event log
- **Run forking** — branch from any point in history and explore alternate paths
- **Execution tracing** — full call graph for every agent workflow
- **Timeline inspection** — step through a run event by event

---

## Architecture


Applications
│
▼
LORK Control Plane
│
├── Workflow Specifications
├── Scheduler
├── Agent Graph
├── Policy Engine
├── Event Store (lork.db)
└── Observability
│
▼
Runtime Workers
│
▼
Tools / APIs / LLMs


The control plane manages workflow state and orchestration. Runtime workers execute agent actions. The separation means orchestration and execution can scale independently, and the event store is always the authoritative record.

---

## Execution Model

Every step in a workflow generates an immutable event appended to the event store:


run_id → unique run identifier
sequence → monotonic step counter
timestamp → wall clock at execution time
type → event type (agent_step, tool_call, approval, error)
agent_id → which agent produced this event
payload → action details and parameters


Because runs are fully event-sourced, any run can be replayed, inspected, or forked at any point — without touching production.

---

## Quickstart

```bash
pip install lork
Run a workflow
python cmd/lork-run-workflow.py workflows/support_ticket.yaml
Starting run: e9268751...
[1] support_agent -> read_ticket
[2] support_agent -> search_docs
[3] support_agent -> draft_reply
Run complete: e9268751...
List runs
python cmd/lork-debug-run.py --list
Available runs:
  e9268751...
  317e26ee...
  test-run
Commands
Inspect a run
python cmd/lork-inspect-run.py <run_id>
Trace execution
python cmd/lork-trace-run.py <run_id>
Replay a run
python cmd/lork-replay-run.py <run_id>
Fork a run
python cmd/lork-fork-run.py <run_id>
Time-Travel Debugging

Because every run is a sequence of immutable events, LORK can reconstruct the exact state of any agent at any point in its execution history. This enables:

Root cause analysis

Regression testing

What-if simulation

Compliance reconstruction

Repository Layout
lork/           Core control plane and execution engine
cmd/            CLI commands
workflows/      Workflow specs
infra/          Deployment configs
migrations/     Schema migrations
examples/       Sample workflows
docs/           Guides
tests/          Test suites
Workflow Specification
name: support_ticket
agents:
  - id: support_agent
    model: claude-sonnet-4-20250514
    tools:
      - read_ticket
      - search_docs
      - draft_reply
steps:
  - agent: support_agent
    action: read_ticket
  - agent: support_agent
    action: search_docs
  - agent: support_agent
    action: draft_reply
Positioning

LORK is not a framework.

It is:
👉 A control plane for deterministic AI execution

License

See LICENSE.
