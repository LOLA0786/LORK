"""
LORK Runtime Worker
===================

This worker executes tasks submitted to the LORK control plane.

Flow:

scheduler → claim task
        ↓
policy check
        ↓
agent execution loop
        ↓
record run
        ↓
complete task

Workers are stateless. Many workers can run simultaneously.
"""

from __future__ import annotations

import asyncio
import logging
import traceback
from datetime import datetime, timezone
from typing import Any

from lork.control_plane.scheduler import Scheduler
from lork.control_plane.agent_registry import AgentRegistry
from lork.models import Run, TaskStatus
from lork.exceptions import RuntimeExecutionError

logger = logging.getLogger(__name__)


class RuntimeWorker:
    """
    Executes tasks from the LORK scheduler.

    Each worker runs an infinite loop:
        poll → claim task → execute → complete
    """

    def __init__(
        self,
        scheduler: Scheduler,
        registry: AgentRegistry,
        worker_id: str = "worker-1",
        poll_interval: float = 1.0,
    ):
        self._scheduler = scheduler
        self._registry = registry
        self._worker_id = worker_id
        self._poll_interval = poll_interval
        self._running = False

    async def start(self):
        """Start the worker loop."""
        logger.info("runtime worker %s starting", self._worker_id)
        self._running = True

        while self._running:
            try:
                task = await self._scheduler.claim_next()

                if not task:
                    await asyncio.sleep(self._poll_interval)
                    continue

                await self._execute_task(task)

            except Exception:
                logger.exception("worker loop failure")
                await asyncio.sleep(self._poll_interval)

    async def stop(self):
        """Stop worker gracefully."""
        logger.info("runtime worker stopping")
        self._running = False

    async def _execute_task(self, task):
        """Execute a single task."""
        logger.info("executing task %s", task.id)

        try:
            agent = await self._registry.get(task.agent_id)

            run = Run(
                id=str(task.id) + "-run",
                tenant_id=task.tenant_id,
                agent_id=task.agent_id,
                task_id=task.id,
                started_at=datetime.now(timezone.utc),
                steps=[],
            )

            result = await self._agent_loop(agent, task)

            run.completed_at = datetime.now(timezone.utc)
            run.result = result

            await self._scheduler.complete(task.id)

            logger.info("task %s completed", task.id)

        except Exception as exc:
            logger.error("task execution failed: %s", exc)
            traceback.print_exc()

            await self._scheduler.fail(task.id, str(exc))

            raise RuntimeExecutionError(str(exc))

    async def _agent_loop(self, agent, task):
        """
        Simple agent execution loop.

        Real version will:
            LLM → tool → policy → repeat
        """

        payload = task.input.payload

        logger.info(
            "agent %s executing task type=%s payload=%s",
            agent.name,
            task.input.type,
            payload,
        )

        # Mock execution (placeholder)
        await asyncio.sleep(1)

        return {
            "status": "success",
            "task_type": task.input.type,
            "processed": payload,
        }


async def start_worker(scheduler: Scheduler, registry: AgentRegistry):
    """
    Helper to run a worker quickly.
    """

    worker = RuntimeWorker(
        scheduler=scheduler,
        registry=registry,
        worker_id="worker-local",
    )

    await worker.start()


if __name__ == "__main__":
    print(
        "Runtime workers should be started via the control plane, "
        "not directly."
    )
