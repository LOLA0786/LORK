# LORK

Control Plane for AI Agents.

Containers → Kubernetes  
Functions → Serverless  
Agents → LORK

LORK provides infrastructure for running, observing, and debugging autonomous AI systems in production. It introduces deterministic execution, event-sourced agent runs, and time-travel debugging for complex AI workflows.

The system is designed as a control plane for agent orchestration, providing the operational guarantees engineers expect from modern distributed systems.

---

## Core Capabilities

**Event-Sourced Execution**

Every agent step is recorded as an immutable event.  
This provides a complete execution history and enables deterministic replay.

**Time-Travel Debugging**

Engineers can inspect the exact timeline of an AI run, including every step, tool invocation, and decision made during execution.

**Run Replay**

Historical runs can be replayed deterministically, enabling debugging and reproducibility.

**Run Forking**

Existing runs can be forked into new timelines, allowing engineers to explore alternate execution paths without modifying the original run.

**Agent Graph Execution**

Multi-agent workflows are executed as directed graphs where agents coordinate through defined actions and tool calls.

---

## Quick Example

Workflow specification:


workflows/support_ticket.yaml


Run the workflow:


python cmd/lork-run-workflow.py workflows/support_ticket.yaml


List runs:


python cmd/lork-debug-run.py --list


Inspect a run:


python cmd/lork-debug-run.py <run_id>


Trace execution:


python cmd/lork-trace-run.py <run_id>


Replay a run:


python cmd/lork-replay-run.py <run_id>


Fork a run:


python cmd/lork-fork-run.py <run_id>


---

## Architecture Overview

Applications interact with the LORK control plane, which manages workflow execution and state.


Applications
│
▼
LORK Control Plane
│
├ Workflow Specifications
├ Controller Loop
├ Scheduler
├ Agent Graph
├ Policy Engine
├ Event Store
└ Observability
│
▼
Runtime Workers
│
▼
Tools / APIs / LLMs


The architecture separates orchestration logic from runtime execution, allowing the system to scale and remain observable.

---

## Key Concepts

**Workflow**

A declarative specification describing a sequence or graph of agent actions.

**Run**

A single execution instance of a workflow.

**Event**

An immutable record describing a step in the execution timeline.

**Replay**

Re-execution of a historical run from its event log.

**Fork**

Creation of a new run derived from the event history of an existing run.

---

## Why LORK Exists

As AI agents become more autonomous, engineering teams require infrastructure capable of managing complex decision-making systems.

Traditional debugging tools are insufficient for systems driven by probabilistic models and external tool calls.

LORK addresses this challenge by introducing deterministic execution, event-sourced state, and replayable agent workflows.

---

## Repository Structure


lork/
├ cmd/
├ lork/
├ workflows/
├ docs/
├ tests/
└ infra/


The project separates control-plane logic, runtime execution, and developer tooling into clearly defined modules.

---

## Status

LORK is currently early-stage infrastructure under active development.

The goal is to establish the operational foundation required for reliable AI agent systems.

---

## License

Apache 2.0
