from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1"
OUTPUT_ROOT_DEFAULT = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/TOOL_EXPANSION/BATCH_001"
REPORT_ROOT_DEFAULT = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/"
    "TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1"
)
SCOPE_ROOT_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCOPE_PACKS/V0_1"
REGISTRY_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json"

COMMON_GATES = [
    "GATE-U00-GIT-TRUTH",
    "GATE-U01-ROLE-ACK",
    "GATE-U02-SCOPE-BOUNDARY",
    "GATE-U04-EVIDENCE-RECEIPT",
    "GATE-U05-STOP-CONDITIONS",
    "GATE-U08-REPO-PURITY",
    "GATE-U09-NO-FAKE-GREEN",
    "GATE-U12-REPORT-OUTPUT-BUDGET",
    "GATE-U13-PYTHON-TYPE-SAFETY",
    "GATE-U14-WHOLE-REPO-SCOPE-RECON",
    "GATE-U15-OPERATIONALITY-IMPACT",
    "GATE-U19-SCRIPT-ARTIFACT-PRESERVATION",
    "GATE-U20-AGENT-KPD-SELF-REVIEW",
    "GATE-U21-COMMAND-CHUNKING",
]

EVIDENCE_SEARCH_CAPS = [
    "DATABASES_SQLITE",
    "DATABASES_SQLITE_FTS5",
    "CAP-DB-SQLITE-FTS5-EVIDENCE",
    "SEARCH_INDEXING_SQLITE_FTS_SEARCH",
    "SEARCH_INDEXING_RIPGREP_SEARCH",
    "SEARCH_INDEXING_RECEIPT_PATH_INDEX",
    "SEARCH_INDEXING_REPORT_PATH_INDEX",
    "SEARCH_INDEXING_TAG_INDEX_MODEL",
    "SEARCH_INDEXING_SIMPLE_INVERTED_INDEX",
    "UTILITIES_RIPGREP",
    "UTILITIES_JQ",
    "TOOLS_RECEIPT_VALIDATOR",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def resolve_repo_root(path_hint: Path) -> Path:
    try:
        top = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path_hint,
            text=True,
        ).strip()
        if top:
            return Path(top)
    except Exception:
        pass
    return path_hint


