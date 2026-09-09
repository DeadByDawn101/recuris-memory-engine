# Architecture Decision: Bounded Memory Evolution

## Decision

Represent the adaptive surface as an immutable `MemoryControl` value containing
exactly four components. Build candidates by replacing only diagnosed fields.
Use deterministic callbacks for source-task and held-out-anchor evaluation, and
return the original baseline object when admission fails.

## Why

This makes the paper's bounded-recursion claim mechanically inspectable:
unrelated components preserve equality, failed patches cannot silently deploy,
and there is no API for changing a model, tool registry, localizer, or gate.

## Alternatives rejected

- **Mutable global dictionaries:** too easy for patches to escape their diagnosis.
- **Model self-evaluation:** violates maker/checker separation.
- **One scalar final reward:** cannot localize state, invocation, skill, or checker defects.
- **Full benchmark reproduction:** requires external environments and compute not included here.

## Rollback

Admission returns the baseline memory on rejection. Release rollback is a normal
git revert because generated traces are evidence artifacts, not runtime state.

