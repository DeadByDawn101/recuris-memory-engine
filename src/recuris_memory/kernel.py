"""Evidence-grounded state transition kernel."""

from __future__ import annotations

from dataclasses import replace
from typing import Callable, Mapping

from .models import (
    Action,
    CheckerDecision,
    GoalProposal,
    GoalState,
    GoalStatus,
    Observation,
    WorkingState,
)

Checker = Callable[[GoalState, GoalProposal, Action, Observation], tuple[bool, str]]


class EvidenceKernel:
    def __init__(self, checkers: Mapping[str, Checker]) -> None:
        self._checkers = dict(checkers)

    def commit(
        self,
        state: WorkingState,
        proposals: tuple[GoalProposal, ...],
        action: Action,
        observation: Observation,
    ) -> tuple[WorkingState, tuple[CheckerDecision, ...]]:
        by_id = {proposal.goal_id: proposal for proposal in proposals}
        unknown = set(by_id).difference(goal.goal_id for goal in state.goals)
        if unknown:
            raise KeyError(f"unknown goal proposals: {sorted(unknown)}")
        decisions: list[CheckerDecision] = []
        goals: list[GoalState] = []
        for current in state.goals:
            proposal = by_id.get(current.goal_id)
            if proposal is None:
                goals.append(current)
                continue
            checker = self._checkers.get(current.goal_id)
            if checker is None:
                accepted, reason = False, "no checker registered"
            elif action.draft:
                accepted, reason = False, "draft action was not executed"
            else:
                accepted, reason = checker(current, proposal, action, observation)
            decisions.append(CheckerDecision(current.goal_id, accepted, reason))
            if accepted:
                goals.append(
                    replace(
                        current,
                        status=proposal.status,
                        evidence=proposal.evidence,
                        blocker=proposal.blocker,
                    )
                )
            else:
                goals.append(current)
        return WorkingState(state.task_id, tuple(goals), state.step + 1), tuple(decisions)


def receipt_checker(required_key: str) -> Checker:
    """Build a checker that accepts completion only with a successful receipt key."""

    def check(
        current: GoalState,
        proposal: GoalProposal,
        action: Action,
        observation: Observation,
    ) -> tuple[bool, str]:
        del current, action
        if proposal.status is GoalStatus.DONE:
            accepted = observation.ok and bool(observation.receipt.get(required_key)) and bool(proposal.evidence)
            return accepted, "receipt verified" if accepted else f"missing successful receipt key: {required_key}"
        if proposal.status is GoalStatus.BLOCKED:
            accepted = bool(proposal.blocker)
            return accepted, "blocker recorded" if accepted else "blocked transition requires blocker"
        return True, "pending state retained"

    return check

