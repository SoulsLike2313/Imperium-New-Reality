#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "${SCRIPT_DIR}/../../.." && pwd)
REPORT_DIR="${REPO_ROOT}/IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-INDEPENDENT-REPLAY-AND-HEAD-CHAIN-RECONCILIATION-VM3-V0_1"

python3 "${SCRIPT_DIR}/run_review_target_alignment.py" \
  --repo-root "${REPO_ROOT}" \
  --report-dir "${REPORT_DIR}" \
  "$@"
