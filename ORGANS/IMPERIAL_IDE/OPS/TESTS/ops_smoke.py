#!/usr/bin/env python3
"""ops_smoke - end-to-end smoke for the operational engine.

Proves the full loop runs and that the anti-fake-green gate actually bites:
  scenario 1: an incomplete report must be HELD;
  scenario 2: a complete, proof-carrying report must be RELEASED.
Exit code 0 only on PASS.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ENGINE = os.path.normpath(os.path.join(_HERE, "..", "ENGINE"))
if _ENGINE not in sys.path:
    sys.path.insert(0, _ENGINE)

from imperium_ops import (  # noqa: E402
    lifecycle,
    safety_gate,
    task_console,
    taskpack_builder as tpb,
)

EXPECTED_TASK_ID = "TASK-NEWREALITY-MECHANICUS-TOOL-MECHANICUS-TOOL-REGISTRY-EDITOR-PC-V0_1"
EXPECTED_SCENARIO1_MISSING = [
    "artifacts",
    "metrics",
    "receipts",
    "next_task_recommendation",
    "evidence_level too weak (E2 < E3)",
]

failures = []


def check(label, cond):
    status = "ok" if cond else "FAIL"
    print(f"  [{status}] {label}")
    if not cond:
        failures.append(label)


def main() -> int:
    repo = os.path.abspath(os.environ.get(
        "IMPERIUM_ROOT",
        os.path.join(_HERE, "..", "..", "..", ".."),
    ))
    out_root = os.path.join(repo, "ORGANS", "IMPERIAL_IDE", "OPS", "STAGING", "SMOKE_TESTS")

    print("== build intent ==")
    intent = task_console.new_task(
        title="Mechanicus tool registry editor",
        goal="Add a Mechanicus tool registry editor to the Imperial IDE",
        task_type=None,  # auto-classify
        scope="IMPERIAL_IDE",
        risk="CONTROLLED_WRITE",
        push_policy="VALIDATED_PUSH",
    )
    check(f"auto-classified as mechanicus_tool ({intent.task_type})",
          intent.task_type == "mechanicus_tool")
    check(f"task_id == {EXPECTED_TASK_ID}", intent.task_id == EXPECTED_TASK_ID)
    ok, problems = task_console.validate_intent(intent)
    check("validate_intent returns tuple ok/problems", ok is True and problems == [])

    print("== taskpack build ==")
    extracted = tpb.write_taskpack(out_root, intent)
    blockers = tpb.admission_precheck(extracted)
    check("admission precheck clean", blockers == [])
    zip_info = tpb.build_zip(extracted, os.path.join(out_root, intent.task_id, "TASKPACK.zip"))
    check(f"taskpack zip has at least 6 files ({zip_info['files']})", zip_info["files"] >= 6)
    check("sha256 is 64 hex chars", len(zip_info["sha256"]) == 64)
    with open(os.path.join(extracted, "MANIFEST.json"), "r", encoding="utf-8") as fh:
        import json
        manifest = json.load(fh)
    check("manifest schema is astronomicon.taskpack.v0_1",
          manifest.get("schema_version") == "astronomicon.taskpack.v0_1")
    check("manifest has cyrillic_in_taskpack field",
          "cyrillic_in_taskpack" in manifest.get("language_and_encoding_policy", {}))
    check("manifest has required_organs", bool(manifest.get("required_organs")))
    check("manifest has organ_route", bool(manifest.get("organ_route")))

    state = safety_gate.SafetyState()

    print("== scenario 1: incomplete report -> HELD ==")
    bad_report = {
        "task_id": intent.task_id,
        "result_summary": "claimed done",
        "evidence_level": "E2",
        "validation": {"result": "PASS"},
    }
    r1 = lifecycle.run_lifecycle(repo, intent, out_root, state=state,
                                 servitor_report=bad_report, dry_run=True)
    check("scenario1 verdict HELD", r1.verdict == "HELD")
    check(f"scenario1 stages == 15 ({len(r1.stages)})", len(r1.stages) == 15)
    check(f"scenario1 missing == expected ({r1.missing_lines})",
          r1.missing_lines == EXPECTED_SCENARIO1_MISSING)

    print("== scenario 2: complete report -> RELEASED ==")
    r2 = lifecycle.run_lifecycle(repo, intent, out_root, state=state,
                                 servitor_report=None, dry_run=True)
    check("scenario2 verdict RELEASED", r2.verdict == "RELEASED")
    check(f"scenario2 stages == 15 ({len(r2.stages)})", len(r2.stages) == 15)
    check(f"scenario2 missing == [] ({r2.missing_lines})", r2.missing_lines == [])
    check("scenario2 all stages OK", all(s.status == "OK" for s in r2.stages))

    print("== final report written ==")
    report_path = os.path.join(
        repo,
        "ORGANS",
        "IMPERIAL_IDE",
        "OPS",
        "STAGING",
        "REPORTS",
        intent.task_id,
        "lifecycle_report.json",
    )
    check("lifecycle_report.json exists", os.path.isfile(report_path))

    print()
    if failures:
        print(f"SMOKE RESULT: FAIL ({len(failures)} failed)")
        for f in failures:
            print(f"   - {f}")
        return 1
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