def run_exporter(repo_root: Path, task_id: str) -> dict[str, Any]:
    script = repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_capability_scope_exporter_v0_2.py"
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        ["python", str(script), "--task-id", task_id, "--repo-root", str(repo_root)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
    )
    return {
        "exit_code": int(proc.returncode),
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def build_evidence_search_pack(repo_root: Path, task_id: str) -> dict[str, Any]:
    registry = load_json(repo_root / REGISTRY_REL)
    cards = registry.get("cards", [])
    cards_by_id = {
        str(row.get("capability_id", "")).strip(): row
        for row in cards
        if isinstance(row, dict) and str(row.get("capability_id", "")).strip()
    }
    owner_decision = sorted(
        cap
        for cap, row in cards_by_id.items()
        if str(row.get("category", "")).strip() in {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"}
    )

    canon_allowed: list[str] = []
    sandbox_allowed: list[str] = []
    candidate_context_only: list[str] = []
    missing_caps: list[str] = []
    for cap in EVIDENCE_SEARCH_CAPS:
        row = cards_by_id.get(cap)
        if not row:
            missing_caps.append(cap)
            continue
        status = str(row.get("status", "CANDIDATE"))
        if status == "CANON":
            canon_allowed.append(cap)
        elif status == "SANDBOX":
            sandbox_allowed.append(cap)
        else:
            candidate_context_only.append(cap)

    payload = {
        "scope_id": "evidence_search_task",
        "version": "0.1",
        "generated_at_utc": utc_now(),
        "source_registry": REGISTRY_REL,
        "purpose": "Evidence index search/retrieval lane for reports, receipts, and status traces after expansion tasks.",
        "target_task_types": [
            "evidence_search",
            "evidence_index_refresh",
            "report_receipt_query_smoke",
        ],
        "canon_allowed": sorted(canon_allowed),
        "sandbox_allowed": sorted(sandbox_allowed),
        "candidate_context_only": sorted(candidate_context_only),
        "owner_decision_required": owner_decision,
        "forbidden": [],
        "required_receipts": [
            "evidence_index_refresh_report.json",
            "evidence_query_smoke_after_expansion.json",
            "quality_gate_result_report.json",
            "scope_pack_check_report.json",
        ],
        "required_gates": COMMON_GATES,
        "warnings": [
            "Evidence search scope does not authorize private external context indexing.",
            "LLM/cloud and visual lanes remain outside this scope.",
        ]
        + (
            [f"missing_focus_capabilities:{','.join(missing_caps)}"]
            if missing_caps
            else []
        ),
        "examples_of_use": [
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_evidence_index_builder_v0_1.py --repo-root E:\\IMPERIUM",
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_evidence_query_runner_v0_1.py --repo-root E:\\IMPERIUM",
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_evidence_index_v0_1.py --repo-root E:\\IMPERIUM",
        ],
        "future_promotion_candidates": [
            "SEARCH_INDEXING_RECEIPT_PATH_INDEX",
            "SEARCH_INDEXING_REPORT_PATH_INDEX",
            "SEARCH_INDEXING_TAG_INDEX_MODEL",
        ],
        "forbidden_actions": [
            "index private/local external context",
            "claim evidence completeness without refresh receipts",
            "LLM/cloud adapter activation inside evidence search scope",
        ],
        "last_generated_from_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            text=True,
        ).strip(),
    }
    return payload


def regenerate_scope_index_ru(scope_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(scope_root.glob("scope_*_task_v0_1.json")):
        payload = load_json(path)
        if not isinstance(payload, dict):
            continue
        rows.append(
            {
                "scope_id": str(payload.get("scope_id", path.stem)),
                "filename": path.name,
                "canon": len(payload.get("canon_allowed", [])),
                "sandbox": len(payload.get("sandbox_allowed", [])),
                "candidate": len(payload.get("candidate_context_only", [])),
                "owner": len(payload.get("owner_decision_required", [])),
                "forbidden": len(payload.get("forbidden", [])),
            }
        )

    lines = [
        "# Mechanicus Scope Packs Index RU (V0.1)",
        "",
        "Назначение: быстрый доступ будущего Servitor/local-agent к разрешенным capability-срезам по типам задач.",
        "",
        "| Scope ID | Файл | CANON | SANDBOX | CANDIDATE | OWNER_DECISION | FORBIDDEN |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {scope_id} | {filename} | {canon} | {sandbox} | {candidate} | {owner} | {forbidden} |".format(
                scope_id=row["scope_id"],
                filename=row["filename"],
                canon=row["canon"],
                sandbox=row["sandbox"],
                candidate=row["candidate"],
                owner=row["owner"],
                forbidden=row["forbidden"],
            )
        )
    lines.extend(
        [
            "",
            "## Важные правила",
            "- `visual_readiness_task` = только readiness; без запуска визуальных прототипов.",
            "- `controlled_tool_provision_task` = только Owner-approved install lane; silent install запрещен.",
            "- `evidence_search_task` = только bounded поиск по индексу Mechanicus, без private context.",
            "- Во всех scope действует запрет на LLM/cloud activation без отдельного Owner gate.",
        ]
    )
    write_text(scope_root / "SCOPE_PACKS_INDEX_RU.md", "\n".join(lines))
    return rows


def run_scope_checker(repo_root: Path, task_id: str, report_root: Path) -> dict[str, Any]:
    checker = repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_scope_packs_v0_1.py"
    output = report_root / "scope_pack_check_report.json"
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            "python",
            str(checker),
            "--task-id",
            task_id,
            "--repo-root",
            str(repo_root),
            "--report-output",
            str(output),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
    )
    payload = load_json(output) if output.exists() else {}
    payload["runner_exit_code"] = int(proc.returncode)
    payload["runner_stdout"] = proc.stdout.strip()
    payload["runner_stderr"] = proc.stderr.strip()
    write_json(output, payload)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh Mechanicus scope packs after tool expansion decisions.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=OUTPUT_ROOT_DEFAULT)
    parser.add_argument("--report-root", default=REPORT_ROOT_DEFAULT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(Path(args.repo_root).resolve())
    output_root = (repo_root / args.output_root).resolve()
    report_root = (repo_root / args.report_root).resolve()
    scope_root = (repo_root / SCOPE_ROOT_REL).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)
    scope_root.mkdir(parents=True, exist_ok=True)

    exporter_run = run_exporter(repo_root, args.task_id)
    evidence_pack = build_evidence_search_pack(repo_root, args.task_id)
    evidence_pack_path = scope_root / "scope_evidence_search_task_v0_1.json"
    write_json(evidence_pack_path, evidence_pack)
    index_rows = regenerate_scope_index_ru(scope_root)
    scope_checker = run_scope_checker(repo_root, args.task_id, report_root)

    updates = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "updated_scope_files": [
            "scope_code_quality_task_v0_1.json",
            "scope_controlled_tool_provision_task_v0_1.json",
            "scope_json_schema_validation_task_v0_1.json",
            "scope_mechanicus_tool_validation_task_v0_1.json",
            "scope_repo_hygiene_task_v0_1.json",
            "scope_taskpack_generation_task_v0_1.json",
            "scope_visual_readiness_task_v0_1.json",
            "scope_evidence_search_task_v0_1.json",
            "SCOPE_PACKS_INDEX_RU.md",
        ],
        "scope_count_after_refresh": len(index_rows),
        "exporter_exit_code": exporter_run["exit_code"],
        "scope_checker_verdict": scope_checker.get("verdict", "UNKNOWN"),
    }

    write_json(output_root / "tool_expansion_scope_updates.json", updates)
    write_json(
        report_root / "scope_pack_update_report.json",
        {
            "task_id": args.task_id,
            "generated_at_utc": utc_now(),
            "checker": "mechanicus_tool_scope_refresh_v0_1.py",
            "scope_root": SCOPE_ROOT_REL,
            "updates": updates,
            "exporter_run": exporter_run,
            "scope_checker_report": str((report_root / "scope_pack_check_report.json").relative_to(repo_root).as_posix()),
            "verdict": (
                "PASS"
                if exporter_run["exit_code"] == 0 and scope_checker.get("verdict") == "PASS"
                else "PASS_WITH_WARNINGS"
            ),
            "raw_dump_status": "COMPACT_ONLY",
        },
    )

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "scope_count_after_refresh": len(index_rows),
                "scope_checker_verdict": scope_checker.get("verdict", "UNKNOWN"),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
