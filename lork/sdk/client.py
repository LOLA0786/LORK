"""
lork/sdk/client.py
==================
LORK Python SDK — the primary interface for developers building on LORK.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from lork.control_plane.agent_registry import AgentRegistry
from lork.control_plane.scheduler import Scheduler

from lork.models import (
    Agent,
    AgentPermissions,
    AgentStatus,
    Task,
    TaskStatus,
)

from lork.storage.memory import (
    InMemoryAgentStore,
    InMemoryEventBus,
    InMemoryPolicyStore,
    InMemoryRunStore,
    InMemoryTaskStore,
    InMemoryTenantStore,
)

logger = logging.getLogger(__name__)


class AgentsClient:

    def __init__(self, registry: AgentRegistry) -> None:
        self._registry = registry


    async def register(
        self,
        tenant_id: str,
        name: str,
        description: str = "",
        allowed_actions: list[str] | None = None,
        allowed_tools: list[str] | None = None,
        max_llm_calls_per_run: int = 50,
        require_human_approval_for: list[str] | None = None,
        tags: dict[str, str] | None = None,
    ) -> Agent:

        permissions = AgentPermissions(
            allowed_actions=allowed_actions or [],
            allowed_tools=allowed_tools or [],
            max_llm_calls_per_run=max_llm_calls_per_run,
            require_human_approval_for=require_human_approval_for or [],
        )

        return await self._registry.register(
            tenant_id=tenant_id,
            name=name,
            description=description,
            permissions=permissions,
            tags=tags,
        )


    async def activate(self, agent_id: str) -> Agent:
        return await self._registry.activate(agent_id)


    async def suspend(self, agent_id: str, reason: str = "") -> Agent:
        return await self._registry.suspend(agent_id, reason)


    async def retire(self, agent_id: str) -> Agent:
        return await self._registry.retire(agent_id)


    async def get(self, agent_id: str) -> Agent:
        return await self._registry.get(agent_id)


    async def list(
        self,
        tenant_id: str,
        status: AgentStatus | None = None,
        tags: dict[str, str] | None = None,
    ) -> list[Agent]:

        return await self._registry.list(
            tenant_id,
            status=status,
            tags=tags,
        )


class TasksClient:

    def __init__(self, scheduler: Scheduler) -> None:
        self._scheduler = scheduler


    async def submit(
        self,
        tenant_id: str,
        agent_id: str,
        task_type: str,
        payload: dict[str, Any] | None = None,
        priority: int = 5,
        deadline_at: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Task:

        return await self._scheduler.submit(
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_type=task_type,
            payload=payload or {},
            priority=priority,
            deadline_at=deadline_at,
            metadata=metadata,
        )


    async def get(self, task_id: str) -> Task:
        return await self._scheduler.get(task_id)


    async def cancel(self, task_id: str) -> Task:
        return await self._scheduler.cancel(task_id)


    async def list_for_agent(
        self,
        agent_id: str,
        status: TaskStatus | None = None,
    ) -> list[Task]:

        return await self._scheduler.list_for_agent(
            agent_id,
            status,
        )


    async def queue_depth(self) -> int:
        return await self._scheduler.queue_depth()


class LorkClient:

    def __init__(
        self,
        registry: AgentRegistry,
        scheduler: Scheduler,
    ) -> None:

        self.agents = AgentsClient(registry)
        self.tasks = TasksClient(scheduler)

        self._scheduler = scheduler


    async def close(self) -> None:
        await self._scheduler.stop()


    @classmethod
    @asynccontextmanager
    async def embedded(cls) -> AsyncIterator["LorkClient"]:

        agent_store = InMemoryAgentStore()
        task_store = InMemoryTaskStore()
        policy_store = InMemoryPolicyStore()
        run_store = InMemoryRunStore()
        tenant_store = InMemoryTenantStore()
        event_bus = InMemoryEventBus()

        registry = AgentRegistry(
            store=agent_store,
            event_bus=event_bus,
        )

        scheduler = Scheduler(
            store=task_store,
            event_bus=event_bus,
            agent_registry=registry,
        )

        await scheduler.start()

        client = cls(
            registry=registry,
            scheduler=scheduler,
        )

        try:
            yield client
        finally:
            await client.close()
            logger.info("LorkClient.embedded: shutdown complete")
