# Agent Contract

## Start

1. Read `docs/IMPLEMENTATION-BRIEF.md` and `paper/claim-ledger.json`.
2. Read `feature_list.json` and `progress.md`.
3. Work on one active feature; do not broaden the paper-derived scope silently.

## Invariants

- Keep paper claims, local assumptions, implementation status, and measured results separate.
- Never treat a model assertion, tool attempt, or drafted action as completion evidence.
- Keep the outer harness fixed; patches may alter only explicitly diagnosed memory components.
- Never expose held-out evaluator internals to patch generation.
- Do not add network, credential, real-money, or deployment behavior without human approval.

## Done

Run `./init.sh`, inspect `evidence/demo-trace.json`, update `progress.md` and
`feature_list.json`, then inspect git status/diff. Passing tests prove the local
contract only—not the paper's benchmark claims.

