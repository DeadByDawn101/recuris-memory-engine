"""State-grounded skill invocation policies."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Action, ExecutionEvent, InvocationRecord, Skill, WorkingState


@dataclass(frozen=True)
class InvocationRule:
    name: str
    event: ExecutionEvent
    tool_keyed: bool = False
    unresolved_tag: str | None = None


@dataclass(frozen=True)
class InvocationPolicy:
    rules: tuple[InvocationRule, ...]

    def select(
        self,
        state: WorkingState,
        event: ExecutionEvent,
        action: Action,
        skills: tuple[Skill, ...],
    ) -> InvocationRecord:
        selected: dict[str, Skill] = {}
        retrieval_key: str | None = None
        unresolved_text = " ".join(goal.content.lower() for goal in state.unresolved)
        for rule in self.rules:
            if rule.event is not event:
                continue
            if rule.tool_keyed:
                if not (action.state_changing and action.draft):
                    continue
                retrieval_key = action.name
                candidates = (skill for skill in skills if skill.tool == action.name)
            else:
                candidates = iter(skills)
            for skill in candidates:
                if rule.unresolved_tag and rule.unresolved_tag.lower() not in unresolved_text:
                    continue
                selected[skill.skill_id] = skill
        return InvocationRecord(event, tuple(sorted(selected)), retrieval_key)

