from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1"
OUTPUT_ROOT_DEFAULT = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/TOOL_EXPANSION/BATCH_001"
REPORT_ROOT_DEFAULT = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/"
    "TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1"
)
REGISTRY_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json"


@dataclass(frozen=True)
class CandidateSpec:
    tool_id: str
    name: str
    category: str
    candidate_group: str
    detection_commands: tuple[str, ...]
    value_level: str
    risk_level: str
    plus: tuple[str, ...]
    minus: tuple[str, ...]
    preferred_action: str
    owner_approval_required: bool
    proposed_install_command: str
    notes: str


CANDIDATES: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        tool_id="UTILITIES_RIPGREP",
        name="ripgrep",
        category="UTILITIES",
        candidate_group="SEARCH_CODE_NAVIGATION",
        detection_commands=("rg --version",),
        value_level="CRITICAL",
        risk_level="LOW",
        plus=("Fast repo-wide search.", "Already used in Mechanicus workflows."),
        minus=("External binary dependency.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="winget install BurntSushi.ripgrep",
        notes="Primary search accelerator for reports/receipts/card lookup.",
    ),
    CandidateSpec(
        tool_id="SEARCH_INDEXING_RIPGREP_SEARCH",
        name="ripgrep search workflow",
        category="SEARCH_INDEXING",
        candidate_group="SEARCH_CODE_NAVIGATION",
        detection_commands=(
            "rg --files IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS | head -n 3",
            "rg --files IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS",
        ),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Gives high-density evidence discovery.",),
        minus=("Depends on ripgrep binary availability.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="winget install BurntSushi.ripgrep",
        notes="Search-indexing lane backed by real report folders.",
    ),
    CandidateSpec(
        tool_id="UTILITIES_FD",
        name="fd",
        category="UTILITIES",
        candidate_group="SEARCH_CODE_NAVIGATION",
        detection_commands=("fd --version", "fdfind --version"),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Very fast file traversal.",),
        minus=("Alternative command names on Windows/Linux.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="winget install sharkdp.fd",
        notes="Complements ripgrep for path-first exploration.",
    ),
    CandidateSpec(
        tool_id="LANGUAGES_POWERSHELL",
        name="PowerShell Select-String fallback",
        category="LANGUAGES",
        candidate_group="SEARCH_CODE_NAVIGATION",
        detection_commands=(
            "powershell -NoProfile -Command \"'alpha' | Select-String -Pattern 'alp' | ForEach-Object { $_.Matches.Count }\"",
        ),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Built-in fallback without installs.",),
        minus=("Slower than ripgrep for large trees.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="",
        notes="Mandatory fallback when external grep utilities are unavailable.",
    ),
    CandidateSpec(
        tool_id="PYTHON_PATHLIB_GLOB_FALLBACK",
        name="Python pathlib/glob fallback",
        category="REFERENCE_CODE",
        candidate_group="SEARCH_CODE_NAVIGATION",
        detection_commands=(
            "python -c \"from pathlib import Path; print(len(list(Path('IMPERIUM_NEW_GENERATION').glob('**/*.md'))) > 0)\"",
        ),
        value_level="MEDIUM",
        risk_level="LOW",
        plus=("No extra install; deterministic fallback.",),
        minus=("Slow on deep trees.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="",
        notes="Used only as bounded fallback when rg/fd are missing.",
    ),
    CandidateSpec(
        tool_id="UTILITIES_JQ",
        name="jq",
        category="UTILITIES",
        candidate_group="JSON_YAML_DATA",
        detection_commands=("jq --version",),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Compact JSON filtering in shell lanes.",),
        minus=("Extra binary if not preinstalled.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="winget install jqlang.jq",
        notes="Speeds up report/receipt shaping and quick data checks.",
    ),
    CandidateSpec(
        tool_id="UTILITIES_YQ",
        name="yq",
        category="UTILITIES",
        candidate_group="JSON_YAML_DATA",
        detection_commands=("yq --version",),
        value_level="MEDIUM",
        risk_level="LOW",
        plus=("YAML+JSON transformations in one CLI.",),
        minus=("Not required for minimal tasks.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="winget install MikeFarah.yq",
        notes="Useful for taskpacks with YAML meta contracts.",
    ),
    CandidateSpec(
        tool_id="CAP-TOOL-JSONSCHEMA",
        name="jsonschema (tool lane)",
        category="TOOLS",
        candidate_group="JSON_YAML_DATA",
        detection_commands=("python -m jsonschema --version",),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Schema-first guard for machine artifacts.",),
        minus=("CLI is deprecated; future migration to check-jsonschema likely.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="python -m pip install --user jsonschema",
        notes="Already in SANDBOX; revalidated to support expansion batch receipts.",
    ),
    CandidateSpec(
        tool_id="CODE_QUALITY_JSONSCHEMA",
        name="jsonschema (code-quality lane)",
        category="CODE_QUALITY",
        candidate_group="JSON_YAML_DATA",
        detection_commands=("python -m jsonschema --version",),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Shared validator across reports/contracts.",),
        minus=("Long-term CLI replacement should be planned.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="python -m pip install --user jsonschema",
        notes="Companion lane for code-quality scope packs.",
    ),
    CandidateSpec(
        tool_id="REFERENCE_CODE_SAFE_JSON_WRITE_HELPER",
        name="safe JSON write helper reference",
        category="REFERENCE_CODE",
        candidate_group="JSON_YAML_DATA",
        detection_commands=(
            "python -c \"from pathlib import Path; p=Path('IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/REFERENCE_CODE/REFERENCE_CODE_SAFE_JSON_WRITE_HELPER/capability_card.json'); print(p.exists()); raise SystemExit(0 if p.exists() else 2)\"",
        ),
        value_level="MEDIUM",
        risk_level="LOW",
        plus=("Reduces malformed JSON artifact risk.",),
        minus=("Reference pattern, not standalone executable.",),
        preferred_action="KEEP_CANDIDATE",
        owner_approval_required=False,
        proposed_install_command="",
        notes="Validated as reference availability; promotion remains conservative.",
    ),
    CandidateSpec(
        tool_id="UTILITIES_7_ZIP",
        name="7-Zip CLI",
        category="UTILITIES",
        candidate_group="ARCHIVE_HASH_EVIDENCE",
        detection_commands=("7z i", "7za i"),
        value_level="HIGH",
        risk_level="MEDIUM",
        plus=("Strong archive tooling for taskpack checks.",),
        minus=("Not installed on many hosts; install required.",),
        preferred_action="OWNER_APPROVAL_REQUIRED",
        owner_approval_required=True,
        proposed_install_command="winget install 7zip.7zip",
        notes="No silent install allowed; queue for owner gate when missing.",
    ),
    CandidateSpec(
        tool_id="TAR_ZIP_RUNTIME_AVAILABILITY",
        name="tar/zip runtime availability",
        category="UTILITIES",
        candidate_group="ARCHIVE_HASH_EVIDENCE",
        detection_commands=("tar --version", "python -c \"import zipfile, tarfile; print('zip_tar_ok')\""),
        value_level="MEDIUM",
        risk_level="LOW",
        plus=("Built-in archive fallback without extra install.",),
        minus=("tar CLI behavior differs across shells.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="",
        notes="Core fallback for controlled packaging lanes.",
    ),
    CandidateSpec(
        tool_id="UTILITIES_ARCHIVE_MANIFEST_GENERATOR",
        name="archive manifest generator",
        category="UTILITIES",
        candidate_group="ARCHIVE_HASH_EVIDENCE",
        detection_commands=(
            "python -c \"import json,hashlib,zipfile,tarfile; print('archive_manifest_stack_ok')\"",
        ),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Supports deterministic hash manifest creation.",),
        minus=("Current implementation is fallback, not dedicated CLI.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="",
        notes="Promotable to SANDBOX if fallback checks pass.",
    ),
    CandidateSpec(
        tool_id="UTILITIES_SHA256_HASHING",
        name="SHA256 hashing lane",
        category="UTILITIES",
        candidate_group="ARCHIVE_HASH_EVIDENCE",
        detection_commands=(
            "certutil -hashfile AGENTS.md SHA256",
            "python -c \"import hashlib, pathlib; print(hashlib.sha256(pathlib.Path('AGENTS.md').read_bytes()).hexdigest()[:8])\"",
        ),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Critical for evidence integrity.",),
        minus=("Some environments lack Get-FileHash cmdlet.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="",
        notes="Validation accepts certutil/Python fallback combo.",
    ),
    CandidateSpec(
        tool_id="DATABASES_SQLITE",
        name="sqlite3 runtime",
        category="DATABASES",
        candidate_group="ARCHIVE_HASH_EVIDENCE",
        detection_commands=("python -c \"import sqlite3; print(sqlite3.sqlite_version)\"",),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Core storage for Evidence Index.",),
        minus=("Limited by stdlib compile options.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="",
        notes="Already SANDBOX; kept in matrix for dependency truth.",
    ),
    CandidateSpec(
        tool_id="DATABASES_SQLITE_FTS5",
        name="sqlite3 FTS5 support",
        category="DATABASES",
        candidate_group="ARCHIVE_HASH_EVIDENCE",
        detection_commands=(
            "python -c \"import sqlite3; con=sqlite3.connect(':memory:'); con.execute('CREATE VIRTUAL TABLE t USING fts5(content)'); print('fts5_ok')\"",
        ),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Enables fast evidence full-text search.",),
        minus=("Fails if Python sqlite build lacks fts5.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="",
        notes="Key dependency for evidence query smoke.",
    ),
    CandidateSpec(
        tool_id="SEARCH_INDEXING_SQLITE_FTS_SEARCH",
        name="SQLite FTS search lane",
        category="SEARCH_INDEXING",
        candidate_group="ARCHIVE_HASH_EVIDENCE",
        detection_commands=(
            "python -c \"import sqlite3; con=sqlite3.connect('IMPERIUM_NEW_GENERATION/MECHANICUS/EVIDENCE_INDEX/V0_1/evidence_index.sqlite3'); c=con.execute('SELECT COUNT(1) FROM evidence_fts').fetchone()[0]; print(c)\"",
        ),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Direct query lane for evidence retrieval.",),
        minus=("Depends on current index refresh state.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="",
        notes="Included to verify index utility after expansion artifacts.",
    ),
    CandidateSpec(
        tool_id="CODE_QUALITY_RUFF",
        name="ruff",
        category="CODE_QUALITY",
        candidate_group="REPO_HYGIENE_SAFETY",
        detection_commands=("python -m ruff --version",),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Fast lint guard for script quality.",),
        minus=("Can block on style drift if run too broad.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="python -m pip install --user ruff",
        notes="Quality gate requirement for new scripts in this task.",
    ),
    CandidateSpec(
        tool_id="CODE_QUALITY_MYPY",
        name="mypy",
        category="CODE_QUALITY",
        candidate_group="REPO_HYGIENE_SAFETY",
        detection_commands=("python -m mypy --version",),
        value_level="MEDIUM",
        risk_level="LOW",
        plus=("Type-safety evidence for reusable scripts.",),
        minus=("First-pass warnings acceptable in this step.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="python -m pip install --user mypy",
        notes="Supports GATE-U13 evidence lane.",
    ),
    CandidateSpec(
        tool_id="ALGORITHMS_RUNTIME_JUNK_CLASSIFIER",
        name="runtime junk classifier",
        category="ALGORITHMS",
        candidate_group="REPO_HYGIENE_SAFETY",
        detection_commands=(
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/newgen_repo_hygiene_check_v0_1.py --help",
        ),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Prevents noisy dirty-state from generated artifacts.",),
        minus=("Classifier quality depends on maintained ignore rules.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="",
        notes="Can be promoted once deterministic help/run evidence exists.",
    ),
    CandidateSpec(
        tool_id="TOOLS_SCOPE_REVIEW_TOOL",
        name="scope pack review tool",
        category="TOOLS",
        candidate_group="REPO_HYGIENE_SAFETY",
        detection_commands=(
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_scope_packs_v0_1.py --help",
        ),
        value_level="HIGH",
        risk_level="LOW",
        plus=("Guards fake-CANON and scope mismatch drift.",),
        minus=("Needs jsonschema package for full checks.",),
        preferred_action="VALIDATE_IF_PRESENT",
        owner_approval_required=False,
        proposed_install_command="",
        notes="Useful as reusable preflight for scope updates.",
    ),
    CandidateSpec(
        tool_id="TOOLS_CANDIDATE_CHECK_WORKFLOW",
        name="candidate check workflow",
        category="TOOLS",
        candidate_group="REPO_HYGIENE_SAFETY",
        detection_commands=(
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_capability_validator_v0_1.py --help",
        ),
        value_level="MEDIUM",
        risk_level="LOW",
        plus=("Structured validation-to-receipt flow exists.",),
        minus=("Current workflow tuned for earlier batches.",),
        preferred_action="KEEP_CANDIDATE",
        owner_approval_required=False,
        proposed_install_command="",
        notes="Kept candidate; this task ships dedicated expansion workflow instead.",
    ),
    CandidateSpec(
        tool_id="TOOLS_TASKPACK_DOSSIER_BUILDER",
        name="taskpack dossier builder lane",
        category="TOOLS",
        candidate_group="REPORTING_TASKPACK",
        detection_commands=(
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_taskpack_validator_v0_1.py --help",
        ),
        value_level="MEDIUM",
        risk_level="LOW",
        plus=("Existing validator supports dossier quality checks.",),
        minus=("Dedicated builder tool still candidate-level concept.",),
        preferred_action="KEEP_CANDIDATE",
        owner_approval_required=False,
        proposed_install_command="",
        notes="Validation confirms taskpack lane exists; install not needed.",
    ),
    CandidateSpec(
        tool_id="MARKDOWNLINT_CLI",
        name="markdownlint CLI",
        category="TOOLS",
        candidate_group="REPORTING_TASKPACK",
        detection_commands=("markdownlint --version", "markdownlint-cli2 --version"),
        value_level="MEDIUM",
        risk_level="MEDIUM",
        plus=("Automated markdown contract hygiene.",),
        minus=("Node-based install; not currently present.",),
        preferred_action="OWNER_APPROVAL_REQUIRED",
        owner_approval_required=True,
        proposed_install_command="npm install -g markdownlint-cli2",
        notes="Queue for owner approval if reporting quality tightening is desired.",
    ),
    CandidateSpec(
        tool_id="CHECK_JSONSCHEMA_CLI",
        name="check-jsonschema CLI",
        category="TOOLS",
        candidate_group="REPORTING_TASKPACK",
        detection_commands=("check-jsonschema --version",),
        value_level="MEDIUM",
        risk_level="MEDIUM",
        plus=("Modern replacement for deprecated jsonschema CLI.",),
        minus=("Not installed by default.",),
        preferred_action="OWNER_APPROVAL_REQUIRED",
        owner_approval_required=True,
        proposed_install_command="python -m pip install --user check-jsonschema",
        notes="Deferred install lane with explicit owner gate.",
    ),
    CandidateSpec(
        tool_id="YAMLLINT_CLI",
        name="yamllint",
        category="TOOLS",
        candidate_group="REPORTING_TASKPACK",
        detection_commands=("yamllint --version",),
        value_level="LOW",
        risk_level="MEDIUM",
        plus=("Strict YAML lint for future taskpack variants.",),
        minus=("Not needed for current JSON-first core flows.",),
        preferred_action="DEFER",
        owner_approval_required=True,
        proposed_install_command="python -m pip install --user yamllint",
        notes="Can remain deferred until YAML-heavy contracts are introduced.",
    ),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def registry_cards_by_id(repo_root: Path) -> dict[str, dict[str, Any]]:
    registry_path = repo_root / REGISTRY_REL
    payload = load_json(registry_path)
    cards = payload.get("cards", [])
    out: dict[str, dict[str, Any]] = {}
    if not isinstance(cards, list):
        return out
    for row in cards:
        if not isinstance(row, dict):
            continue
        cap = str(row.get("capability_id", "")).strip()
        if cap:
            out[cap] = row
    return out


def build_candidate_rows(repo_root: Path) -> list[dict[str, Any]]:
    cards_by_id = registry_cards_by_id(repo_root)
    rows: list[dict[str, Any]] = []
    for spec in CANDIDATES:
        card = cards_by_id.get(spec.tool_id)
        rows.append(
            {
                "tool_id": spec.tool_id,
                "name": spec.name,
                "category": spec.category,
                "candidate_group": spec.candidate_group,
                "detection_commands": list(spec.detection_commands),
                "present": None,
                "current_capability_card": str(card.get("card_path", "")) if card else "",
                "current_status": str(card.get("status", "NO_CARD")) if card else "NO_CARD",
                "value_level": spec.value_level,
                "risk_level": spec.risk_level,
                "plus": list(spec.plus),
                "minus": list(spec.minus),
                "recommended_action": spec.preferred_action,
                "owner_approval_required": bool(spec.owner_approval_required),
                "proposed_install_command": spec.proposed_install_command,
                "validation_receipt": "",
                "status_recommendation": "KEEP_CANDIDATE",
                "notes": spec.notes,
            }
        )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Mechanicus tool expansion candidate matrix.")
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
    output_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)

    rows = build_candidate_rows(repo_root)
    no_card_count = sum(1 for row in rows if row["current_status"] == "NO_CARD")
    approval_count = sum(1 for row in rows if bool(row["owner_approval_required"]))
    by_group: dict[str, int] = {}
    for row in rows:
        key = str(row["candidate_group"])
        by_group[key] = by_group.get(key, 0) + 1

    matrix_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "builder": "mechanicus_tool_expansion_candidate_builder_v0_1.py",
        "candidates": rows,
        "summary": {
            "candidate_count": len(rows),
            "owner_approval_required_count": approval_count,
            "no_card_count": no_card_count,
            "by_group": by_group,
        },
    }

    write_json(output_root / "tool_candidate_matrix_v0_1.json", matrix_payload)
    write_json(
        report_root / "tool_expansion_candidate_report.json",
        {
            "task_id": args.task_id,
            "generated_at_utc": utc_now(),
            "checker": "mechanicus_tool_expansion_candidate_builder_v0_1.py",
            "summary": matrix_payload["summary"],
            "warnings": (
                ["some_candidates_have_no_capability_card"]
                if no_card_count > 0
                else []
            ),
            "verdict": "PASS",
            "raw_dump_status": "COMPACT_ONLY",
        },
    )

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "candidate_count": len(rows),
                "approval_required": approval_count,
                "no_card_count": no_card_count,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
