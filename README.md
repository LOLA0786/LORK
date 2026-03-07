# LORK

**Control Plane for AI Agents**

> Just like Kubernetes manages containers,  
> **LORK manages autonomous AI workers.**

AI agents are starting to run real operations:
- processing invoices
- answering support tickets
- executing workflows
- interacting with APIs

But today they run with **no infrastructure**.

No identity.  
No permissions.  
No replay debugging.  
No audit trail.

**LORK fixes this.**

---

# The Problem

Today most AI agent systems look like this:


LLM → Tools → Chaos


Agents can call APIs, modify data, and make decisions — but there is **no control layer** governing those actions.

When something goes wrong:

- Why did the agent send that email?
- Why did it delete data?
- Why did it transfer money?

You cannot answer those questions.

---

# The Solution

LORK introduces an infrastructure layer between the agent and the real world.


LLM → LORK → Tools


LORK provides:

- Agent identity
- Policy enforcement
- Task orchestration
- Execution runtime
- Immutable event logs
- Replayable runs
- Time-travel debugging

---

# Quick Example

```python
import asyncio
from lork.sdk.client import LorkClient

async def main():

    async with LorkClient.embedded() as lork:

        agent = await lork.agents.register(
            tenant_id="acme",
            name="support_agent",
            allowed_actions=["email.send", "data.read"]
        )

        await lork.agents.activate(agent.id)

        task = await lork.tasks.submit(
            tenant_id="acme",
            agent_id=agent.id,
            task_type="answer_support_ticket",
            payload={"ticket": "TICK-1"}
        )

        print(task.status)

asyncio.run(main())
Time-Travel Debugging for Agents

Every agent run is stored as an immutable event log.

You can replay any run:

await lork.runs.replay(run_id)

Or fork the run into a new timeline:

await lork.runs.fork(run_id)

This allows engineers to debug AI systems the same way they debug software.

Architecture
                Your Application
                        │
                        ▼
             ┌────────────────────┐
             │   LORK Control     │
             │       Plane        │
             ├────────────────────┤
             │ Agent Registry     │
             │ Policy Engine      │
             │ Task Scheduler     │
             │ State Engine       │
             │ Replay Engine      │
             └──────────┬─────────┘
                        │
                        ▼
                 Runtime Workers
                        │
                        ▼
                 Tools / APIs / LLMs
Core Components
Component	Purpose
Agent Registry	Identity and lifecycle of agents
Policy Engine	Default-deny governance layer
Task Scheduler	Priority task orchestration
Runtime Workers	Distributed agent execution
State Engine	Event-sourced execution history
Replay Engine	Deterministic run replay
Observability	Metrics and tracing
Repository Structure
lork/
├── control_plane/
├── policy/
├── runtime/
├── storage/
├── state/
├── observability/
├── gateway/
├── sdk/
Roadmap
Phase 1

Agent identity

Policy enforcement

Task scheduling

Replayable runs

Phase 2

REST API

Postgres storage

Redis distributed queue

multi-worker runtime

Phase 3

agent marketplace

multi-agent coordination

enterprise governance

Why LORK Exists

We believe AI agents will become the next generation of workers.

But workers need infrastructure.

containers → Kubernetes
functions → serverless
agents → LORK
Status

LORK is currently early-stage infrastructure under active development.

The goal is to build the control plane for autonomous AI systems.

Contributing

Contributions are welcome.

See CONTRIBUTING.md for development guidelines.

License

Apache 2.0

