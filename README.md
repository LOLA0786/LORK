# LORK

**Control Plane for AI Agents**

> In the same way Kubernetes became the control plane for containers,  
> LORK is the control plane for AI workers.

---

# What is LORK?

Companies are deploying AI agents to run real operations:

- processing invoices
- answering support tickets
- running internal workflows
- managing infrastructure
- performing research

But most agents today run with **no identity, no permissions, no audit trail, and no governance**.

LORK provides the **infrastructure layer for running AI workers safely at scale**.

| Without LORK | With LORK |
|---|---|
| Agents run with no identity | Every agent has a unique ID |
| No permission system | Default-deny policy engine |
| Ad-hoc task execution | Priority scheduler with deadlines |
| No observability | Full execution traces (Run records) |
| No governance | Policy enforcement on every action |
| Hard to scale | Stateless workers + pluggable storage |

---

# Quickstart

Install:


pip install lork


Example:

```python
import asyncio
from lork.sdk.client import LorkClient

async def main():
    async with LorkClient.embedded() as lork:

        agent = await lork.agents.register(
            tenant_id="acme-corp",
            name="invoice_processor",
            description="Processes vendor invoices.",
            allowed_actions=["finance.read", "data.read", "email.send"],
        )

        await lork.agents.activate(agent.id)

        task = await lork.tasks.submit(
            tenant_id="acme-corp",
            agent_id=agent.id,
            task_type="process_invoice",
            payload={"invoice_id": "INV-001", "amount": 4500.00},
        )

        print(task.id)

asyncio.run(main())

Run the full demo:

python examples/demo_agent.py
Core Concepts
Agent

An AI worker with identity, permissions, and lifecycle.

Lifecycle:

PENDING → ACTIVE → SUSPENDED → RETIRED

Example:

agent = await lork.agents.register(
    tenant_id="my-org",
    name="support_agent",
    allowed_actions=["email.send", "crm.read"],
)
Policy

Governance rules controlling agent behavior.

Default model:

DENY everything unless explicitly allowed

Example:

PolicyRule(
    effect=PolicyEffect.DENY,
    actions=["finance.transfer"],
    conditions=[
        PolicyCondition(field="amount", operator="gt", value=10000)
    ]
)
Task

Unit of work assigned to an agent.

QUEUED → ASSIGNED → RUNNING → SUCCEEDED

Example:

task = await lork.tasks.submit(
    tenant_id="org",
    agent_id=agent.id,
    task_type="summarize_report",
    payload={"url": "..."},
)
Run

A full execution trace of a task:

LLM calls

tool invocations

policy checks

outputs

token usage

Runs are immutable audit records.

Architecture
Application
     │
     ▼
┌─────────────────────────────┐
│        LORK Control Plane   │
│                             │
│  Agent Registry             │
│  Task Scheduler             │
│  Policy Engine              │
└──────────────┬──────────────┘
               │
               ▼
        Runtime Workers
               │
               ▼
     Tools • APIs • LLMs

Runtime workers are stateless, allowing horizontal scaling.

Repository Structure
lork/
├── lork/
│   ├── models.py
│   ├── exceptions.py
│   ├── control_plane/
│   ├── policy/
│   ├── runtime/
│   ├── storage/
│   └── sdk/
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── examples/
│   └── demo_agent.py
Where to Start Reading

1️⃣ lork/models.py
2️⃣ lork/exceptions.py
3️⃣ lork/policy/engine.py
4️⃣ examples/demo_agent.py

Roadmap
Phase 1 — Core

Agent identity

Policy engine

Task scheduler

Runtime workers

Python SDK

Phase 2 — Production

REST API

Postgres storage

Redis queue

Metrics + tracing

Kubernetes deployment

Phase 3 — Scale

Multi-agent orchestration

Human approval workflows

Streaming execution logs

Enterprise authentication

Why LORK Exists

AI agents are becoming operational infrastructure.

But companies will not trust agents unless they have:

identity

permissions

governance

auditability

LORK provides that foundation.

License

Apache 2.0
