"""Bounded component patching and validation-gated admission."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Iterable

from .models import Component, MemoryControl


@dataclass(frozen=True)
class ComponentPatch:
    component: Component
    value: tuple[object, ...]
    reason: str


@dataclass(frozen=True)
class AdmissionResult:
    admitted: bool
    source_repaired: bool
    baseline_anchor_score: float
    candidate_anchor_score: float
    memory: MemoryControl
    reason: str


def apply_scoped_patches(
    baseline: MemoryControl,
    diagnosed: frozenset[Component],
    patches: Iterable[ComponentPatch],
) -> MemoryControl:
    candidate = baseline
    seen: set[Component] = set()
    fields = {
        Component.EXPERIENTIAL: "skills",
        Component.WORKING: "working_fields",
        Component.INVOCATION: "invocation_rules",
        Component.CHECKERS: "checker_ids",
    }
    for patch in patches:
        if patch.component not in diagnosed:
            raise ValueError(f"patch escapes diagnosis: {patch.component.value}")
        if patch.component in seen:
            raise ValueError(f"duplicate component patch: {patch.component.value}")
        if not patch.reason.strip():
            raise ValueError("patch reason must be non-empty")
        seen.add(patch.component)
        candidate = replace(candidate, **{fields[patch.component]: tuple(patch.value)})
    if seen != diagnosed:
        missing = sorted(component.value for component in diagnosed - seen)
        raise ValueError(f"missing patches for diagnosed components: {missing}")
    return candidate


SourceEvaluator = Callable[[MemoryControl], bool]
AnchorEvaluator = Callable[[MemoryControl], float]


class AdmissionGate:
    def __init__(self, minimum_anchor_delta: float = 0.0) -> None:
        self.minimum_anchor_delta = minimum_anchor_delta

    def evaluate(
        self,
        baseline: MemoryControl,
        candidate: MemoryControl,
        source_evaluator: SourceEvaluator,
        held_out_anchor_evaluator: AnchorEvaluator,
    ) -> AdmissionResult:
        source_repaired = bool(source_evaluator(candidate))
        baseline_score = float(held_out_anchor_evaluator(baseline))
        candidate_score = float(held_out_anchor_evaluator(candidate))
        no_regression = candidate_score - baseline_score >= self.minimum_anchor_delta
        admitted = source_repaired and no_regression
        if not source_repaired:
            reason = "source task not repaired"
        elif not no_regression:
            reason = "held-out anchor regression"
        else:
            reason = "source repaired and anchor criterion satisfied"
        return AdmissionResult(
            admitted,
            source_repaired,
            baseline_score,
            candidate_score,
            candidate if admitted else baseline,
            reason,
        )

