"""Task-level coordinator producing append-only structured traces."""

from __future__ import annotations

from .invocation import InvocationPolicy
from .kernel import EvidenceKernel
from .models import (
    Action,
    ExecutionEvent,
    GoalProposal,
    MemoryControl,
    Observation,
    TraceEntry,
    WorkingState,
)


class RecurisEngine:
    def __init__(self, memory: MemoryControl, policy: InvocationPolicy, kernel: EvidenceKernel) -> None:
        self.memory = memory
        self.policy = policy
        self.kernel = kernel
        self._trace: list[TraceEntry] = []

    @property
    def trace(self) -> tuple[TraceEntry, ...]:
        return tuple(self._trace)

    def step(
        self,
        state: WorkingState,
        event: ExecutionEvent,
        action: Action,
        observation: Observation,
        proposals: tuple[GoalProposal, ...],
    ) -> WorkingState:
        invocation = self.policy.select(state, event, action, self.memory.skills)
        post_state, decisions = self.kernel.commit(state, proposals, action, observation)
        self._trace.append(
            TraceEntry(
                step=state.step,
                pre_state=state,
                invocation=invocation,
                action=action,
                observation=observation,
                proposals=proposals,
                checker_decisions=decisions,
                post_state=post_state,
            )
        )
        return post_state

