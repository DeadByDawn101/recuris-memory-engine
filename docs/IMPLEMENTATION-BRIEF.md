# Implementation Brief: Recuris Reference Memory Engine

> Independent, clean-room reference implementation derived from the published description in arXiv:2608.24876v1. This is not the authors' implementation and does not reproduce their benchmark results.

## Sources

- Paper HTML: https://arxiv.org/html/2608.24876v1
- Paper PDF: https://arxiv.org/pdf/2608.24876v1
- Harness Engineering course: https://walkinglabs.github.io/learn-harness-engineering/en/
- Harness Engineering repository snapshot: walkinglabs/learn-harness-engineering at `77e7a3e21469dcbece2558086c8d91657abeaa40`
- Exact hashes are recorded in `source-manifest.json` and the parent report's `SOURCE-MANIFEST.txt`.

## Evidence boundary

Paper statements are treated as claims, not local measurements. Unit tests can establish conformance to the architecture described below; they cannot establish the paper's reported benchmark gains. No author source repository was identified in the paper HTML, so implementation code must be independently authored.

## Paper-derived architecture

The paper defines a fixed outer harness around a frozen model and a mutable memory-control layer:

`M_k = (E_k, W_k, rho_k, C_k)`

- `E` — experiential memory containing reusable skills.
- `W` — working-memory specification and task-local state.
- `rho` — invocation policy deciding when and which skills are delivered.
- `C` — checker set that validates proposed state changes against environment evidence.

Within a task:

1. Initialize compact goal state with `pending | done | blocked`, evidence, and optional blocker.
2. At a defined execution event, retrieve skills from current verified state rather than the full transcript.
3. Draft state-changing calls without executing them, inject applicable skills, then redraft/execute.
4. Propose a next working state after the observation.
5. A fixed kernel commits only transitions supported by an explicit checker.
6. Persist a structured trace joining state, invoked skills, action, observation, proposed state, and checker decisions.

Across tasks:

1. Localize failures from structured traces to one or more of `E`, `W`, `rho`, or `C`.
2. Patch only implicated components; copy all others unchanged.
3. Evaluate the candidate on the source failure and held-out anchor tasks.
4. Admit only if the source failure is repaired and the preset regression rule passes.
5. Keep the model, tools, localizer, patcher, gate, and outer harness fixed.

## Original implementation design

Package: `recuris_memory`

- `models.py` — immutable component/state/trace types and validation.
- `invocation.py` — call-time and boundary policies over state and event.
- `kernel.py` — evidence-grounded transition proposal and commit.
- `evolution.py` — component-scoped patches and validation-gated admission.
- `engine.py` — task-step coordinator producing append-only structured traces.
- `cli.py` — deterministic demo and JSON trace export.

## Invariants and test oracles

1. A goal never becomes `done` merely because an action or model claims success.
2. Rejected completion evidence leaves the goal unresolved and records the checker decision.
3. A state-changing draft is never treated as an executed action.
4. Invocation selection reads the verified working state and execution event.
5. Every trace entry contains pre-state, invoked skill IDs, action, observation, proposal, and checker decisions.
6. A candidate patch cannot modify a component absent from its diagnosed component set.
7. Rejected candidates leave the deployed memory byte-for-byte/structurally unchanged.
8. Held-out anchors participate only in admission, never patch generation.
9. Evolution is bounded to the memory-control layer; no model/tool/outer-harness mutation API exists.
10. Test-time adaptation is out of scope for the first reference release because a hidden-verifier benchmark environment is not available.

## Harness and design fusion

The repository follows the Harness Engineering five-subsystem model: concise instructions, external state, runnable verification, constrained feature scope, and session handoff. Maker and checker are separated by deterministic test oracles. The interface is a typed Python library and CLI rather than a decorative web UI; Tier-1/tri-archetype principles are applied as restraint, hierarchy, accessible output, strict validation, and production-safe defaults. No blockchain or live-financial surface is relevant or included.

## Non-goals

- Reproducing the four published benchmark suites or their numerical results.
- Implementing the paper authors' fixed Meta-Agent prompts, which are not fully specified here.
- Training or modifying a model.
- Autonomous mutation of arbitrary files, prompts, tools, or safety policy.
- Network, credential, wallet, exchange, or deployment connectivity.
