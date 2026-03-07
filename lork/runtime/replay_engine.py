"""
LORK Replay Engine
==================

Provides deterministic replay for agent executions.

Every agent run is stored as a sequence of immutable steps.
The replay engine can reconstruct and replay the run exactly.

Run structure:

Run
 ├─ step 1: llm_call
 ├─ step 2: tool_call
 ├─ step 3: policy_check
 ├─ step 4: tool_result
 └─ step 5: final_output
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class RunStep:
    """
    Single step in an agent execution.
    """

    def __init__(
        self,
        step_type: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ):
        self.step_type = step_type
        self.input = input_data
        self.output = output_data or {}
        self.timestamp = timestamp or datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.step_type,
            "input": self.input,
            "output": self.output,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunStep":
        return cls(
            step_type=data["type"],
            input_data=data.get("input", {}),
            output_data=data.get("output", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


class RunLedger:
    """
    Immutable ledger of run steps.
    """

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.steps: List[RunStep] = []

    def record_step(self, step: RunStep):
        logger.debug("Recording step %s for run %s", step.step_type, self.run_id)
        self.steps.append(step)

    def to_json(self) -> str:
        return json.dumps(
            {
                "run_id": self.run_id,
                "steps": [s.to_dict() for s in self.steps],
            },
            indent=2,
        )

    @classmethod
    def from_json(cls, data: str) -> "RunLedger":
        obj = json.loads(data)
        ledger = cls(obj["run_id"])
        ledger.steps = [RunStep.from_dict(s) for s in obj["steps"]]
        return ledger


class ReplayEngine:
    """
    Replays an agent run deterministically.
    """

    def __init__(self):
        self._handlers = {}

    def register_handler(self, step_type: str, handler):
        """
        Register a replay handler for a step type.
        """
        self._handlers[step_type] = handler

    async def replay(self, ledger: RunLedger):
        """
        Replay the full run.
        """
        logger.info("Replaying run %s", ledger.run_id)

        results = []

        for step in ledger.steps:
            handler = self._handlers.get(step.step_type)

            if not handler:
                logger.warning(
                    "No handler registered for step type '%s'", step.step_type
                )
                continue

            result = await handler(step.input)

            results.append(
                {
                    "step": step.step_type,
                    "expected_output": step.output,
                    "replay_output": result,
                }
            )

        return results


class StepRecorder:
    """
    Helper used by runtime workers to record execution steps.
    """

    def __init__(self, ledger: RunLedger):
        self._ledger = ledger

    def record_llm_call(self, prompt: str, response: str, model: str):
        step = RunStep(
            step_type="llm_call",
            input_data={
                "prompt": prompt,
                "model": model,
            },
            output_data={
                "response": response,
            },
        )
        self._ledger.record_step(step)

    def record_tool_call(self, tool: str, args: Dict[str, Any], result: Any):
        step = RunStep(
            step_type="tool_call",
            input_data={
                "tool": tool,
                "arguments": args,
            },
            output_data={
                "result": result,
            },
        )
        self._ledger.record_step(step)

    def record_policy_check(self, action: str, decision: str):
        step = RunStep(
            step_type="policy_check",
            input_data={"action": action},
            output_data={"decision": decision},
        )
        self._ledger.record_step(step)


async def example_llm_handler(input_data: Dict[str, Any]):
    """
    Example replay handler for LLM calls.
    """
    prompt = input_data["prompt"]
    model = input_data["model"]

    logger.info("Replaying LLM call with model %s", model)

    # In replay mode you usually do NOT call the model again.
    # Instead you compare recorded output.

    return {
        "replayed": True,
        "prompt": prompt,
    }


async def example_tool_handler(input_data: Dict[str, Any]):
    """
    Example replay handler for tool calls.
    """
    tool = input_data["tool"]

    logger.info("Replaying tool call: %s", tool)

    return {"tool_executed": tool}


def create_default_replay_engine() -> ReplayEngine:
    engine = ReplayEngine()

    engine.register_handler("llm_call", example_llm_handler)
    engine.register_handler("tool_call", example_tool_handler)

    return engine
