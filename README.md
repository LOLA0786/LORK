# LORK

**Control Plane for AI Agents**

LORK is infrastructure for managing and operating AI workers safely in production.

As organizations deploy autonomous agents for operations, finance, support, and research, they need a system that provides identity, permissions, governance, and observability.

LORK provides that control layer.

---

# Vision

In the same way that Kubernetes became the control plane for containers, LORK aims to become the control plane for AI workers.

Companies will run thousands of AI agents.  
Those agents must operate with security, permissions, auditability, and operational control.

LORK provides the infrastructure to manage them.

---

# Core Capabilities

LORK provides five core capabilities:

### 1. Agent Identity
Every AI worker must have a unique identity and ownership.

Example:

agent_id: finance_agent  
owner: acme_corp  
permissions: invoice.read, payment.request  

---

### 2. Policy Enforcement
Before an agent executes any action, LORK verifies that the action is permitted.

Example policy:

- AI agents cannot transfer funds without approval
- AI agents cannot delete production data
- AI agents must log financial actions

---

### 3. Task Orchestration
LORK schedules and assigns tasks to AI agents.

Example tasks:

- process invoice
- summarize report
- answer support ticket

---

### 4. Execution Runtime
Agents execute tasks in controlled runtime workers.

The runtime connects to LLMs, tools, and APIs while enforcing governance rules.

---

### 5. Monitoring & Audit
All agent actions are recorded for auditability and debugging.

Logs include:

- agent decisions
- executed actions
- policy checks
- failures

---

# High Level Architecture

AI Agents  
    ↓  
LORK SDK  
    ↓  
LORK Control Plane  
    ↓  
Agent Runtime Workers  
    ↓  
External Tools / APIs / Databases

---

# System Components

## Control Plane
Responsible for management and governance.

Components:

- Agent Registry
- Policy Engine
- Task Scheduler
- Audit Logger
- Monitoring APIs

---

## Runtime Workers
Execute agent tasks safely.

Responsibilities:

- run LLM calls
- execute tool actions
- enforce runtime policies
- stream execution logs

---

## Developer SDK
SDK for developers to run agents on LORK.

Example:

from lork import Agent

agent = Agent(
    name="support_agent",
    permissions=["email.send","crm.read"]
)

agent.run()

---

# Repository Structure (Planned)

lork/
 ├── control_plane
 │   ├── api.py
 │   ├── agent_registry.py
 │   ├── scheduler.py
 │   └── audit_logger.py
 │
 ├── runtime
 │   ├── worker.py
 │   └── executor.py
 │
 ├── policy
 │   └── policy_engine.py
 │
 ├── sdk
 │   └── agent_client.py
 │
 └── examples
     └── demo_agent.py

---

# Initial Goals

Phase 1 (Prototype)

- agent registry
- permission system
- simple task scheduler
- runtime worker
- logging

Phase 2

- distributed runtimes
- policy framework
- monitoring dashboard
- enterprise security controls

Phase 3

- large scale AI workforce orchestration
- multi-agent coordination
- enterprise integrations

---

# Long-Term Goal

LORK aims to provide the infrastructure layer for operating AI workers at scale across organizations.

