"""
lork/runtime/worker.py
=======================
Runtime Worker — executes tasks assigned to agents.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Protocol

from lork.models import (
    Agent,
    Run,
    RunOutcome,
    RunStep,
    Task,
    EventType,
    LorkEvent,
    new_id,
    utc_now,
)

from lork.policy.engine import PolicyEngine

from lork.exceptions import (
    LLMCallError,
    LLMQuotaExceededError,
    PolicyDeniedError,
    RuntimeExecutionError,
    ToolCallError,
)

logger = logging.getLogger(__name__)

MAX_RUN_WALL_CLOCK_SECONDS = 300
MAX_LLM_RETRIES = 3


class LLMClient(Protocol):

    async def complete(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        max_tokens: int = 2048,
    ) -> dict:
        ...


class ToolRegistry(Protocol):

    async def execute(self, tool_name: str, arguments: dict) -> Any: ...
    def get_schemas(self, tool_names: list[str]) -> list[dict]: ...


class RunStore(Protocol):

    async def save(self, run: Run) -> None: ...
    async def get(self, run_id: str) -> Run | None: ...


class EventBus(Protocol):

    async def publish(self, event: LorkEvent) -> None: ...


class RuntimeWorker:

    def __init__(
        self,
        worker_id: str,
        llm_client: LLMClient,
        tool_registry: ToolRegistry,
        run_store: RunStore,
        event_bus: EventBus,
    ) -> None:

        self.worker_id = worker_id
        self._llm = llm_client
        self._tools = tool_registry
        self._run_store = run_store
        self._bus = event_bus


    async def execute(
        self,
        agent: Agent,
        task: Task,
        policy_engine: PolicyEngine,
    ) -> Run:

        run = Run(
            id=new_id(),
            tenant_id=task.tenant_id,
            task_id=task.id,
            agent_id=agent.id,
            started_at=utc_now(),
        )

        await self._run_store.save(run)

        await self._bus.publish(
            LorkEvent(
                type=EventType.RUN_STARTED,
                tenant_id=task.tenant_id,
                source=f"worker:{self.worker_id}",
                payload={
                    "run_id": run.id,
                    "task_id": task.id,
                    "agent_id": agent.id,
                },
            )
        )

        try:

            run = await asyncio.wait_for(
                self._run_loop(agent, task, run, policy_engine),
                timeout=MAX_RUN_WALL_CLOCK_SECONDS,
            )

        except asyncio.TimeoutError:

            run = await self._finish_run(
                run,
                outcome=RunOutcome.TIMEOUT,
                error=f"Run exceeded {MAX_RUN_WALL_CLOCK_SECONDS}s",
            )

        except PolicyDeniedError as exc:

            run = await self._finish_run(
                run,
                outcome=RunOutcome.POLICY_BLOCKED,
                error=str(exc),
            )

        except (LLMCallError, ToolCallError) as exc:

            run = await self._finish_run(
                run,
                outcome=RunOutcome.RUNTIME_ERROR,
                error=str(exc),
            )

        except Exception as exc:

            logger.exception(
                "runtime.unhandled_error worker=%s run=%s",
                self.worker_id,
                run.id,
            )

            run = await self._finish_run(
                run,
                outcome=RunOutcome.RUNTIME_ERROR,
                error=str(exc),
            )

        await self._bus.publish(
            LorkEvent(
                type=EventType.RUN_FINISHED,
                tenant_id=task.tenant_id,
                source=f"worker:{self.worker_id}",
                payload={
                    "run_id": run.id,
                    "outcome": run.outcome,
                    "step_count": len(run.steps),
                    "token_usage": run.token_usage,
                },
            )
        )

        return run


    async def _run_loop(
        self,
        agent: Agent,
        task: Task,
        run: Run,
        policy_engine: PolicyEngine,
    ) -> Run:

        messages = self._build_initial_messages(agent, task)

        tool_schemas = self._tools.get_schemas(agent.permissions.allowed_tools)

        llm_call_count = 0

        total_tokens: dict[str, int] = {}

        steps: list[RunStep] = list(run.steps)

        while True:

            if llm_call_count >= agent.permissions.max_llm_calls_per_run:

                raise LLMQuotaExceededError(
                    f"max_llm_calls_per_run exceeded",
                    agent_id=agent.id,
                )

            llm_step = RunStep(
                type="llm_call",
                input={"messages": messages},
            )

            llm_response = await self._call_llm_with_retry(
                messages=messages,
                tool_schemas=tool_schemas,
            )

            llm_call_count += 1

            for k, v in llm_response.get("usage", {}).items():
                total_tokens[k] = total_tokens.get(k, 0) + v

            completed_llm_step = llm_step.model_copy(
                update={
                    "output": llm_response,
                    "finished_at": utc_now(),
                }
            )

            steps.append(completed_llm_step)

            run = run.model_copy(
                update={
                    "steps": steps,
                    "token_usage": total_tokens,
                }
            )

            await self._run_store.save(run)

            tool_calls = llm_response.get("tool_calls", [])

            if not tool_calls:
                break

            messages.append(
                {
                    "role": "assistant",
                    "content": llm_response.get("content", ""),
                    "tool_calls": tool_calls,
                }
            )

            for tool_call in tool_calls:

                tool_name = tool_call.get("name", "")
                arguments = tool_call.get("arguments", {})
                call_id = tool_call.get("id", new_id())

                policy_engine.enforce(
                    agent=agent,
                    action="api.call",
                    context={
                        "tool_name": tool_name,
                        "arguments": arguments,
                    },
                )

                tool_step = RunStep(
                    type="tool_call",
                    input={
                        "tool": tool_name,
                        "arguments": arguments,
                    },
                )

                try:

                    result = await self._tools.execute(
                        tool_name,
                        arguments,
                    )

                    completed = tool_step.model_copy(
                        update={
                            "output": {"result": result},
                            "finished_at": utc_now(),
                        }
                    )

                except Exception as exc:

                    completed = tool_step.model_copy(
                        update={
                            "error": str(exc),
                            "finished_at": utc_now(),
                        }
                    )

                    result = {"error": str(exc)}

                steps.append(completed)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": str(result),
                    }
                )

        return await self._finish_run(
            run,
            outcome=RunOutcome.SUCCESS,
        )


    async def _call_llm_with_retry(
        self,
        messages: list[dict],
        tool_schemas: list[dict],
    ) -> dict:

        last_error = None

        for attempt in range(MAX_LLM_RETRIES):

            try:

                return await self._llm.complete(
                    messages=messages,
                    tools=tool_schemas or None,
                )

            except LLMCallError as exc:

                last_error = exc

                wait = 2 ** attempt

                await asyncio.sleep(wait)

        raise LLMCallError(
            f"LLM call failed after retries: {last_error}"
        )


    async def _finish_run(
        self,
        run: Run,
        outcome: RunOutcome,
        error: str | None = None,
    ) -> Run:

        finished = run.model_copy(
            update={
                "outcome": outcome,
                "finished_at": utc_now(),
                "error": error,
            }
        )

        await self._run_store.save(finished)

        return finished


    @staticmethod
    def _build_initial_messages(agent: Agent, task: Task) -> list[dict]:

        system_prompt = (
            f"You are {agent.name}.\n"
            f"{agent.description}\n\n"
            f"Task: {task.input.type}\n"
            f"Payload: {task.input.payload}\n"
        )

        return [
            {"role": "system", "content": system_prompt},
        ]
