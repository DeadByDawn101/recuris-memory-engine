# Recuris Memory Engine

An independently authored, executable reference implementation of the bounded
Experiential–Working Memory architecture described in **“Recursive
Experiential–Working Memory Evolution for Long-Horizon Agent Harnesses”**
([arXiv:2608.24876v1](https://arxiv.org/abs/2608.24876v1)).

This repository is **not** an official author implementation, has no affiliation
with the paper's authors, and does **not** claim to reproduce the paper's reported
benchmark results. It tests architectural invariants disclosed in the paper.

## What it implements

- Compact goal-oriented working state: `pending`, `done`, or `blocked`
- Call-time and boundary-triggered, state-grounded skill invocation
- Evidence-gated state transitions with explicit checker decisions
- Append-only structured traces connecting state, skill selection, actions,
  observations, proposals, and checker outcomes
- Component-scoped patches over experiential memory, working-memory schema,
  invocation policy, and checker definitions
- Admission gates that require source repair without held-out anchor regression
- A fixed outer engine with no model mutation or unrestricted self-modification

## Run

```bash
./init.sh
PYTHONPATH=src python3 -m recuris_memory.cli --output evidence/demo-trace.json
```

The demo first attempts to mark a goal complete from an unexecuted draft. The
kernel rejects it. A later action with an environment receipt is accepted.

## Architecture

```text
verified working state + execution event
                  │
                  ▼
        state-grounded invocation
                  │
                  ▼
 action ──► environment observation ──► proposed state
                  │                         │
                  └────────► checker set ◄──┘
                                  │
                                  ▼
                         fixed commit kernel
                                  │
                                  ▼
                     state + structured trace

failed traces ─► diagnosis ─► scoped candidate patch ─► source + anchor gate
                                                        │
                                              admit or preserve baseline
```

See `docs/IMPLEMENTATION-BRIEF.md` for the paper-to-module mapping and
`paper/claim-ledger.json` for the evidence boundary.

## Safety boundary

This library has no network, wallet, exchange, credential, deployment, or
arbitrary file-mutation integration. Evaluators are supplied as deterministic
callbacks. Held-out evaluator internals never enter patch generation through
this API.

## License

RavenX-authored implementation code is MIT licensed. The cited paper and the
Harness Engineering course remain under their respective owners and licenses.

