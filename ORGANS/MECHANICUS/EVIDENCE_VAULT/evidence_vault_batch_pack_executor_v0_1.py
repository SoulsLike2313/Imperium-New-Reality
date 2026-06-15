#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Imperium Evidence Vault Batch 001 Pack Executor v0.1.0

Purpose:
  Execute owner-approved copy/pack/seal of Batch 001 candidates into Evidence Vault.

Safety contract:
  - Requires explicit owner token.
  - Copies source files into temporary Vault buffer, then zips/seals into Vault pack folder.
  - Does NOT delete source.
  - Does NOT move source.
  - Does NOT rewrite source.
  - Writes only to --vault-root and --out-root.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import html
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

SCHEMA = "imperium.evidence_vault_batch_pack_execution.v0_1"
SURFACE = "MECHANICUS_EVIDENCE_VAULT_BATCH_PACK_EXECUTOR_V0_1"
VERSION = "0.1.0"
OWNER_TOKEN = "APPROVE_EVIDENCE_VAULT_BATCH_001_COPY_PACK_NO_SOURCE_DELETE"
BATCH_ID_DEFAULT = "BATCH_001_REPORTS_LEGACY_PACK_TO_VAULT"

PATH_KEYS = (
    "relative_path", "repo_path", "source_relative_path", "path", "file", "source_path"
)
SHA_KEYS = (
    "sha256", "actual_sha256", "source_sha256", "expected_sha256", "planned_sha256"
)
SIZE_KEYS = ("bytes", "size", "size_bytes", "actual_bytes", "source_bytes")
STATUS_KEYS = ("status", "dry_run_status", "state")


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def run(cmd: List[str], cwd: Optional[Path] = None) -> str:
    try:
        return subprocess.check_output(cmd, cwd=str(cwd) if cwd else None, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "UNKNOWN"


def git_info(repo: Path) -> Dict[str, str]:
    return {
        "head": run(["git", "rev-parse", "HEAD"], repo),
        "short_head": run(["git", "rev-parse", "--short=12", "HEAD"], repo),
        "branch": run(["git", "branch", "--show-current"], repo),
        "status_short_before_execution": run(["git", "status", "--short"], repo),
    }


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_rel(raw: str) -> str:
    s = str(raw).replace("\\", "/").strip()
    while s.startswith("./"):
        s = s[2:]
    if not s or s.startswith("/") or ":" in s:
        raise ValueError(f"unsafe path: {raw!r}")
    parts = [p for p in s.split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts):
        raise ValueError(f"unsafe traversal path: {raw!r}")
    return "/".join(parts)


def first_value(row: Dict[str, Any], keys: Iterable[str]) -> Any:
    for k in keys:
        if k in row and row[k] not in (None, ""):
            return row[k]
    return None


def looks_ready(row: Dict[str, Any]) -> bool:
    status = str(first_value(row, STATUS_KEYS) or "").upper()
    if not status:
        return True
    bad = ("MISSING", "FAIL", "FAILED", "ERROR", "MISMATCH", "BLOCKED")
    return not any(token in status for token in bad)


def load_jsonl_candidates(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if not isinstance(obj, dict):
                continue
            raw_path = first_value(obj, PATH_KEYS)
            if not raw_path:
                continue
            try:
                rel = safe_rel(str(raw_path))
            except ValueError:
                continue
            if not looks_ready(obj):
                continue
            obj["relative_path"] = rel
            obj["_source_manifest"] = str(path)
            obj["_line_no"] = line_no
            rows.append(obj)
    return rows


def load_csv_candidates(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, 2):
            raw_path = first_value(row, PATH_KEYS)
            if not raw_path:
                continue
            try:
                rel = safe_rel(str(raw_path))
            except ValueError:
                continue
            if not looks_ready(row):
                continue
            row["relative_path"] = rel
            row["_source_manifest"] = str(path)
            row["_line_no"] = line_no
            rows.append(row)
    return rows


def discover_candidate_rows(plan_root: Path, explicit_manifest: Optional[Path] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    candidates: List[Tuple[int, Path, List[Dict[str, Any]]]] = []
    sources: List[str] = []

    manifest_paths: List[Path] = []
    if explicit_manifest:
        manifest_paths.append(explicit_manifest)
    else:
        for pattern in ("*.jsonl", "*.csv"):
            manifest_paths.extend(plan_root.rglob(pattern))

    for p in manifest_paths:
        name = p.name.lower()
        if "research" in name or "machine" in name or "sha256" in name:
            continue
        try:
            if p.suffix.lower() == ".jsonl":
                rows = load_jsonl_candidates(p)
            elif p.suffix.lower() == ".csv":
                rows = load_csv_candidates(p)
            else:
                rows = []
        except Exception:
            rows = []
        if rows:
            # Prefer dry-run/manifest/plan files with the largest candidate count.
            score = len(rows)
            if "dry" in name:
                score += 100000
            if "manifest" in name:
                score += 10000
            if "candidate" in name:
                score += 1000
            candidates.append((score, p, rows))
            sources.append(str(p))

    if not candidates:
        raise SystemExit(f"No candidate manifest rows found under: {plan_root}")

    candidates.sort(key=lambda x: x[0], reverse=True)
    chosen_score, chosen_path, chosen_rows = candidates[0]

    # De-duplicate by relative path while preserving chosen order.
    seen = set()
    deduped = []
    for row in chosen_rows:
        rel = row["relative_path"]
        if rel in seen:
            continue
        seen.add(rel)
        deduped.append(row)

    meta = {
        "chosen_manifest": str(chosen_path),
        "chosen_manifest_rows": len(chosen_rows),
        "deduped_rows": len(deduped),
        "candidate_source_files_considered": sources,
    }
    return deduped, meta


def check_rows(repo: Path, rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    checked: List[Dict[str, Any]] = []
    totals = {
        "candidates_total": len(rows),
        "ready_total": 0,
        "missing_total": 0,
        "sha256_mismatch_total": 0,
        "total_bytes": 0,
    }
    for idx, row in enumerate(rows, 1):
        rel = row["relative_path"]
        src = repo / Path(rel)
        expected = first_value(row, SHA_KEYS)
        expected = str(expected).lower() if expected else None
        rec = {
            "id": f"BATCH_001_REPORTS_LEGACY_PACK_TO_VAULT_EXECUTION-{idx:05d}",
            "relative_path": rel,
            "source_exists": src.exists() and src.is_file(),
            "source_path": str(src),
            "expected_sha256": expected,
        }
        if not rec["source_exists"]:
            rec.update({"status": "MISSING", "bytes": 0, "sha256": None, "sha256_matches_plan": False})
            totals["missing_total"] += 1
            checked.append(rec)
            continue
        actual_sha = sha256_file(src)
        size = src.stat().st_size
        matches = True if not expected else (expected == actual_sha)
        rec.update({
            "status": "READY" if matches else "SHA256_MISMATCH",
            "bytes": size,
            "sha256": actual_sha,
            "sha256_matches_plan": matches,
        })
        totals["total_bytes"] += size
        if matches:
            totals["ready_total"] += 1
        else:
            totals["sha256_mismatch_total"] += 1
        checked.append(rec)
    return checked, totals


def human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    x = float(n)
    for u in units:
        if x < 1024 or u == units[-1]:
            if u == "B":
                return f"{int(x)} B"
            return f"{x:.1f} {u}"
        x /= 1024
    return f"{n} B"


def zip_payload(repo: Path, checked: List[Dict[str, Any]], zip_path: Path) -> None:
    compression = zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(zip_path, "w", compression=compression, compresslevel=6) as zf:
        for rec in checked:
            if rec["status"] != "READY":
                continue
            src = repo / Path(rec["relative_path"])
            arcname = "payload/" + rec["relative_path"].replace("\\", "/")
            zf.write(src, arcname)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["id", "status", "relative_path", "bytes", "sha256", "expected_sha256", "sha256_matches_plan"]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fields})


def write_sqlite(path: Path, checked: List[Dict[str, Any]], manifest: Dict[str, Any]) -> None:
    if path.exists():
        path.unlink()
    con = sqlite3.connect(str(path))
    try:
        con.execute("""create table pack_items(
            id text primary key,
            status text,
            relative_path text,
            bytes integer,
            sha256 text,
            expected_sha256 text,
            sha256_matches_plan integer
        )""")
        con.execute("""create table manifest(key text primary key, value text)""")
        con.executemany(
            "insert into pack_items values(?,?,?,?,?,?,?)",
            [(
                r.get("id"), r.get("status"), r.get("relative_path"), int(r.get("bytes") or 0),
                r.get("sha256"), r.get("expected_sha256"), 1 if r.get("sha256_matches_plan") else 0,
            ) for r in checked]
        )
        for k, v in manifest.items():
            if isinstance(v, (dict, list)):
                v = json.dumps(v, ensure_ascii=False, sort_keys=True)
            con.execute("insert into manifest values(?,?)", (str(k), str(v)))
        con.commit()
    finally:
        con.close()


def top_dirs(rows: List[Dict[str, Any]], limit: int = 25) -> List[Dict[str, Any]]:
    agg: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        rel = r.get("relative_path", "")
        parts = rel.split("/")
        if len(parts) >= 2:
            key = "/".join(parts[:2])
        elif parts:
            key = parts[0]
        else:
            key = "ROOT"
        cur = agg.setdefault(key, {"folder": key, "count": 0, "bytes": 0})
        cur["count"] += 1
        cur["bytes"] += int(r.get("bytes") or 0)
    total = sum(x["count"] for x in agg.values()) or 1
    items = sorted(agg.values(), key=lambda x: (-x["count"], -x["bytes"], x["folder"]))[:limit]
    for x in items:
        x["share_ratio"] = x["count"] / total
        x["share_percent"] = round(x["share_ratio"] * 100, 2)
    return items


def make_owner_summary_ru(path: Path, manifest: Dict[str, Any]) -> None:
    text = f"""# Evidence Vault Batch 001 — Pack Execution

Статус: **{manifest['status']}**

Этот execution-патч скопировал и упаковал Batch 001 в Evidence Vault.

- Кандидатов: {manifest['candidates_total']}
- Упаковано: {manifest['packed_total']}
- Missing: {manifest['missing_total']}
- SHA256 mismatch: {manifest['sha256_mismatch_total']}
- Объём source payload: {human_bytes(manifest['total_bytes'])}
- ZIP: `{manifest['pack_zip']}`
- ZIP SHA256: `{manifest['pack_zip_sha256']}`

## Owner gate

Source НЕ удалялся, НЕ перемещался и НЕ переписывался. Этот pack разрешает только регистрацию/верификацию Vault pack. Cleanup source остаётся отдельным будущим owner gate.
"""
    path.write_text(text, encoding="utf-8")


def make_owner_summary_en(path: Path, manifest: Dict[str, Any]) -> None:
    text = f"""# Evidence Vault Batch 001 — Pack Execution

Status: **{manifest['status']}**

This execution patch copied and packed Batch 001 into Evidence Vault.

- Candidates: {manifest['candidates_total']}
- Packed: {manifest['packed_total']}
- Missing: {manifest['missing_total']}
- SHA256 mismatch: {manifest['sha256_mismatch_total']}
- Source payload bytes: {human_bytes(manifest['total_bytes'])}
- ZIP: `{manifest['pack_zip']}`
- ZIP SHA256: `{manifest['pack_zip_sha256']}`

## Owner gate

Source was NOT deleted, NOT moved and NOT rewritten. This pack authorizes only Vault pack registration/verification. Source cleanup remains a separate future owner gate.
"""
    path.write_text(text, encoding="utf-8")


def make_dashboard(path: Path, manifest: Dict[str, Any], tops: List[Dict[str, Any]], rows: List[Dict[str, Any]]) -> None:
    ready_pct = 100.0 * manifest["packed_total"] / max(1, manifest["candidates_total"])
    status_color = "ok" if manifest["status"].startswith("PASS") else "warn"
    top_rows = "\n".join(
        f"<tr><td><code>{html.escape(t['folder'])}</code></td><td>{t['count']}</td><td>{human_bytes(t['bytes'])}</td><td><div class='bar'><span style='width:{min(100,t['share_percent']):.2f}%'></span></div><span class='pct'>{t['share_percent']:.1f}%</span></td></tr>"
        for t in tops
    )
    first_rows = "\n".join(
        f"<tr><td><code>{html.escape(r['id'])}</code></td><td class='{ 'ok' if r['status']=='READY' else 'danger'}'>{html.escape(r['status'])}</td><td>{human_bytes(int(r.get('bytes') or 0))}</td><td><code>{html.escape(r.get('relative_path',''))}</code></td></tr>"
        for r in rows[:80]
    )
    doc = f"""<!doctype html><html lang=\"ru\"><head><meta charset=\"utf-8\"><title>Imperium Evidence Vault Batch Execution</title><style>
    :root{{--bg:#0d1117;--panel:#151b24;--line:#2b3445;--text:#f2f7ff;--muted:#b8c7e6;--accent:#8bd5ff;--accent2:#dab6ff;--warn:#ffd166;--danger:#ff7b72;--ok:#7ee787;}}
    *{{box-sizing:border-box}}body{{margin:0;padding:24px;background:var(--bg);color:var(--text);font-family:Segoe UI,Arial,sans-serif}}h1,h2{{margin:0 0 14px}}.muted{{color:var(--muted)}}
    .top{{display:flex;justify-content:space-between;gap:12px;align-items:start;border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:22px}}
    .lang button{{background:#20283a;color:var(--text);border:1px solid #36435c;border-radius:8px;padding:8px 12px;margin-left:6px;cursor:pointer}}.lang button.active{{border-color:var(--accent);box-shadow:0 0 0 2px rgba(139,213,255,.2)}}
    .grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}}.label{{text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-size:13px}}.big{{font-size:34px;font-weight:800;margin-top:10px}}
    .owner{{background:linear-gradient(135deg,#17212c,#21172f);border:1px solid var(--line);border-radius:12px;margin:18px 0;padding:20px}}table{{width:100%;border-collapse:collapse;background:var(--panel);border-radius:12px;overflow:hidden;margin:12px 0 28px}}th{{background:#20283a;color:#cfe2ff;text-align:left}}td,th{{border-bottom:1px solid var(--line);padding:11px 12px;vertical-align:top}}code{{font-family:Consolas,monospace;color:#dbeafe}}.bar{{display:inline-block;width:220px;height:11px;background:#30384b;border-radius:99px;overflow:hidden;margin-right:10px}}.bar span{{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2))}}.pct{{color:#cfe2ff}}.pill{{display:inline-block;border:1px solid #2f8ed8;color:#8bd5ff;border-radius:999px;padding:3px 8px;font-size:12px}}.ok{{color:var(--ok)}}.warn{{color:var(--warn)}}.danger{{color:var(--danger)}}.gate{{border-left:4px solid var(--accent);background:#111827;padding:14px 18px;margin-top:22px}}.ru .enOnly{{display:none}}.en .ruOnly{{display:none}}@media(max-width:900px){{.grid{{grid-template-columns:1fr}}.bar{{width:120px}}}}
    </style></head><body class=\"ru\"><div class=\"top\"><div><h1><span class=\"ruOnly\">Imperium Trinity Plus — Execution Batch 001</span><span class=\"enOnly\">Imperium Trinity Plus — Batch 001 Execution</span></h1><div class=\"muted\">{html.escape(manifest['patch_id'])} · {manifest['generated_at_utc']}</div></div><div class=\"lang\"><button onclick=\"document.body.className='ru';this.classList.add('active');this.nextElementSibling.classList.remove('active')\" class=\"active\">RU</button><button onclick=\"document.body.className='en';this.classList.add('active');this.previousElementSibling.classList.remove('active')\">EN</button></div></div>
    <div class=\"grid\"><div class=\"card\"><div class=\"label ruOnly\">Статус</div><div class=\"label enOnly\">Status</div><div class=\"big {status_color}\">{html.escape(manifest['status'])}</div><div class=\"muted\">Evidence Vault pack</div></div><div class=\"card\"><div class=\"label ruOnly\">Упаковано</div><div class=\"label enOnly\">Packed</div><div class=\"big\">{manifest['packed_total']}/{manifest['candidates_total']}</div><div class=\"bar\"><span style=\"width:{ready_pct:.2f}%\"></span></div><span class=\"pct\">{ready_pct:.1f}%</span></div><div class=\"card\"><div class=\"label ruOnly\">Объём</div><div class=\"label enOnly\">Bytes</div><div class=\"big\">{human_bytes(manifest['total_bytes'])}</div><div class=\"muted\">source payload</div></div><div class=\"card\"><div class=\"label ruOnly\">Режим</div><div class=\"label enOnly\">Mode</div><div class=\"big\">pack</div><div class=\"muted\">copy + zip + seal; no source delete</div></div></div>
    <div class=\"owner\"><div class=\"label\">Owner Gate</div><h2 class=\"ruOnly\">Batch 001 упакован в Evidence Vault. Source остался нетронутым.</h2><h2 class=\"enOnly\">Batch 001 was packed into Evidence Vault. Source stayed untouched.</h2><p class=\"ruOnly\">Этот патч копирует данные в Vault pack и создаёт manifest/receipt/SHA256. Он НЕ удаляет и НЕ перемещает source. Cleanup source — только отдельным будущим owner gate.</p><p class=\"enOnly\">This patch copies data into a Vault pack and creates manifest/receipt/SHA256. It does NOT delete or move source. Source cleanup requires a separate future owner gate.</p></div>
    <h2 class=\"ruOnly\">Готовность и результат</h2><h2 class=\"enOnly\">Readiness and result</h2><table><tr><th>Status</th><th>Progress</th><th class=\"ruOnly\">Шаг</th><th class=\"enOnly\">Step</th><th>Evidence</th></tr><tr><td><span class=\"pill\">PASS</span></td><td><div class=\"bar\"><span style=\"width:100%\"></span></div><span class=\"pct\">100.0%</span></td><td class=\"ruOnly\">Source-файлы проверены</td><td class=\"enOnly\">Source files checked</td><td>missing={manifest['missing_total']}; mismatch={manifest['sha256_mismatch_total']}</td></tr><tr><td><span class=\"pill\">PASS</span></td><td><div class=\"bar\"><span style=\"width:{ready_pct:.2f}%\"></span></div><span class=\"pct\">{ready_pct:.1f}%</span></td><td class=\"ruOnly\">ZIP создан</td><td class=\"enOnly\">ZIP created</td><td><code>{html.escape(manifest['pack_zip_name'])}</code></td></tr><tr><td><span class=\"pill\">PASS</span></td><td><div class=\"bar\"><span style=\"width:100%\"></span></div><span class=\"pct\">100.0%</span></td><td class=\"ruOnly\">Receipt создан</td><td class=\"enOnly\">Receipt created</td><td>zip_sha256=<code>{manifest['pack_zip_sha256'][:16]}...</code></td></tr><tr><td><span class=\"pill\">BLOCKED</span></td><td><div class=\"bar\"><span style=\"width:0%\"></span></div><span class=\"pct\">0.0%</span></td><td class=\"ruOnly\">Удаление source</td><td class=\"enOnly\">Source deletion</td><td>explicitly out of scope</td></tr></table>
    <h2 class=\"ruOnly\">Vault output</h2><h2 class=\"enOnly\">Vault output</h2><table><tr><th>Artifact</th><th>Path</th></tr><tr><td>Pack folder</td><td><code>{html.escape(manifest['pack_folder'])}</code></td></tr><tr><td>EVIDENCE_PACK.zip</td><td><code>{html.escape(manifest['pack_zip'])}</code></td></tr><tr><td>SHA256</td><td><code>{manifest['pack_zip_sha256']}</code></td></tr></table>
    <h2 class=\"ruOnly\">Главные папки</h2><h2 class=\"enOnly\">Top folders</h2><table><tr><th>Folder</th><th>Count</th><th>Bytes</th><th>Share</th></tr>{top_rows}</table><h2 class=\"ruOnly\">Первые упакованные кандидаты</h2><h2 class=\"enOnly\">First packed candidates</h2><table><tr><th>ID</th><th>Status</th><th>Bytes</th><th>Path</th></tr>{first_rows}</table><div class=\"gate\"><b>Owner gate:</b> <span class=\"ruOnly\">Vault pack создан. Source cleanup всё ещё запрещён без отдельного owner gate.</span><span class=\"enOnly\">Vault pack was created. Source cleanup remains blocked without a separate owner gate.</span></div></body></html>"""
    path.write_text(doc, encoding="utf-8")


def build(args: argparse.Namespace) -> Dict[str, Any]:
    repo = Path(args.repo).resolve()
    vault_root = Path(args.vault_root).resolve()
    out_root = Path(args.out_root).resolve()
    plan_root = Path(args.plan_root).resolve()
    manifest_path = Path(args.manifest).resolve() if args.manifest else None

    if args.owner_token != OWNER_TOKEN:
        raise SystemExit("OWNER TOKEN REQUIRED. Refusing to copy/pack without explicit owner gate token.")
    if not repo.exists():
        raise SystemExit(f"Repo not found: {repo}")
    if not plan_root.exists():
        raise SystemExit(f"Plan root not found: {plan_root}")
    if args.delete_source or args.move_source:
        raise SystemExit("Source delete/move is forbidden by v0.9.5 contract.")

    git = git_info(repo)
    generated = utc_now()
    stamp = utc_stamp()
    patch_id = args.patch_id or f"EVIDENCE-VAULT-BATCH-001-PACK-EXECUTION-{stamp}"
    batch_id = args.batch_id or BATCH_ID_DEFAULT

    rows, discover_meta = discover_candidate_rows(plan_root, manifest_path)
    checked, totals = check_rows(repo, rows)

    fail = totals["missing_total"] or totals["sha256_mismatch_total"]
    if fail:
        status = "FAIL_EVIDENCE_VAULT_BATCH_PACK_PRECHECK"
    else:
        status = "PASS_EVIDENCE_VAULT_BATCH_PACK_EXECUTED"

    # Refuse to create pack if prechecks fail.
    if fail:
        out_root.mkdir(parents=True, exist_ok=True)
        report = {
            "schema": SCHEMA,
            "surface": SURFACE,
            "version": VERSION,
            "status": status,
            "generated_at_utc": generated,
            "patch_id": patch_id,
            "batch_id": batch_id,
            "repo": str(repo),
            "git": git,
            **totals,
            "owner_gate": "No pack created because precheck failed; source untouched.",
            "discovery": discover_meta,
        }
        write_json(out_root / "EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION_REPORT.json", report)
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))

    pack_folder = vault_root / "packs" / _dt.datetime.now(_dt.timezone.utc).strftime("%Y") / _dt.datetime.now(_dt.timezone.utc).strftime("%m") / f"EVIDENCE_VAULT_BATCH_001_REPORTS_LEGACY_PACK_TO_VAULT_{stamp}"
    buffer_folder = vault_root / "buffer" / "active" / f"EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION_{stamp}"
    pack_folder.mkdir(parents=True, exist_ok=False)
    buffer_folder.mkdir(parents=True, exist_ok=False)
    out_root.mkdir(parents=True, exist_ok=True)

    zip_path = pack_folder / "EVIDENCE_PACK.zip"
    zip_payload(repo, checked, zip_path)
    zip_sha = sha256_file(zip_path)
    packed_total = sum(1 for r in checked if r["status"] == "READY")

    manifest = {
        "schema": SCHEMA,
        "surface": SURFACE,
        "version": VERSION,
        "status": status,
        "generated_at_utc": generated,
        "patch_id": patch_id,
        "batch_id": batch_id,
        "repo": str(repo),
        "source_head": git.get("head"),
        "source_short_head": git.get("short_head"),
        "source_branch": git.get("branch"),
        "vault_root": str(vault_root),
        "pack_folder": str(pack_folder),
        "pack_zip": str(zip_path),
        "pack_zip_name": zip_path.name,
        "pack_zip_sha256": zip_sha,
        "pack_zip_bytes": zip_path.stat().st_size,
        "mode": "copy_pack_seal_no_source_delete_no_source_move",
        "source_delete_performed": False,
        "source_move_performed": False,
        "source_rewrite_performed": False,
        "candidates_total": totals["candidates_total"],
        "packed_total": packed_total,
        "ready_total": totals["ready_total"],
        "missing_total": totals["missing_total"],
        "sha256_mismatch_total": totals["sha256_mismatch_total"],
        "total_bytes": totals["total_bytes"],
        "total_bytes_human": human_bytes(totals["total_bytes"]),
        "owner_gate": "Owner approved copy/pack into Evidence Vault only; no source deletion or movement authorized.",
        "discovery": discover_meta,
    }

    machine_index = {
        "schema": "imperium.evidence_vault_batch_pack_execution.machine_index.v0_1",
        "pack": manifest,
        "items": checked,
    }
    receipt = {
        "schema": "imperium.evidence_vault_batch_pack_execution.receipt.v0_1",
        "status": "PASS_EVIDENCE_VAULT_BATCH_PACK_RECEIPT",
        "generated_at_utc": generated,
        "pack_zip": str(zip_path),
        "pack_zip_sha256": zip_sha,
        "pack_zip_bytes": zip_path.stat().st_size,
        "packed_total": packed_total,
        "source_untouched_contract": {
            "source_delete_performed": False,
            "source_move_performed": False,
            "source_rewrite_performed": False,
        },
    }

    # Pack folder artifacts.
    write_json(pack_folder / "EVIDENCE_MANIFEST.json", manifest)
    write_json(pack_folder / "MACHINE_INDEX.json", machine_index)
    write_json(pack_folder / "MACHINE_RECEIPT.json", receipt)
    write_jsonl(pack_folder / "EVIDENCE_FILE_INDEX.jsonl", checked)
    write_csv(pack_folder / "EVIDENCE_FILE_INDEX.csv", checked)
    (pack_folder / "SHA256SUMS.txt").write_text(
        "\n".join([f"{zip_sha}  EVIDENCE_PACK.zip"] + [f"{r['sha256']}  payload/{r['relative_path']}" for r in checked if r.get("sha256")]) + "\n",
        encoding="utf-8",
    )
    make_owner_summary_ru(pack_folder / "OWNER_SUMMARY_RU.md", manifest)
    make_owner_summary_en(pack_folder / "OWNER_SUMMARY_EN.md", manifest)
    write_sqlite(pack_folder / "EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION.sqlite", checked, manifest)

    tops = top_dirs(checked)
    dashboard_path = pack_folder / "EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION_VISUAL_PROOF_DASHBOARD.html"
    make_dashboard(dashboard_path, manifest, tops, checked)

    # Mirror proof/output to handoff out_root for easier owner opening.
    write_json(out_root / "EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION_REPORT.json", manifest)
    write_json(out_root / "EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION_RECEIPT.json", receipt)
    write_jsonl(out_root / "EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION_FILE_INDEX.jsonl", checked)
    write_csv(out_root / "EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION_FILE_INDEX.csv", checked)
    write_sqlite(out_root / "EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION.sqlite", checked, manifest)
    make_dashboard(out_root / "EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION_VISUAL_PROOF_DASHBOARD.html", manifest, tops, checked)
    (out_root / "EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION_TERMINAL_RU_EN.txt").write_text(
        f"""Imperium Evidence Vault Batch 001 Pack Execution\nStatus: {status}\nPacked: {packed_total}/{totals['candidates_total']}\nMissing: {totals['missing_total']}\nSHA256 mismatch: {totals['sha256_mismatch_total']}\nBytes: {human_bytes(totals['total_bytes'])}\nPack folder: {pack_folder}\nEVIDENCE_PACK.zip SHA256: {zip_sha}\nOwner gate: no source delete / no source move / no source rewrite\n""",
        encoding="utf-8",
    )

    # Remove temporary buffer marker; payload exists only in ZIP and indexed manifests.
    shutil.rmtree(buffer_folder, ignore_errors=True)

    print(json.dumps({
        "status": status,
        "packed_total": packed_total,
        "candidates_total": totals["candidates_total"],
        "missing_total": totals["missing_total"],
        "sha256_mismatch_total": totals["sha256_mismatch_total"],
        "total_bytes": totals["total_bytes"],
        "pack_folder": str(pack_folder),
        "pack_zip": str(zip_path),
        "pack_zip_sha256": zip_sha,
        "dashboard": str(out_root / "EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION_VISUAL_PROOF_DASHBOARD.html"),
        "owner_gate": manifest["owner_gate"],
    }, ensure_ascii=False, indent=2))
    return manifest


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Execute owner-approved Evidence Vault Batch 001 copy/pack with no source deletion.")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--vault-root", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--plan-root", required=True)
    ap.add_argument("--manifest", default=None, help="Optional explicit candidate JSONL/CSV manifest.")
    ap.add_argument("--batch-id", default=BATCH_ID_DEFAULT)
    ap.add_argument("--patch-id", default=None)
    ap.add_argument("--owner-token", required=True)
    ap.add_argument("--delete-source", action="store_true", help="Forbidden; always rejected.")
    ap.add_argument("--move-source", action="store_true", help="Forbidden; always rejected.")
    args = ap.parse_args(argv)
    build(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
