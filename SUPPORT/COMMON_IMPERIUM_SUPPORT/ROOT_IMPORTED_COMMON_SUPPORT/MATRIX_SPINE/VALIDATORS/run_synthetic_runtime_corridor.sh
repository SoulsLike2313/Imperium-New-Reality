#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "${SCRIPT_DIR}/../../.." && pwd)
OUTPUT_DIR="${REPO_ROOT}/IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-GATE-VM3-V0_1"

python3 "${SCRIPT_DIR}/run_synthetic_runtime_corridor.py" \
  --repo-root "${REPO_ROOT}" \
  --output-dir "${OUTPUT_DIR}" \
  "$@"
