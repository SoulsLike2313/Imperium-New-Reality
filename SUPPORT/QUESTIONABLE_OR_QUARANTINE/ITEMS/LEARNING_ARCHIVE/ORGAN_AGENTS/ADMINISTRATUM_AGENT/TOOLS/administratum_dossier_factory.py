#!/usr/bin/env python3
"""Administratum dossier factory and OSS admission helpers."""
from __future__ import annotations

import hashlib
import html
import importlib.util
import json
import shutil
import subprocess
import textwrap
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _module_available(module_name: str) -> bool:
    return bool(importlib.util.find_spec(module_name))


def _first_existing_path(candidates: Sequence[str]) -> Optional[str]:
    for item in candidates:
        if Path(item).exists():
            return item
    return None


def detect_oss_availability(agent_root: Path) -> Dict[str, Any]:
    register_path = agent_root / "OSS_ADMISSION" / "OSS_ADMISSION_REGISTER_V0_1.json"
    register = read_json(register_path)

    tool_modules = {
        "rich": "rich",
        "jsonschema": "jsonschema",
        "reportlab": "reportlab",
        "weasyprint": "weasyprint",
        "pillow": "PIL",
        "pytest": "pytest",
        "ruff": "ruff",
        "playwright": "playwright",
        "duckdb": "duckdb",
        "sqlite3": "sqlite3",
    }
    detected_tools: List[Dict[str, Any]] = []
    admitted_or_detected: List[str] = []
    unavailable: List[str] = []
    for row in register.get("tools", []):
        tool_id = str(row.get("tool_id", ""))
        module_name = tool_modules.get(tool_id)
        available = _module_available(module_name) if module_name else False
        out_row = dict(row)
        out_row["availability"] = bool(available)
        out_row["detected_at_utc"] = now_utc()
        if available:
            admitted_or_detected.append(tool_id)
        else:
            unavailable.append(tool_id)
        detected_tools.append(out_row)

    edge_path = _first_existing_path(
        [
            "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
            "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
        ]
    )
    chrome_path = _first_existing_path(
        [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        ]
    )
    pdf_backends = [
        {"backend": "edge_headless", "available": bool(edge_path), "path": edge_path or ""},
        {"backend": "chrome_headless", "available": bool(chrome_path), "path": chrome_path or ""},
    ]
    available_pdf_backend = "unavailable"
    if edge_path:
        available_pdf_backend = "edge_headless"
    elif chrome_path:
        available_pdf_backend = "chrome_headless"

    return {
        "report_type": "OSS_ADMISSION_DETECTION_REPORT",
        "generated_at_utc": now_utc(),
        "register_path": str(register_path),
        "tools": detected_tools,
        "admitted_or_detected": admitted_or_detected,
        "unavailable": unavailable,
        "pdf_backends": pdf_backends,
        "available_pdf_backend": available_pdf_backend,
    }


def _markdown_to_html(markdown_text: str, title: str) -> str:
    lines = markdown_text.splitlines()
    html_lines: List[str] = []
    in_code = False
    for raw in lines:
        stripped = raw.rstrip()
        if stripped.startswith("```"):
            if not in_code:
                html_lines.append("<pre><code>")
                in_code = True
            else:
                html_lines.append("</code></pre>")
                in_code = False
            continue
        if in_code:
            html_lines.append(html.escape(raw))
            continue
        if stripped.startswith("### "):
            html_lines.append(f"<h3>{html.escape(stripped[4:])}</h3>")
            continue
        if stripped.startswith("## "):
            html_lines.append(f"<h2>{html.escape(stripped[3:])}</h2>")
            continue
        if stripped.startswith("# "):
            html_lines.append(f"<h1>{html.escape(stripped[2:])}</h1>")
            continue
        if stripped.startswith("- "):
            if not html_lines or not html_lines[-1].endswith("<ul>"):
                html_lines.append("<ul>")
            html_lines.append(f"<li>{html.escape(stripped[2:])}</li>")
            continue
        if html_lines and html_lines[-1].startswith("<li>"):
            html_lines.append("</ul>")
        if stripped:
            html_lines.append(f"<p>{html.escape(stripped)}</p>")
    if html_lines and html_lines[-1].startswith("<li>"):
        html_lines.append("</ul>")

    body = "\n".join(html_lines)
    return (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        f"<title>{html.escape(title)}</title>"
        "<style>"
        "body{font-family:'Segoe UI',Arial,sans-serif;font-size:13px;line-height:1.4;color:#111;padding:18px;}"
        "h1{font-size:24px;margin:0 0 12px 0;}h2{font-size:18px;margin:18px 0 10px 0;}h3{font-size:15px;margin:14px 0 8px 0;}"
        "pre{background:#f4f4f4;padding:10px;border:1px solid #ddd;overflow:auto;}"
        "code{font-family:Consolas,'Courier New',monospace;font-size:12px;}"
        "ul{margin:0 0 10px 20px;}p{margin:0 0 8px 0;}"
        "</style></head><body>"
        + body
        + "</body></html>"
    )


