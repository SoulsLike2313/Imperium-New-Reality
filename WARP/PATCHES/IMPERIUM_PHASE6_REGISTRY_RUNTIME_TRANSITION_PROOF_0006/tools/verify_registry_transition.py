from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


REGISTRY_REL = (
    "ORGANS/MECHANICUS/REPORTS/"
    "IMPERIUM-CORE-REFERENCE-CORRIDOR-0001/CAPABILITY_REGISTRY.json"
)
DIAGNOSTIC_ID = "CORE_DIAGNOSTIC"


class TransitionError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TransitionError(f"expected object: {path}")
    return value


def _git_blob(repo: Path, head: str, relative: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo), "show", f"{head}:{relative}"],
        shell=False,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise TransitionError(
            completed.stderr.decode("utf-8", errors="replace").strip()
            or "git show failed"
        )
    return completed.stdout


def _canonical_digest(value: dict[str, Any]) -> str:
    clone = copy.deepcopy(value)
    clone.pop("registry_digest", None)
    payload = json.dumps(
        clone,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _capability(registry: dict[str, Any], capability_id: str) -> dict[str, Any]:
    matches = [
        item
        for item in registry.get("capabilities", [])
        if isinstance(item, dict) and item.get("capability_id") == capability_id
    ]
    if len(matches) != 1:
        raise TransitionError(
            f"expected exactly one {capability_id}, got {len(matches)}"
        )
    return matches[0]


def _iso_utc(value: Any) -> str:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise TransitionError("new diagnostic timestamp is not UTC Z form")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise TransitionError("new diagnostic timestamp is invalid") from exc
    return value


def verify_transition(
    *,
    baseline_registry: dict[str, Any],
    current_registry: dict[str, Any],
    baseline_live_ids: list[str],
    current_live_ids: list[str],
) -> dict[str, Any]:
    before_ids = set(baseline_live_ids)
    after_ids = set(current_live_ids)
    new_ids = sorted(after_ids - before_ids)
    removed_ids = sorted(before_ids - after_ids)

    if len(new_ids) != 1:
        raise TransitionError(f"expected one new live evidence, got {new_ids}")
    if removed_ids:
        raise TransitionError(f"historical live evidence removed: {removed_ids}")

    new_evidence_id = new_ids[0]
    before_diag = _capability(baseline_registry, DIAGNOSTIC_ID)
    after_diag = _capability(current_registry, DIAGNOSTIC_ID)

    before_validation = before_diag.get("last_validation")
    after_validation = after_diag.get("last_validation")
    if not isinstance(before_validation, dict):
        raise TransitionError("baseline diagnostic last_validation is not an object")
    if not isinstance(after_validation, dict):
        raise TransitionError("current diagnostic last_validation is not an object")

    before_evidence_id = before_validation.get("evidence_id")
    after_evidence_id = after_validation.get("evidence_id")
    if before_evidence_id not in before_ids:
        raise TransitionError(
            "baseline diagnostic binding is not one of baseline live evidence IDs"
        )
    if after_evidence_id != new_evidence_id:
        raise TransitionError(
            f"current diagnostic binding {after_evidence_id!r} "
            f"does not equal new evidence {new_evidence_id!r}"
        )
    if before_validation.get("verdict") != "PASS_PROVEN":
        raise TransitionError("baseline diagnostic verdict is not PASS_PROVEN")
    if after_validation.get("verdict") != "PASS_PROVEN":
        raise TransitionError("current diagnostic verdict is not PASS_PROVEN")
    new_timestamp = _iso_utc(after_validation.get("timestamp_utc"))

    expected = copy.deepcopy(baseline_registry)
    expected_diag = _capability(expected, DIAGNOSTIC_ID)
    expected_diag["last_validation"] = copy.deepcopy(after_validation)
    expected["registry_digest"] = current_registry.get("registry_digest")

    if expected != current_registry:
        raise TransitionError(
            "registry changed outside CORE_DIAGNOSTIC.last_validation "
            "and registry_digest"
        )

    expected_digest = _canonical_digest(current_registry)
    observed_digest = current_registry.get("registry_digest")
    if observed_digest != expected_digest:
        raise TransitionError(
            f"registry digest mismatch: observed={observed_digest}, "
            f"expected={expected_digest}"
        )

    return {
        "verdict": "EXACT_RUNTIME_REGISTRY_TRANSITION_PROVEN",
        "historical_evidence_id": before_evidence_id,
        "new_evidence_id": new_evidence_id,
        "live_count_before": len(before_ids),
        "live_count_after": len(after_ids),
        "old_last_validation": before_validation,
        "new_last_validation": after_validation,
        "new_timestamp_utc": new_timestamp,
        "registry_digest_before": baseline_registry.get("registry_digest"),
        "registry_digest_after": observed_digest,
        "allowed_semantic_changes": [
            "CORE_DIAGNOSTIC.last_validation.evidence_id",
            "CORE_DIAGNOSTIC.last_validation.timestamp_utc",
            "registry_digest",
        ],
        "all_other_registry_fields_unchanged": True,
    }


def _self_test() -> None:
    before = {
        "capabilities": [
            {
                "capability_id": DIAGNOSTIC_ID,
                "last_validation": {
                    "evidence_id": "UI_DIAGNOSTIC_OLD",
                    "verdict": "PASS_PROVEN",
                    "timestamp_utc": "2026-07-14T12:00:00Z",
                },
            },
            {"capability_id": "OTHER", "value": 7},
        ]
    }
    before["registry_digest"] = _canonical_digest(before)

    after = copy.deepcopy(before)
    diag = _capability(after, DIAGNOSTIC_ID)
    diag["last_validation"] = {
        "evidence_id": "UI_DIAGNOSTIC_NEW",
        "verdict": "PASS_PROVEN",
        "timestamp_utc": "2026-07-14T13:00:00Z",
    }
    after["registry_digest"] = _canonical_digest(after)

    result = verify_transition(
        baseline_registry=before,
        current_registry=after,
        baseline_live_ids=["UI_DIAGNOSTIC_OLD"],
        current_live_ids=["UI_DIAGNOSTIC_OLD", "UI_DIAGNOSTIC_NEW"],
    )
    assert result["new_evidence_id"] == "UI_DIAGNOSTIC_NEW"

    bad = copy.deepcopy(after)
    _capability(bad, "OTHER")["value"] = 8
    bad["registry_digest"] = _canonical_digest(bad)
    try:
        verify_transition(
            baseline_registry=before,
            current_registry=bad,
            baseline_live_ids=["UI_DIAGNOSTIC_OLD"],
            current_live_ids=["UI_DIAGNOSTIC_OLD", "UI_DIAGNOSTIC_NEW"],
        )
    except TransitionError:
        pass
    else:
        raise AssertionError("unexpected registry mutation was not rejected")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo")
    parser.add_argument("--head")
    parser.add_argument("--registry")
    parser.add_argument("--baseline")
    parser.add_argument("--live-index")
    parser.add_argument("--receipt")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        _self_test()
        print("SELF_TEST: PASS")
        return 0

    required = {
        "repo": args.repo,
        "head": args.head,
        "registry": args.registry,
        "baseline": args.baseline,
        "live_index": args.live_index,
        "receipt": args.receipt,
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise SystemExit(f"missing arguments: {missing}")

    repo = Path(args.repo).resolve()
    registry_path = Path(args.registry).resolve()
    baseline_path = Path(args.baseline).resolve()
    live_index_path = Path(args.live_index).resolve()
    receipt_path = Path(args.receipt).resolve()

    baseline = _load(baseline_path)
    if baseline.get("implementation_head") != args.head:
        raise TransitionError("baseline is not bound to the current committed HEAD")

    baseline_blob = _git_blob(repo, args.head, REGISTRY_REL)
    baseline_registry = json.loads(baseline_blob.decode("utf-8"))
    current_registry = _load(registry_path)
    live_index = _load(live_index_path)

    baseline_ids = baseline.get("live_evidence_ids", [])
    current_entries = live_index.get("entries", {})
    if not isinstance(baseline_ids, list):
        raise TransitionError("baseline live evidence IDs are invalid")
    if not isinstance(current_entries, dict):
        raise TransitionError("current live evidence index entries are invalid")

    result = verify_transition(
        baseline_registry=baseline_registry,
        current_registry=current_registry,
        baseline_live_ids=[str(item) for item in baseline_ids],
        current_live_ids=sorted(str(item) for item in current_entries),
    )
    result.update(
        {
            "schema_version": (
                "imperium.phase6_registry_runtime_transition_receipt.v1"
            ),
            "implementation_head": args.head,
            "registry_path": str(registry_path),
            "registry_blob_sha256_before": hashlib.sha256(
                baseline_blob
            ).hexdigest(),
            "registry_file_sha256_after": _sha256(registry_path),
            "baseline_path": str(baseline_path),
            "live_index_path": str(live_index_path),
        }
    )

    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
