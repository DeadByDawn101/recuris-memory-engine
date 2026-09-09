#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="${PWD}/src${PYTHONPATH:+:${PYTHONPATH}}"
python3 -m compileall -q src tests
python3 -m unittest discover -s tests -v
python3 -m recuris_memory.cli --output evidence/demo-trace.json
python3 - <<'PY'
import json
from pathlib import Path

trace = json.loads(Path("evidence/demo-trace.json").read_text())
assert trace["final_state"]["goals"][0]["status"] == "done"
assert trace["trace"][0]["checker_decisions"][0]["accepted"] is False
assert trace["trace"][1]["checker_decisions"][0]["accepted"] is True
print("smoke: evidence-gated transition verified")
PY