def _run_browser_pdf(binary: str, html_path: Path, out_pdf_path: Path) -> Tuple[bool, str]:
    out_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        binary,
        "--headless=new",
        "--disable-gpu",
        "--allow-file-access-from-files",
        f"--print-to-pdf={out_pdf_path}",
        str(html_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode == 0 and out_pdf_path.exists():
        return True, (proc.stdout.strip() or "pdf_generated")
    err = (proc.stderr.strip() or proc.stdout.strip() or f"exit_code={proc.returncode}").strip()
    return False, err


def _render_owner_pdf_ru(markdown_ru: str, out_dir: Path, preferred_backend: str) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    owner_md_path = out_dir / "OWNER_DOSSIER_RU.md"
    owner_html_path = out_dir / "OWNER_DOSSIER_RU.html"
    owner_pdf_path = out_dir / "OWNER_DOSSIER_RU.pdf"
    owner_md_path.write_text(markdown_ru, encoding="utf-8")
    owner_html_path.write_text(_markdown_to_html(markdown_ru, "Owner Dossier RU"), encoding="utf-8")

    edge_path = _first_existing_path(
        [
            "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
            "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
        ]
    )
    chrome_path = _first_existing_path(
        [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        ]
    )
    attempts: List[Tuple[str, Optional[str]]] = []
    if preferred_backend == "edge_headless":
        attempts = [("edge_headless", edge_path), ("chrome_headless", chrome_path)]
    elif preferred_backend == "chrome_headless":
        attempts = [("chrome_headless", chrome_path), ("edge_headless", edge_path)]
    else:
        attempts = [("edge_headless", edge_path), ("chrome_headless", chrome_path)]

    for backend, binary in attempts:
        if not binary:
            continue
        ok, message = _run_browser_pdf(binary, owner_html_path, owner_pdf_path)
        if ok:
            return {
                "generated": True,
                "backend": backend,
                "owner_pdf_path": str(owner_pdf_path),
                "owner_md_path": str(owner_md_path),
                "owner_html_path": str(owner_html_path),
                "message": message,
            }
    return {
        "generated": False,
        "backend": "unavailable",
        "owner_pdf_path": None,
        "owner_md_path": str(owner_md_path),
        "owner_html_path": str(owner_html_path),
        "message": "no_browser_pdf_backend_available",
    }


def _hash_lines_for_dir(base_dir: Path, *, skip_names: Optional[Sequence[str]] = None) -> List[str]:
    skip = set(skip_names or [])
    lines: List[str] = []
    for path in sorted(p for p in base_dir.rglob("*") if p.is_file()):
        if path.name in skip:
            continue
        rel = path.relative_to(base_dir).as_posix()
        lines.append(f"{sha256_file(path)} *{rel}")
    return lines


def _write_sha256sums(base_dir: Path) -> Path:
    out = base_dir / "SHA256SUMS.txt"
    lines = _hash_lines_for_dir(base_dir, skip_names=["SHA256SUMS.txt"])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def _verify_sha256sums(base_dir: Path, sha_path: Path) -> Dict[str, Any]:
    if not sha_path.exists():
        return {"ok": False, "missing": ["SHA256SUMS.txt"], "mismatched": []}
    missing: List[str] = []
    mismatched: List[str] = []
    for line in sha_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, rel = line.split(" *", 1)
        target = base_dir / rel
        if not target.exists():
            missing.append(rel)
            continue
        if sha256_file(target) != digest:
            mismatched.append(rel)
    return {"ok": not missing and not mismatched, "missing": missing, "mismatched": mismatched}


def _copy_if_exists(src: Path, dst: Path, copied: List[str], missing: List[str]) -> None:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(dst.as_posix())
    else:
        missing.append(src.as_posix())


def _parse_command_status_matrix(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    rows: List[Dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text.startswith("|") or text.startswith("|---"):
            continue
        cells = [c.strip() for c in text.strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower() == "command":
            continue
        rows.append({"command": cells[0], "status": cells[1], "notes": cells[2]})
    return rows


@dataclass
class DossierBuildResult:
    verdict: str
    zip_path: str
    manifest_path: str
    sha256sums_path: str
    owner_pdf_generated: bool
    owner_pdf_path: Optional[str]
    owner_pdf_language: str
    pdf_backend: str
    evidence_index_path: str
    warnings: List[str]
    limitations: List[str]
    unverified: List[str]
    staging_root: str
    readme_path: str
    machine_receipt_path: str


def build_dossier_package(
    *,
    task_id: str,
    run_id: str,
    run_dir: Path,
    repo_root: Path,
    source_report_dir: Path,
    source_receipt_path: Path,
    command_status_matrix_path: Path,
    oss_snapshot: Dict[str, Any],
    next_recommended_task: str,
) -> DossierBuildResult:
    dossier_root = run_dir / "dossier_factory"
    dossier_root.mkdir(parents=True, exist_ok=True)
    zip_name = f"ADMINISTRATUM_DOSSIER_{task_id}.zip".replace("/", "_")
    staging_root = dossier_root / f"ADMINISTRATUM_DOSSIER_{task_id}"
    if staging_root.exists():
        shutil.rmtree(staging_root)
    staging_root.mkdir(parents=True, exist_ok=True)

    (staging_root / "machine").mkdir(parents=True, exist_ok=True)
    (staging_root / "reports_en").mkdir(parents=True, exist_ok=True)
    (staging_root / "owner_ru").mkdir(parents=True, exist_ok=True)
    (staging_root / "evidence" / "terminal_captures").mkdir(parents=True, exist_ok=True)
    (staging_root / "evidence" / "json_samples").mkdir(parents=True, exist_ok=True)
    (staging_root / "evidence" / "zip_listings").mkdir(parents=True, exist_ok=True)
    (staging_root / "evidence" / "logs").mkdir(parents=True, exist_ok=True)

    warnings: List[str] = []
    limitations: List[str] = []
    unverified: List[str] = []
    copied_reports: List[str] = []
    missing_reports: List[str] = []

    canonical_reports = {
        "IMPLEMENTATION_REPORT.md": ["IMPLEMENTATION_REPORT.md", "IMPLEMENTATION_REPORT_V0_1.md"],
        "TEST_REPORT.md": ["TEST_REPORT.md", "TEST_REPORT_V0_1.md"],
        "CHANGED_FILES.md": ["CHANGED_FILES.md", "CHANGED_FILES_V0_1.md"],
        "SELF_ASSESSMENT.md": ["SELF_ASSESSMENT.md", "SELF_ASSESSMENT_V0_1.md"],
        "LIMITATIONS_AND_UNVERIFIED.md": ["LIMITATIONS_AND_UNVERIFIED.md", "LIMITATIONS_AND_UNVERIFIED_V0_1.md"],
        "OSS_ADMISSION_REPORT.md": ["OSS_ADMISSION_REPORT.md", "OSS_ADMISSION_REPORT_V0_1.md"],
        "DOSSIER_FACTORY_REPORT.md": ["DOSSIER_FACTORY_REPORT.md", "DOSSIER_FACTORY_REPORT_V0_1.md"],
        "EVIDENCE_CAPTURE_REPORT.md": ["EVIDENCE_CAPTURE_REPORT.md", "EVIDENCE_CAPTURE_REPORT_V0_1.md"],
        "OWNER_QUICKSTART.md": ["OWNER_QUICKSTART.md", "OWNER_QUICKSTART_V0_1.md"],
        "COMMAND_STATUS_MATRIX.md": ["COMMAND_STATUS_MATRIX.md", "COMMAND_STATUS_MATRIX_V0_1.md"],
    }
    for out_name, src_names in canonical_reports.items():
        src = next((source_report_dir / name for name in src_names if (source_report_dir / name).exists()), None)
        if src is None:
            missing_reports.append((source_report_dir / src_names[0]).as_posix())
            continue
        _copy_if_exists(src, staging_root / "reports_en" / out_name, copied_reports, missing_reports)
    if missing_reports:
        warnings.append("Some canonical reports were missing and not copied to dossier reports_en.")

    if not source_receipt_path.exists():
        raise FileNotFoundError(f"Source receipt missing: {source_receipt_path}")
    source_receipt = read_json(source_receipt_path)
    receipt_copy_path = staging_root / "machine" / "receipt.json"
    write_json(receipt_copy_path, source_receipt)

    status_payload = {
        "task_id": task_id,
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "git_truth": {
            "head": str(source_receipt.get("ending_head_before_commit", "")),
            "branch": str(source_receipt.get("branch", "")),
            "dirty": bool(source_receipt.get("git_dirty_after", True)),
        },
        "source_report_dir": str(source_report_dir),
        "source_receipt_path": str(source_receipt_path),
        "verdict_hint": str(source_receipt.get("final_verdict", "UNKNOWN")),
    }
    write_json(staging_root / "machine" / "status.json", status_payload)

    command_matrix = _parse_command_status_matrix(command_status_matrix_path)
    write_json(staging_root / "machine" / "command_matrix.json", {"entries": command_matrix})

    limitations_payload = {
        "warnings": list(source_receipt.get("warnings", [])),
        "limitations": list(source_receipt.get("limitations", [])),
        "unverified": list(source_receipt.get("unverified", [])),
    }
    write_json(staging_root / "machine" / "limitations.json", limitations_payload)

    terminal_capture = staging_root / "evidence" / "terminal_captures" / "dossier_build_terminal_capture.txt"
    terminal_capture.write_text(
        "\n".join(
            [
                "ADMINISTRATUM DOSSIER BUILD TERMINAL CAPTURE",
                f"task_id={task_id}",
                f"run_id={run_id}",
                f"source_report_dir={source_report_dir}",
                f"source_receipt_path={source_receipt_path}",
                f"timestamp_utc={now_utc()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    builder_log = staging_root / "evidence" / "logs" / "dossier_builder.log"
    builder_log.write_text(
        "\n".join(
            [
                "dossier_factory_started",
                f"task_id={task_id}",
                f"copied_reports={len(copied_reports)}",
                f"missing_reports={len(missing_reports)}",
                f"available_pdf_backend={oss_snapshot.get('available_pdf_backend', 'unavailable')}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    owner_ru_md = [
        f"# Досье Owner: {task_id}",
        "",
        "## Краткий итог для Owner",
        f"- verdict: {source_receipt.get('final_verdict', 'UNKNOWN')}",
        f"- head: {source_receipt.get('starting_head', '')} -> {source_receipt.get('ending_head_before_commit', '')}",
        f"- branch: {source_receipt.get('branch', '')}",
            "- short_owner_summary: Досье собрано в machine-first формате; стандартный ZIP содержит markdown/json без PDF.",
        "",
        "## Доказательная база (evidence)",
        "- machine/receipt.json",
        "- machine/status.json",
        "- machine/command_matrix.json",
        "- machine/limitations.json",
        "- machine/evidence_index.json",
        "- MANIFEST.json",
        "- SHA256SUMS.txt",
        "",
        "## Включенные канонические отчеты (reports_en)",
    ]
    for copied in copied_reports:
        rel = Path(copied).relative_to(staging_root).as_posix()
        if rel.startswith("reports_en/"):
            owner_ru_md.append(f"- {rel}")
    if not any(Path(c).relative_to(staging_root).as_posix().startswith("reports_en/") for c in copied_reports):
        owner_ru_md.append("- none")
    owner_ru_md.extend(
        [
            "",
            "## Warnings",
        ]
    )
    for row in source_receipt.get("warnings", []) or ["none"]:
        owner_ru_md.append(f"- warning: {row}")
    owner_ru_md.extend(
        [
            "",
            "## Limitations",
        ]
    )
    for row in source_receipt.get("limitations", []) or ["none"]:
        owner_ru_md.append(f"- limitation: {row}")
    owner_ru_md.extend(
        [
            "",
            "## Unverified",
        ]
    )
    for row in source_receipt.get("unverified", []) or ["none"]:
        owner_ru_md.append(f"- unverified: {row}")
    owner_ru_md.extend(
        [
            "",
            "## Why trust",
            "- Канонические markdown-отчеты включены в ZIP без замены источника истины.",
            "- Машинный receipt и индекс доказательств включены в machine/.",
            "- Целостность фиксируется через SHA256SUMS.txt.",
            "",
            "## Next actions",
            f"- next_task: {next_recommended_task}",
            "",
        ]
    )
    owner_summary_path = staging_root / "owner_ru" / "OWNER_SUMMARY_RU.md"
    owner_summary_path.write_text("\n".join(owner_ru_md) + "\n", encoding="utf-8")
    owner_pdf_generated = False
    owner_pdf_path = None
    pdf_backend = "not_rendered_default_no_pdf"

    readme_path = staging_root / "README.md"
    readme_path.write_text(
        "\n".join(
            [
                f"# Administratum Dossier: {task_id}",
                "",
                "This archive contains machine-first JSON, canonical English reports, and Owner-facing Russian summary artifact.",
                "Canonical truth remains markdown reports and JSON receipts.",
                "Default exchange policy: no PDF files are included in this ZIP.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    evidence_entries: List[Dict[str, Any]] = []
    for rel_kind, path in [
        ("terminal_transcript", terminal_capture),
        ("file_hash_manifest", builder_log),
        ("owner_summary_md", owner_summary_path),
    ]:
        evidence_entries.append(
            {
                "evidence_kind": rel_kind,
                "path": path.relative_to(staging_root).as_posix(),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
                "note": "",
            }
        )
    evidence_index = {"schema_version": "imperium.administratum.evidence_index.v0_1", "entries": evidence_entries}
    evidence_index_path = staging_root / "machine" / "evidence_index.json"
    write_json(evidence_index_path, evidence_index)

    manifest_files: List[Dict[str, Any]] = []
    for p in sorted(x for x in staging_root.rglob("*") if x.is_file()):
        if p.name == "MANIFEST.json":
            continue
        rel = p.relative_to(staging_root).as_posix()
        manifest_files.append({"path": rel, "sha256": sha256_file(p), "bytes": p.stat().st_size})

    initial_verdict = "PASS"
    if warnings or limitations or unverified:
        initial_verdict = "WARN"

    manifest = {
        "schema_version": "imperium.administratum.dossier_manifest.v0_1",
        "task_id": task_id,
        "run_id": run_id,
        "created_at_utc": now_utc(),
        "git_truth": {
            "head": str(source_receipt.get("ending_head_before_commit", "")),
            "branch": str(source_receipt.get("branch", "")),
            "dirty": bool(source_receipt.get("git_dirty_after", True)),
        },
        "verdict": initial_verdict,
        "warnings": warnings,
        "limitations": limitations,
        "unverified": unverified,
        "files": manifest_files,
        "owner_pdf": {
            "generated": owner_pdf_generated,
            "language": "ru",
            "backend": pdf_backend,
            "path": Path(owner_pdf_path).relative_to(staging_root).as_posix() if owner_pdf_path else None,
            "default_zip_policy": "NO_PDF_MD_JSON_ONLY",
            "optional_external_render_only": True,
        },
    }
    manifest_path = staging_root / "MANIFEST.json"
    write_json(manifest_path, manifest)

    sha_path = _write_sha256sums(staging_root)
    hash_verify = _verify_sha256sums(staging_root, sha_path)
    if not hash_verify.get("ok", False):
        initial_verdict = "FAIL"
        warnings.append("SHA256 verification mismatch in staging.")
        unverified.append("Hash manifest mismatch requires manual inspection.")
        manifest["verdict"] = initial_verdict
        manifest["warnings"] = warnings
        manifest["unverified"] = unverified
        write_json(manifest_path, manifest)

    zip_path = dossier_root / zip_name
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(x for x in staging_root.rglob("*") if x.is_file()):
            zf.write(file_path, arcname=file_path.relative_to(staging_root).as_posix())

    verdict = initial_verdict
    if not hash_verify.get("ok", False):
        verdict = "FAIL"
    return DossierBuildResult(
        verdict=verdict,
        zip_path=str(zip_path),
        manifest_path=str(manifest_path),
        sha256sums_path=str(sha_path),
        owner_pdf_generated=owner_pdf_generated,
        owner_pdf_path=owner_pdf_path,
        owner_pdf_language="ru",
        pdf_backend=pdf_backend,
        evidence_index_path=str(evidence_index_path),
        warnings=warnings,
        limitations=limitations,
        unverified=unverified,
        staging_root=str(staging_root),
        readme_path=str(readme_path),
        machine_receipt_path=str(receipt_copy_path),
    )


def verify_dossier_package(zip_path: Path, verify_dir: Path) -> Dict[str, Any]:
    verify_dir.mkdir(parents=True, exist_ok=True)
    if not zip_path.exists():
        return {
            "report_type": "DOSSIER_VERIFY_REPORT",
            "generated_at_utc": now_utc(),
            "zip_path": str(zip_path),
            "verdict": "BLOCKED",
            "warnings": ["zip_not_found"],
        }
    extract_root = verify_dir / f"verify_{zip_path.stem}"
    if extract_root.exists():
        shutil.rmtree(extract_root)
    extract_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_root)
        zip_members = sorted(zf.namelist())

    required = [
        "MANIFEST.json",
        "SHA256SUMS.txt",
        "README.md",
        "machine/receipt.json",
        "machine/status.json",
        "machine/command_matrix.json",
        "machine/limitations.json",
        "machine/evidence_index.json",
        "reports_en/IMPLEMENTATION_REPORT.md",
        "reports_en/TEST_REPORT.md",
        "reports_en/CHANGED_FILES.md",
        "reports_en/LIMITATIONS_AND_UNVERIFIED.md",
        "owner_ru/OWNER_SUMMARY_RU.md",
    ]
    missing_required = [item for item in required if not (extract_root / item).exists()]
    hash_report = _verify_sha256sums(extract_root, extract_root / "SHA256SUMS.txt")
    pdf_members = [name for name in zip_members if name.lower().endswith(".pdf")]

    warnings: List[str] = []
    verdict = "PASS"
    if missing_required:
        verdict = "FAIL"
        warnings.append("required_files_missing")
    if not hash_report.get("ok", False):
        verdict = "FAIL"
        warnings.append("hash_verification_failed")
    if pdf_members:
        verdict = "FAIL"
        warnings.append("default_dossier_contains_pdf")

    return {
        "report_type": "DOSSIER_VERIFY_REPORT",
        "generated_at_utc": now_utc(),
        "zip_path": str(zip_path),
        "extract_root": str(extract_root),
        "zip_members_count": len(zip_members),
        "zip_members": zip_members,
        "missing_required": missing_required,
        "hash_verification": hash_report,
        "owner_pdf_generated": False,
        "owner_pdf_path": None,
        "pdf_members": pdf_members,
        "default_dossier_has_pdf": bool(pdf_members),
        "warnings": warnings,
        "verdict": verdict,
    }


def find_latest_dossier_zip(runs_root: Path) -> Optional[Path]:
    zips = sorted(
        [p for p in runs_root.glob("RUN-*/dossier_factory/ADMINISTRATUM_DOSSIER_*.zip") if p.is_file()],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )
    return zips[0] if zips else None
