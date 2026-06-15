#!/usr/bin/env python3
"""Validate NewGen Visual Brain Task Corridor V0.1 artifacts."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-VISUAL-BRAIN-TASK-CORRIDOR-PC-V0_1"
FORBIDDEN_PATH_PREFIXES = ("ORGANS/", "SANCTUM/", "IMPERIUM_TEST_VERSION/", ".github/", ".git/")
REQUIRED_NODE_IDS = {
    "owner_intent",
    "astronomicon",
    "officio_agentis",
    "doctrinarium",
    "administratum",
    "mechanicus",
    "inquisition",
    "strategium",
    "schola_imperialis",
    "servitor_core",
    "evidence_binder",
    "owner_verdict_gate",
}
REQUIRED_WARNING_MARKERS = {
    "READ_ONLY_LAB",
    "FOUNDATION_ONLY",
    "NO LIVE BACKEND",
    "NO LIVE AUTONOMOUS ORGAN DIALOGUE PROVEN",
    "GREEN REQUIRES RECEIPT",
}
FORBIDDEN_CLAIMS = {
    "production orchestration is ready",
    "live autonomous execution is proven",
    "live organ dialogue is proven",
}


@dataclass
class CheckResult:
    check_id: str
    status: str
    details: str

    def as_dict(self) -> dict[str, str]:
        return {"check_id": self.check_id, "status": self.status, "details": self.details}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Visual Brain Task Corridor V0.1.")
    parser.add_argument("--repo-root", default="E:\\IMPERIUM")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--out", default="")
    return parser.parse_args()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_changed_paths_report(path: Path) -> list[str]:
    if not path.exists():
        return []
    changed: list[str] = []
    capture = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line == "BEGIN_CHANGED_PATHS":
            capture = True
            continue
        if line == "END_CHANGED_PATHS":
            capture = False
            continue
        if capture and line:
            changed.append(line.replace("\\", "/"))
    return changed


def parse_git_status_paths(repo_root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    result: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            result.append(path.replace("\\", "/"))
    return result


def forbidden_hits(paths: list[str]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        for prefix in FORBIDDEN_PATH_PREFIXES:
            if path.startswith(prefix):
                hits.append(path)
                break
    return sorted(set(hits))


def required_paths(repo_root: Path, task_id: str) -> dict[str, Path]:
    report = repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS" / task_id
    return {
        "architecture_doc": repo_root / "IMPERIUM_NEW_GENERATION/ARCHITECTURE/VISUAL_BRAIN_TASK_CORRIDOR_V0_1.md",
        "state_schema": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/VISUAL_BRAIN/VISUAL_BRAIN_TASK_CORRIDOR_STATE_V0_1.schema.json",
        "state_sample": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/VISUAL_BRAIN/EXAMPLES/SAMPLE_VISUAL_BRAIN_TASK_CORRIDOR_STATE_V0_1.json",
        "lab_readme": repo_root / "IMPERIUM_NEW_GENERATION/VISUAL_BRAIN/TASK_CORRIDOR_V0_1/README.md",
        "lab_index": repo_root / "IMPERIUM_NEW_GENERATION/VISUAL_BRAIN/TASK_CORRIDOR_V0_1/index.html",
        "lab_styles": repo_root / "IMPERIUM_NEW_GENERATION/VISUAL_BRAIN/TASK_CORRIDOR_V0_1/styles.css",
        "lab_js": repo_root / "IMPERIUM_NEW_GENERATION/VISUAL_BRAIN/TASK_CORRIDOR_V0_1/visual_brain_task_corridor.js",
        "lab_generated_state": repo_root
        / "IMPERIUM_NEW_GENERATION/VISUAL_BRAIN/TASK_CORRIDOR_V0_1/data/visual_brain_task_corridor_state.generated.json",
        "builder": repo_root / "IMPERIUM_NEW_GENERATION/TOOLS/VISUAL_BRAIN/build_visual_brain_task_corridor_v0_1.py",
        "validator": repo_root
        / "IMPERIUM_NEW_GENERATION/TOOLS/VALIDATORS/newgen_visual_brain_task_corridor_validator_v0_1.py",
        "gate_ack": report / "GATE_ACK.md",
        "officio_ack": report / "OFFICIO_ROLE_ACK_OR_WARN.json",
        "doctr_ack": report / "DOCTRINARIUM_LAW_ACK_OR_WARN.json",
        "skeptic_ack": report / "SUPER_SKEPTICISM_ACK.json",
        "step_proof": report / "STEP_PROOF_RECORDS.jsonl",
        "changed_files": report / "CHANGED_FILES_STATUS.md",
        "owner_report": report / "OWNER_REPORT_RU.md",
        "final_receipt": report / "FINAL_RECEIPT.json",
        "validator_report": report / "VALIDATOR_REPORT.json",
    }


def validate_visual_state(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []

    if data.get("schema_version") != "0.1":
        errors.append("schema_version must be 0.1")
    if data.get("foundation_only") is not True:
        errors.append("foundation_only must be true")
    if data.get("production_ready") is not False:
        errors.append("production_ready must be false")
    if data.get("live_autonomous_organ_dialogue_proven") is not False:
        errors.append("live_autonomous_organ_dialogue_proven must be false")
    if data.get("mode") not in {"READ_ONLY_LAB", "FOUNDATION_ONLY"}:
        errors.append("mode must be READ_ONLY_LAB or FOUNDATION_ONLY")

    node_ids = set()
    nodes = data.get("nodes")
    if not isinstance(nodes, list):
        errors.append("nodes must be array")
        nodes = []
    for idx, node in enumerate(nodes, start=1):
        if not isinstance(node, dict):
            errors.append(f"nodes[{idx}] must be object")
            continue
        node_id = str(node.get("node_id", "")).strip()
        if not node_id:
            errors.append(f"nodes[{idx}] missing node_id")
            continue
        node_ids.add(node_id)
        status = str(node.get("status", ""))
        evidence_ref = str(node.get("evidence_ref", "")).strip()
        if status == "PROVED_BY_RECEIPT" and not evidence_ref:
            errors.append(f"nodes[{idx}] PROVED_BY_RECEIPT missing evidence_ref")
    missing_nodes = REQUIRED_NODE_IDS - node_ids
    if missing_nodes:
        errors.append("missing required node ids: " + ", ".join(sorted(missing_nodes)))

    edges = data.get("edges")
    if not isinstance(edges, list):
        errors.append("edges must be array")
        edges = []
    for idx, edge in enumerate(edges, start=1):
        if not isinstance(edge, dict):
            errors.append(f"edges[{idx}] must be object")
            continue
        status = str(edge.get("status", ""))
        evidence_ref = str(edge.get("evidence_ref", "")).strip()
        if status == "PROVED_BY_RECEIPT" and not evidence_ref:
            errors.append(f"edges[{idx}] PROVED_BY_RECEIPT missing evidence_ref")

    run_rail = data.get("run_rail")
    if not isinstance(run_rail, list):
        errors.append("run_rail must be array")
        run_rail = []
    for idx, step in enumerate(run_rail, start=1):
        if not isinstance(step, dict):
            errors.append(f"run_rail[{idx}] must be object")
            continue
        status = str(step.get("status", ""))
        evidence_ref = str(step.get("evidence_ref", "")).strip()
        if status == "PROVED_BY_RECEIPT" and not evidence_ref:
            errors.append(f"run_rail[{idx}] PROVED_BY_RECEIPT missing evidence_ref")

    warnings = data.get("warnings")
    if not isinstance(warnings, list):
        errors.append("warnings must be array")
    else:
        marker_set = {str(x) for x in warnings}
        missing_warn_markers = REQUIRED_WARNING_MARKERS - marker_set
        if missing_warn_markers:
            warns.append("warnings missing markers: " + ", ".join(sorted(missing_warn_markers)))

        source_records = data.get("source_records")
        if isinstance(source_records, list):
            if any(isinstance(r, dict) and str(r.get("status")) != "READ" for r in source_records):
                if not any(str(x).startswith("MISSING_INPUT_WARN:") for x in warnings):
                    errors.append("warnings must include MISSING_INPUT_WARN:* markers for missing/read_error sources")

    forbidden_claims = data.get("forbidden_claims")
    if not isinstance(forbidden_claims, list):
        errors.append("forbidden_claims must be array")
    else:
        claim_set = {str(x) for x in forbidden_claims}
        missing_claims = FORBIDDEN_CLAIMS - claim_set
        if missing_claims:
            errors.append("forbidden_claims missing required items: " + ", ".join(sorted(missing_claims)))

    return errors, warns


def check_local_only_lab(index_html: Path, css: Path, js_path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    targets = [index_html, css, js_path]
    for target in targets:
        text = target.read_text(encoding="utf-8", errors="ignore").lower()
        if "http://" in text or "https://" in text:
            errors.append(f"{target.as_posix()} contains external http(s) reference")
        if "cdn" in text or "npm " in text or "playwright" in text or "storybook" in text:
            warns.append(f"{target.as_posix()} contains keyword requiring manual review")
    return errors, warns


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    task_id = args.task_id
    paths = required_paths(repo_root, task_id)
    out_path = Path(args.out).resolve() if args.out else paths["validator_report"]

    checks: list[CheckResult] = []
    blockers: list[str] = []
    warnings: list[str] = []

    missing = [f"{k}: {v.as_posix()}" for k, v in paths.items() if k != "validator_report" and not v.exists()]
    checks.append(
        CheckResult(
            "required_file_exists",
            "PASS" if not missing else "BLOCK",
            "all required files exist" if not missing else "; ".join(missing),
        )
    )
    if missing:
        blockers.extend(missing)

    parse_targets = [
        paths["state_schema"],
        paths["state_sample"],
        paths["officio_ack"],
        paths["doctr_ack"],
        paths["skeptic_ack"],
        paths["final_receipt"],
    ]
    parse_errors: list[str] = []
    for target in parse_targets:
        if not target.exists():
            continue
        try:
            read_json(target)
        except Exception as exc:  # pragma: no cover
            parse_errors.append(f"{target.as_posix()}: {exc}")
    checks.append(
        CheckResult(
            "json_parseability",
            "PASS" if not parse_errors else "BLOCK",
            "json parse checks passed" if not parse_errors else "; ".join(parse_errors),
        )
    )
    if parse_errors:
        blockers.extend(parse_errors)

    builder_cmd = [
        sys.executable,
        str(paths["builder"]),
        "--repo-root",
        str(repo_root),
        "--task-id",
        task_id,
    ]
    run = subprocess.run(builder_cmd, text=True, capture_output=True, check=False)
    builder_ok = run.returncode == 0
    checks.append(
        CheckResult(
            "builder_run",
            "PASS" if builder_ok else "BLOCK",
            "builder generated state" if builder_ok else f"returncode={run.returncode}; stderr={run.stderr.strip()}",
        )
    )
    if not builder_ok:
        blockers.append("builder failed: " + (run.stderr.strip() or run.stdout.strip() or "unknown error"))

    if not paths["lab_generated_state"].exists():
        blockers.append("generated visual state file missing")
    checks.append(
        CheckResult(
            "generated_state_exists",
            "PASS" if paths["lab_generated_state"].exists() else "BLOCK",
            str(paths["lab_generated_state"]),
        )
    )

    visual_state: dict[str, Any] = {}
    if not blockers:
        generated = read_json(paths["lab_generated_state"])
        if not isinstance(generated, dict):
            blockers.append("generated visual state must be JSON object")
        else:
            visual_state = generated
            shape_errors, shape_warns = validate_visual_state(visual_state)
            blockers.extend(shape_errors)
            warnings.extend(shape_warns)
    checks.append(
        CheckResult(
            "state_shape_no_fake_green",
            "PASS" if not blockers else "BLOCK",
            "state structure and truth-bound checks passed" if not blockers else "see blockers",
        )
    )

    local_errors, local_warns = check_local_only_lab(paths["lab_index"], paths["lab_styles"], paths["lab_js"])
    checks.append(
        CheckResult(
            "local_only_static_lab",
            "PASS" if not local_errors else "BLOCK",
            "local static lab has no external references" if not local_errors else "; ".join(local_errors),
        )
    )
    blockers.extend(local_errors)
    warnings.extend(local_warns)

    changed_report_paths = parse_changed_paths_report(paths["changed_files"])
    report_forbidden = forbidden_hits(changed_report_paths)
    checks.append(
        CheckResult(
            "forbidden_paths_not_in_changed_report",
            "PASS" if not report_forbidden else "BLOCK",
            "no forbidden paths in changed files report"
            if not report_forbidden
            else "; ".join(report_forbidden),
        )
    )
    if report_forbidden:
        blockers.extend([f"forbidden path in changed report: {x}" for x in report_forbidden])

    status_forbidden = forbidden_hits(parse_git_status_paths(repo_root))
    checks.append(
        CheckResult(
            "forbidden_paths_not_in_git_status",
            "PASS" if not status_forbidden else "BLOCK",
            "no forbidden paths in git status" if not status_forbidden else "; ".join(status_forbidden),
        )
    )
    if status_forbidden:
        blockers.extend([f"forbidden path in git status: {x}" for x in status_forbidden])

    verdict = "BLOCK" if blockers else ("WARN" if warnings else "PASS")
    report = {
        "schema_version": "0.1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": [c.as_dict() for c in checks],
        "warnings": sorted(set(warnings)),
        "blockers": sorted(set(blockers)),
        "builder_command": " ".join(builder_cmd),
        "no_fake_green_note": (
            "Validator PASS/WARN proves bounded static/read-only corridor integrity only. "
            "It does not prove production Visual Brain or live autonomous organ dialogue."
        ),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out_path.as_posix())
    print(f"verdict={verdict}")
    return 1 if verdict == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
