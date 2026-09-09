"""Small deterministic demonstration of evidence-grounded completion."""

from __future__ import annotations

import argparse
import dataclasses
import enum
import json
from pathlib import Path
from typing import Any

from .engine import RecurisEngine
from .invocation import InvocationPolicy, InvocationRule
from .kernel import EvidenceKernel, receipt_checker
from .models import (
    Action,
    ExecutionEvent,
    GoalProposal,
    GoalState,
    GoalStatus,
    MemoryControl,
    Observation,
    Skill,
    WorkingState,
)


def encode(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {field.name: encode(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, tuple):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {key: encode(item) for key, item in value.items()}
    return value


def demo(output: Path | None) -> int:
    skill = Skill("verify-write", "Verify a write receipt before completion", tool="store")
    rule = InvocationRule("call-time", ExecutionEvent.STATE_CHANGING_DRAFT, tool_keyed=True)
    memory = MemoryControl((skill,), ("status", "evidence", "blocker"), (rule,), ("persist",))
    policy = InvocationPolicy((rule,))
    engine = RecurisEngine(memory, policy, EvidenceKernel({"persist": receipt_checker("write_id")}))
    state = WorkingState("demo", (GoalState("persist", "Persist the record"),))
    draft = Action("store", {"record": "demo"}, state_changing=True, draft=True)
    state = engine.step(
        state,
        ExecutionEvent.STATE_CHANGING_DRAFT,
        draft,
        Observation(False, {}, "synthetic not-executed result"),
        (GoalProposal("persist", GoalStatus.DONE, ("model claimed success",)),),
    )
    executed = Action("store", {"record": "demo"}, state_changing=True)
    state = engine.step(
        state,
        ExecutionEvent.TURN_BOUNDARY,
        executed,
        Observation(True, {"write_id": "demo-001"}, "stored"),
        (GoalProposal("persist", GoalStatus.DONE, ("write_id=demo-001",)),),
    )
    payload = {"final_state": encode(state), "trace": encode(engine.trace)}
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    return demo(args.output)


if __name__ == "__main__":
    raise SystemExit(main())

