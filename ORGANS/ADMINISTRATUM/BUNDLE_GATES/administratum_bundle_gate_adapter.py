from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EVIDENCE = {"E1": 1, "E2": 2, "E3": 3, "E4": 4, "E5": 5, "E6": 6}


class AdministratumBundleGateAdapter:
    def __init__(self, policy_path: Path | None = None) -> None:
        path = policy_path or Path(__file__).with_name("bundle_gate_policy.json")
        self.policy = json.loads(path.read_text(encoding="utf-8-sig"))

    def review(self, bundle: dict[str, Any]) -> dict[str, Any]:
        missing = []
        for field in self.policy["mandatory_fields"]:
            value = bundle.get(field)
            if field not in bundle or value in (None, "", [], {}):
                missing.append(field)
        evidence = str(bundle.get("evidence_level", "E1")).upper()
        minimum = self.policy["minimum_evidence_level"]
        if EVIDENCE.get(evidence, 0) < EVIDENCE[minimum]:
            missing.append(f"evidence_level>={minimum}")
        verdict = "HELD" if missing else "RELEASED"
        return {
            "status": "PASS_WITH_WARNINGS",
            "verdict": verdict,
            "evidence_level": evidence,
            "minimum_evidence_level": minimum,
            "missing_fields": missing,
            "release_scope": "RELEASE_MANIFEST_ONLY",
            "automatic_kernel_promotion": False,
            "kernel_touched": False,
        }


def smoke() -> dict[str, Any]:
    gate = AdministratumBundleGateAdapter()
    held = gate.review({"task_id": "SMOKE-HELD", "goal": "test", "evidence_level": "E2"})
    released = gate.review({
        "task_id": "SMOKE-RELEASED",
        "goal": "test",
        "result_summary": "validated candidate manifest",
        "artifacts": ["artifact://smoke/release_manifest.json"],
        "evidence_level": "E3",
        "metrics": {"tests": 1},
    })
    passed = held["verdict"] == "HELD" and released["verdict"] == "RELEASED"
    return {
        "status": "PASS_WITH_WARNINGS" if passed else "BLOCKED",
        "held": held,
        "released": released,
        "automatic_kernel_promotion": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Administratum release-manifest gate")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--bundle")
    args = parser.parse_args(argv)
    if args.smoke:
        result = smoke()
    elif args.bundle:
        result = AdministratumBundleGateAdapter().review(
            json.loads(Path(args.bundle).read_text(encoding="utf-8-sig"))
        )
    else:
        result = {"status": "BLOCKED", "reason": "bundle_or_smoke_required"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
