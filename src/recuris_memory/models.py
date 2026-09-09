"""Immutable domain types for the memory-control layer and execution trace."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class GoalStatus(str, Enum):
    PENDING = "pending"
    DONE = "done"
    BLOCKED = "blocked"


class Component(str, Enum):
    EXPERIENTIAL = "experiential"
    WORKING = "working"
    INVOCATION = "invocation"
    CHECKERS = "checkers"


class ExecutionEvent(str, Enum):
    FIRST_TURN = "first_turn"
    TURN_BOUNDARY = "turn_boundary"
    STATE_CHANGING_DRAFT = "state_changing_draft"


@dataclass(frozen=True)
class Skill:
    skill_id: str
    description: str
    tool: str | None = None
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.skill_id.strip() or not self.description.strip():
            raise ValueError("skill_id and description must be non-empty")


@dataclass(frozen=True)
class GoalState:
    goal_id: str
    content: str
    status: GoalStatus = GoalStatus.PENDING
    evidence: tuple[str, ...] = ()
    blocker: str | None = None

    def __post_init__(self) -> None:
        if not self.goal_id.strip() or not self.content.strip():
            raise ValueError("goal_id and content must be non-empty")
        if self.status is GoalStatus.DONE and not self.evidence:
            raise ValueError("done goals require evidence")
        if self.status is GoalStatus.BLOCKED and not self.blocker:
            raise ValueError("blocked goals require a blocker")


@dataclass(frozen=True)
class WorkingState:
    task_id: str
    goals: tuple[GoalState, ...]
    step: int = 0

    def __post_init__(self) -> None:
        if len({goal.goal_id for goal in self.goals}) != len(self.goals):
            raise ValueError("goal IDs must be unique")

    def goal(self, goal_id: str) -> GoalState:
        try:
            return next(goal for goal in self.goals if goal.goal_id == goal_id)
        except StopIteration as exc:
            raise KeyError(goal_id) from exc

    @property
    def unresolved(self) -> tuple[GoalState, ...]:
        return tuple(goal for goal in self.goals if goal.status is not GoalStatus.DONE)


@dataclass(frozen=True)
class GoalProposal:
    goal_id: str
    status: GoalStatus
    evidence: tuple[str, ...] = ()
    blocker: str | None = None


@dataclass(frozen=True)
class Action:
    name: str
    arguments: Mapping[str, Any] = field(default_factory=dict)
    state_changing: bool = False
    draft: bool = False


@dataclass(frozen=True)
class Observation:
    ok: bool
    receipt: Mapping[str, Any] = field(default_factory=dict)
    message: str = ""


@dataclass(frozen=True)
class CheckerDecision:
    goal_id: str
    accepted: bool
    reason: str


@dataclass(frozen=True)
class InvocationRecord:
    event: ExecutionEvent
    skill_ids: tuple[str, ...]
    retrieval_key: str | None


@dataclass(frozen=True)
class TraceEntry:
    step: int
    pre_state: WorkingState
    invocation: InvocationRecord
    action: Action
    observation: Observation
    proposals: tuple[GoalProposal, ...]
    checker_decisions: tuple[CheckerDecision, ...]
    post_state: WorkingState


@dataclass(frozen=True)
class MemoryControl:
    """The bounded mutable layer M=(E,W,rho,C); outer harness is excluded."""

    skills: tuple[Skill, ...]
    working_fields: tuple[str, ...]
    invocation_rules: tuple[Any, ...]
    checker_ids: tuple[str, ...]

