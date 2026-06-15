#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Imperium Evidence Vault Batch 001 Receipt Verifier v0.1.0

Purpose:
  Verify a sealed Evidence Vault Batch 001 pack produced by v0.9.5 and emit a
  Data Atlas registration artifact that links hygiene Batch 001 to the Vault receipt.

Safety contract:
  - Read-only against source repo.
  - Read-only against Evidence Vault pack folder.
  - Writes only to --out-root.
  - Does NOT delete source.
  - Does NOT move source.
  - Does NOT rewrite source.
  - Does NOT create another Vault pack.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import html
import json
import os
import sqlite3
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

SCHEMA = "imperium.evidence_vault_batch_receipt_verification.v0_1"
SURFACE = "INQUISITION_EVIDENCE_VAULT_BATCH_RECEIPT_VERIFIER_V0_1"
VERSION = "0.1.0"
BATCH_ID_DEFAULT = "BATCH_001_REPORTS_LEGACY_PACK_TO_VAULT"
EXPECTED_SHA_DEFAULT = "26f143fe2df3ebb45991cb44bde87308a201f8149e20dbacf5b1c13b1ed12065"
EXPECTED_PACKED_DEFAULT = 2004
EXPECTED_BYTES_DEFAULT = 125624513
REQUIRED_SIDECARS = [
    "EVIDENCE_PACK.zip",
    "EVIDENCE_MANIFEST.json",
    "MACHINE_RECEIPT.json",
    "MACHINE_INDEX.json",
    "EVIDENCE_FILE_INDEX.jsonl",
    "EVIDENCE_FILE_INDEX.csv",
    "SHA256SUMS.txt",
    "OWNER_SUMMARY_RU.md",
    "OWNER_SUMMARY_EN.md",
    "EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION.sqlite",
    "EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION_VISUAL_PROOF_DASHBOARD.html",
]


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(cmd: List[str], cwd: Optional[Path] = None) -> str:
    try:
        return subprocess.check_output(cmd, cwd=str(cwd) if cwd else None, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "UNKNOWN"


def git_info(repo: Optional[Path]) -> Dict[str, str]:
    if not repo or not repo.exists():
        return {"head": "UNKNOWN", "short_head": "UNKNOWN", "branch": "UNKNOWN", "status_short": "UNKNOWN"}
    return {
        "head": run(["git", "rev-parse", "HEAD"], repo),
        "short_head": run(["git", "rev-parse", "--short=12", "HEAD"], repo),
        "branch": run(["git", "branch", "--show-current"], repo),
        "status_short": run(["git", "status", "--short"], repo),
    }


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_zip_member(zf: zipfile.ZipFile, name: str, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with zf.open(name, "r") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try:
                obj=json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True)+"\n")


def write_csv(path: Path, rows: List[Dict[str, Any]], fields: Optional[List[str]]=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not fields:
        fieldset=[]
        for row in rows:
            for k in row.keys():
                if k not in fieldset: fieldset.append(k)
        fields=fieldset or ["status"]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,"") for k in fields})


def human_bytes(n: int) -> str:
    units=["B","KB","MB","GB","TB"]
    x=float(n)
    for u in units:
        if x < 1024 or u == units[-1]:
            if u == "B": return f"{int(x)} B"
            return f"{x:.1f} {u}"
        x/=1024
    return f"{n} B"


def parse_sha256s(path: Path) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    if not path.exists():
        return mapping
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line=raw.strip()
        if not line or line.startswith("#"):
            continue
        parts=line.split(None, 1)
        if len(parts) != 2:
            continue
        digest, name = parts[0].lower(), parts[1].strip()
        if name.startswith("*"):
            name=name[1:]
        mapping[name.replace("\\", "/")] = digest
    return mapping


def top_dirs(rows: List[Dict[str, Any]], limit: int=25) -> List[Dict[str, Any]]:
    agg: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        rel=str(r.get("relative_path") or r.get("path") or "").replace("\\","/")
        parts=[p for p in rel.split("/") if p]
        key="/".join(parts[:2]) if len(parts)>=2 else (parts[0] if parts else "ROOT")
        cur=agg.setdefault(key,{"folder":key,"count":0,"bytes":0})
        cur["count"]+=1
        cur["bytes"]+=int(r.get("bytes") or r.get("size") or 0)
    total=sum(x["count"] for x in agg.values()) or 1
    items=sorted(agg.values(), key=lambda x:(-x["count"], -x["bytes"], x["folder"]))[:limit]
    for x in items:
        x["share_ratio"]=x["count"]/total
        x["share_percent"]=round(x["share_ratio"]*100, 2)
    return items


def sidecar_checks(pack_folder: Path) -> Tuple[List[Dict[str, Any]], bool]:
    rows=[]; ok=True
    for name in REQUIRED_SIDECARS:
        p=pack_folder/name
        exists=p.exists() and p.is_file()
        if not exists: ok=False
        rows.append({"name":name,"exists":exists,"bytes":p.stat().st_size if exists else 0,"status":"PASS" if exists else "MISSING"})
    return rows, ok


def sqlite_checks(sqlite_path: Path) -> Dict[str, Any]:
    out={"exists": sqlite_path.exists(), "tables": [], "pack_items_count": None, "manifest_count": None, "status": "MISSING"}
    if not sqlite_path.exists():
        return out
    con=sqlite3.connect(str(sqlite_path))
    try:
        tables=[r[0] for r in con.execute("select name from sqlite_master where type='table' order by name")]
        out["tables"]=tables
        if "pack_items" in tables:
            out["pack_items_count"]=con.execute("select count(*) from pack_items").fetchone()[0]
        if "manifest" in tables:
            out["manifest_count"]=con.execute("select count(*) from manifest").fetchone()[0]
        out["status"]="PASS" if "pack_items" in tables and "manifest" in tables else "FAIL_TABLES"
    except Exception as e:
        out["status"]="FAIL_SQLITE_OPEN"
        out["error"]=str(e)
    finally:
        con.close()
    return out


def zip_checks(zip_path: Path, sha_map: Dict[str,str], deep_hash: bool=True) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    info={"exists":zip_path.exists(),"zip_opens":False,"payload_entries_total":0,"zip_sha256":None,"zip_bytes":0,"status":"MISSING"}
    rows: List[Dict[str, Any]]=[]
    if not zip_path.exists():
        return info, rows
    info["zip_sha256"]=sha256_file(zip_path)
    info["zip_bytes"]=zip_path.stat().st_size
    expected_zip_sha=sha_map.get("EVIDENCE_PACK.zip")
    if expected_zip_sha:
        info["sha256s_zip_match"]=(expected_zip_sha.lower()==info["zip_sha256"])
    try:
        with zipfile.ZipFile(zip_path,"r") as zf:
            bad=zf.testzip()
            info["zip_testzip_bad_member"]=bad
            names=[n for n in zf.namelist() if not n.endswith("/")]
            payload=[n for n in names if n.startswith("payload/")]
            info["zip_opens"]=True
            info["entries_total"]=len(names)
            info["payload_entries_total"]=len(payload)
            limit_mismatches=25
            mismatches=0
            missing_sha=0
            for idx,name in enumerate(payload,1):
                expected=sha_map.get(name)
                actual=None; matches=None
                if deep_hash:
                    actual=sha256_zip_member(zf,name)
                    if expected:
                        matches=(actual.lower()==expected.lower())
                    else:
                        missing_sha+=1
                        matches=False
                rec={"id":idx,"zip_member":name,"relative_path":name[len("payload/"):],"expected_sha256":expected,"actual_sha256":actual,"sha256_matches":matches if matches is not None else "NOT_COMPUTED","bytes":zf.getinfo(name).file_size,"status":"PASS" if matches or not deep_hash else "SHA256_MISSING_OR_MISMATCH"}
                if deep_hash and not matches:
                    mismatches+=1
                rows.append(rec)
            info["zip_payload_sha256_mismatch_total"]=mismatches
            info["zip_payload_sha256_missing_total"]=missing_sha
            info["status"]="PASS" if bad is None and (not deep_hash or mismatches==0) else "FAIL_ZIP_CONTENT"
    except Exception as e:
        info["status"]="FAIL_ZIP_OPEN"
        info["error"]=str(e)
    return info, rows


def compare_counts(manifest: Dict[str,Any], receipt: Dict[str,Any], machine_index: Dict[str,Any], file_rows: List[Dict[str,Any]], zip_info: Dict[str,Any], sqlite_info: Dict[str,Any], expected_packed: Optional[int]) -> Dict[str,Any]:
    manifest_packed=manifest.get("packed_total") or manifest.get("ready_total") or manifest.get("candidates_total")
    receipt_packed=receipt.get("packed_total")
    machine_items=machine_index.get("items") if isinstance(machine_index,dict) else None
    machine_count=len(machine_items) if isinstance(machine_items,list) else None
    file_count=len(file_rows)
    zip_count=zip_info.get("payload_entries_total")
    sqlite_count=sqlite_info.get("pack_items_count")
    values={"manifest_packed_total":manifest_packed,"receipt_packed_total":receipt_packed,"machine_index_items_total":machine_count,"file_index_rows_total":file_count,"zip_payload_entries_total":zip_count,"sqlite_pack_items_total":sqlite_count,"expected_packed_total":expected_packed}
    normalized=[v for v in values.values() if isinstance(v,int)]
    ok=True
    if expected_packed is not None and any(v != expected_packed for v in normalized if v is not None):
        ok=False
    if normalized and len(set(normalized))>1:
        ok=False
    values["counts_match"]=ok
    return values


def make_dashboard(path: Path, report: Dict[str,Any], sidecars: List[Dict[str,Any]], top: List[Dict[str,Any]], file_rows: List[Dict[str,Any]]) -> None:
    def esc(x: Any) -> str:
        return html.escape(str(x))
    side_rows="\n".join(f"<tr><td><code>{esc(r['name'])}</code></td><td class={'ok' if r['exists'] else 'danger'}>{'YES' if r['exists'] else 'NO'}</td><td>{human_bytes(int(r.get('bytes') or 0))}</td></tr>" for r in sidecars)
    top_rows="\n".join(f"<tr><td><code>{esc(t['folder'])}</code></td><td>{t['count']}</td><td>{human_bytes(int(t['bytes']))}</td><td><div class='bar'><span style='width:{min(100,float(t['share_percent'])):.2f}%'></span></div><span class='pct'>{float(t['share_percent']):.1f}%</span></td></tr>" for t in top)
    first_rows="\n".join(f"<tr><td><code>{esc(r.get('relative_path') or r.get('path') or '')}</code></td><td>{human_bytes(int(r.get('bytes') or r.get('size') or 0))}</td><td><code>{esc((r.get('sha256') or r.get('actual_sha256') or '')[:16])}</code></td></tr>" for r in file_rows[:80])
    status=report['status']
    pack_hash=report.get('pack_zip_sha256','')
    pack_folder=report.get('pack_folder','')
    payload_count=report.get('zip',{}).get('payload_entries_total',0)
    packed_total=report.get('packed_total') or payload_count
    total_bytes=report.get('total_bytes') or 0
    ok_pct=100.0 if status.startswith('PASS') else 0.0
    html_doc=f"""<!doctype html><html lang=\"ru\"><head><meta charset=\"utf-8\"><title>Imperium Evidence Vault Receipt Verification</title><style>
    :root{{--bg:#0d1117;--panel:#151b24;--line:#2b3445;--text:#f2f7ff;--muted:#b8c7e6;--accent:#8bd5ff;--accent2:#dab6ff;--warn:#ffd166;--danger:#ff7b72;--ok:#7ee787;}}
    *{{box-sizing:border-box}} body{{margin:0;padding:24px;background:var(--bg);color:var(--text);font-family:Segoe UI,Arial,sans-serif}} h1,h2{{margin:0 0 14px}} .muted{{color:var(--muted)}}
    .top{{display:flex;justify-content:space-between;gap:12px;align-items:start;border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:22px}} .lang button{{background:#20283a;color:var(--text);border:1px solid #36435c;border-radius:8px;padding:8px 12px;margin-left:6px;cursor:pointer}}.lang button.active{{border-color:var(--accent);box-shadow:0 0 0 2px rgba(139,213,255,.2)}}
    .grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}} .card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}} .label{{text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-size:13px}} .big{{font-size:34px;font-weight:800;margin-top:10px}}
    .owner{{background:linear-gradient(135deg,#17212c,#21172f);border:1px solid var(--line);border-radius:12px;margin:18px 0;padding:20px}} table{{width:100%;border-collapse:collapse;background:var(--panel);border-radius:12px;overflow:hidden;margin:12px 0 28px}} th{{background:#20283a;color:#cfe2ff;text-align:left}} td,th{{border-bottom:1px solid var(--line);padding:11px 12px;vertical-align:top}} code{{font-family:Consolas,monospace;color:#dbeafe}} .bar{{display:inline-block;width:220px;height:11px;background:#30384b;border-radius:99px;overflow:hidden;margin-right:10px}} .bar span{{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2))}} .pct{{color:#cfe2ff}} .pill{{display:inline-block;border:1px solid #2f8ed8;color:#8bd5ff;border-radius:999px;padding:3px 8px;font-size:12px}} .ok{{color:var(--ok)}} .warn{{color:var(--warn)}} .danger{{color:var(--danger)}} .gate{{border-left:4px solid var(--accent);background:#111827;padding:14px 18px;margin-top:22px}} .ru .enOnly{{display:none}} .en .ruOnly{{display:none}} @media(max-width:900px){{.grid{{grid-template-columns:1fr}}.bar{{width:120px}}}}
    </style></head><body class=\"ru\"><div class=\"top\"><div><h1><span class=\"ruOnly\">Imperium Trinity Plus — Верификация Vault receipt Batch 001</span><span class=\"enOnly\">Imperium Trinity Plus — Batch 001 Vault Receipt Verification</span></h1><div class=\"muted\">{esc(report.get('patch_id'))} · {esc(report.get('generated_at_utc'))}</div></div><div class=\"lang\"><button onclick=\"document.body.className='ru';this.classList.add('active');this.nextElementSibling.classList.remove('active')\" class=\"active\">RU</button><button onclick=\"document.body.className='en';this.classList.add('active');this.previousElementSibling.classList.remove('active')\">EN</button></div></div>
    <div class=\"grid\"><div class=\"card\"><div class=\"label ruOnly\">Статус</div><div class=\"label enOnly\">Status</div><div class=\"big\">{esc(status.replace('PASS_','PASS'))}</div><div class=\"bar\"><span style=\"width:{ok_pct:.1f}%\"></span></div><span class=\"pct\">{ok_pct:.1f}%</span></div><div class=\"card\"><div class=\"label ruOnly\">Упаковано</div><div class=\"label enOnly\">Packed</div><div class=\"big\">{packed_total}</div><div class=\"muted\">payload entries verified</div></div><div class=\"card\"><div class=\"label ruOnly\">Объём source</div><div class=\"label enOnly\">Source bytes</div><div class=\"big\">{human_bytes(int(total_bytes))}</div><div class=\"muted\">registered payload size</div></div><div class=\"card\"><div class=\"label\">SHA256</div><div class=\"big\" style=\"font-size:18px\"><code>{esc(str(pack_hash)[:24])}…</code></div><div class=\"muted\">EVIDENCE_PACK.zip</div></div></div>
    <div class=\"owner\"><div class=\"label\">Owner Gate</div><h2 class=\"ruOnly\">Vault pack проверен и зарегистрирован. Это НЕ разрешает удаление source.</h2><h2 class=\"enOnly\">Vault pack verified and registered. This does NOT authorize source deletion.</h2><p class=\"ruOnly\">Следующий этап может готовить cleanup proposal, но фактическое удаление/перемещение source требует отдельного owner gate.</p><p class=\"enOnly\">A later step may prepare a cleanup proposal, but actual source deletion/movement requires a separate owner gate.</p></div>
    <h2 class=\"ruOnly\">Проверки receipt</h2><h2 class=\"enOnly\">Receipt checks</h2><table><tr><th>Status</th><th>Progress</th><th class=\"ruOnly\">Шаг</th><th class=\"enOnly\">Step</th><th>Evidence</th></tr><tr><td><span class=\"pill\">{esc(report.get('sidecars_status'))}</span></td><td><div class=\"bar\"><span style=\"width:{100 if report.get('sidecars_status')=='PASS' else 0}%\"></span></div></td><td class=\"ruOnly\">Sidecars присутствуют</td><td class=\"enOnly\">Sidecars present</td><td>{len([s for s in sidecars if s.get('exists')])}/{len(sidecars)}</td></tr><tr><td><span class=\"pill\">{esc(report.get('zip',{}).get('status'))}</span></td><td><div class=\"bar\"><span style=\"width:{100 if report.get('zip',{}).get('status')=='PASS' else 0}%\"></span></div></td><td class=\"ruOnly\">ZIP открывается и payload hash совпадает</td><td class=\"enOnly\">ZIP opens and payload hashes match</td><td>payload={payload_count}</td></tr><tr><td><span class=\"pill\">{esc(report.get('sqlite',{}).get('status'))}</span></td><td><div class=\"bar\"><span style=\"width:{100 if report.get('sqlite',{}).get('status')=='PASS' else 0}%\"></span></div></td><td class=\"ruOnly\">SQLite index валиден</td><td class=\"enOnly\">SQLite index valid</td><td>pack_items={esc(report.get('sqlite',{}).get('pack_items_count'))}</td></tr><tr><td><span class=\"pill\">{esc('PASS' if report.get('counts',{}).get('counts_match') else 'FAIL')}</span></td><td><div class=\"bar\"><span style=\"width:{100 if report.get('counts',{}).get('counts_match') else 0}%\"></span></div></td><td class=\"ruOnly\">Counts согласованы</td><td class=\"enOnly\">Counts consistent</td><td>{esc(report.get('counts'))}</td></tr></table>
    <h2>Vault output</h2><table><tr><th>Artifact</th><th>Path</th></tr><tr><td>Pack folder</td><td><code>{esc(pack_folder)}</code></td></tr><tr><td>EVIDENCE_PACK.zip</td><td><code>{esc(report.get('pack_zip'))}</code></td></tr><tr><td>Data Atlas registration</td><td><code>{esc(report.get('data_atlas_registration'))}</code></td></tr></table>
    <h2 class=\"ruOnly\">Sidecars</h2><h2 class=\"enOnly\">Sidecars</h2><table><tr><th>Name</th><th>Exists</th><th>Bytes</th></tr>{side_rows}</table>
    <h2 class=\"ruOnly\">Главные папки pack</h2><h2 class=\"enOnly\">Top pack folders</h2><table><tr><th>Folder</th><th>Count</th><th>Bytes</th><th>Share</th></tr>{top_rows}</table>
    <h2 class=\"ruOnly\">Первые записи</h2><h2 class=\"enOnly\">First records</h2><table><tr><th>Path</th><th>Bytes</th><th>SHA256 prefix</th></tr>{first_rows}</table><div class=\"gate\"><b>Owner gate:</b> <span class=\"ruOnly\">verification/registration разрешают только cleanup proposal, не удаление.</span><span class=\"enOnly\">verification/registration authorizes cleanup proposal only, not deletion.</span></div></body></html>"""
    path.write_text(html_doc, encoding="utf-8")


def write_sqlite(path: Path, report: Dict[str,Any], sidecars: List[Dict[str,Any]], zip_rows: List[Dict[str,Any]], file_rows: List[Dict[str,Any]]) -> None:
    if path.exists(): path.unlink()
    con=sqlite3.connect(str(path))
    try:
        con.execute("create table verification_manifest(key text primary key, value text)")
        con.execute("create table sidecars(name text primary key, exists_on_disk integer, bytes integer, status text)")
        con.execute("create table zip_payload(relative_path text primary key, bytes integer, expected_sha256 text, actual_sha256 text, sha256_matches integer, status text)")
        con.execute("create table file_index(relative_path text primary key, bytes integer, sha256 text, status text)")
        for k,v in report.items():
            if isinstance(v,(dict,list)):
                v=json.dumps(v, ensure_ascii=False, sort_keys=True)
            con.execute("insert into verification_manifest values(?,?)",(str(k),str(v)))
        con.executemany("insert into sidecars values(?,?,?,?)", [(r['name'],1 if r['exists'] else 0,int(r.get('bytes') or 0),r['status']) for r in sidecars])
        con.executemany("insert into zip_payload values(?,?,?,?,?,?)", [(r.get('relative_path'),int(r.get('bytes') or 0),r.get('expected_sha256'),r.get('actual_sha256'),1 if r.get('sha256_matches') is True else 0,r.get('status')) for r in zip_rows])
        con.executemany("insert into file_index values(?,?,?,?)", [(str(r.get('relative_path') or r.get('path') or ''),int(r.get('bytes') or r.get('size') or 0),r.get('sha256') or r.get('actual_sha256'),r.get('status','')) for r in file_rows if (r.get('relative_path') or r.get('path'))])
        con.commit()
    finally:
        con.close()


def build(args: argparse.Namespace) -> Dict[str,Any]:
    repo=Path(args.repo).resolve() if args.repo else None
    pack_folder=Path(args.pack_folder).resolve()
    out_root=Path(args.out_root).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    generated=utc_now()
    patch_id=args.patch_id or "EVIDENCE-VAULT-BATCH-001-RECEIPT-VERIFY-REGISTER"
    expected_sha=(args.expected_pack_sha256 or EXPECTED_SHA_DEFAULT).lower() if args.expected_pack_sha256 != "NONE" else None
    expected_packed=args.expected_packed_total
    expected_bytes=args.expected_total_bytes

    git=git_info(repo)
    sidecars, side_ok = sidecar_checks(pack_folder)
    manifest=read_json(pack_folder/"EVIDENCE_MANIFEST.json") if (pack_folder/"EVIDENCE_MANIFEST.json").exists() else {}
    receipt=read_json(pack_folder/"MACHINE_RECEIPT.json") if (pack_folder/"MACHINE_RECEIPT.json").exists() else {}
    machine_index=read_json(pack_folder/"MACHINE_INDEX.json") if (pack_folder/"MACHINE_INDEX.json").exists() else {}
    file_rows=read_jsonl(pack_folder/"EVIDENCE_FILE_INDEX.jsonl") if (pack_folder/"EVIDENCE_FILE_INDEX.jsonl").exists() else []
    sha_map=parse_sha256s(pack_folder/"SHA256SUMS.txt")
    zip_info, zip_rows = zip_checks(pack_folder/"EVIDENCE_PACK.zip", sha_map, deep_hash=not args.no_deep_zip_hash)
    sqlite_info=sqlite_checks(pack_folder/"EVIDENCE_VAULT_BATCH_001_PACK_EXECUTION.sqlite")
    counts=compare_counts(manifest, receipt, machine_index, file_rows, zip_info, sqlite_info, expected_packed)

    actual_sha=zip_info.get("zip_sha256")
    hash_ok=True
    hash_sources=[]
    for label,obj,key in [
        ("expected", {"sha":expected_sha}, "sha"),
        ("manifest", manifest, "pack_zip_sha256"),
        ("receipt", receipt, "pack_zip_sha256"),
        ("sha256s", {"sha":sha_map.get("EVIDENCE_PACK.zip")}, "sha"),
    ]:
        val=obj.get(key) if isinstance(obj,dict) else None
        if val:
            hash_sources.append({"source":label,"sha256":str(val).lower(),"matches_actual":str(val).lower()==str(actual_sha).lower()})
            if str(val).lower()!=str(actual_sha).lower():
                hash_ok=False
    total_bytes = int(manifest.get("total_bytes") or sum(int(r.get("bytes") or r.get("size") or 0) for r in file_rows))
    bytes_ok = True if expected_bytes is None else (int(expected_bytes)==total_bytes)
    status_ok = side_ok and hash_ok and bytes_ok and zip_info.get("status")=="PASS" and sqlite_info.get("status")=="PASS" and counts.get("counts_match")
    status="PASS_EVIDENCE_VAULT_BATCH_RECEIPT_VERIFIED_REGISTERED" if status_ok else "FAIL_EVIDENCE_VAULT_BATCH_RECEIPT_VERIFICATION"

    registration={
        "schema":"imperium.data_atlas.evidence_vault_batch_registration.v0_1",
        "surface":"ADMINISTRATUM_DATA_ATLAS_EVIDENCE_VAULT_BATCH_REGISTRATION",
        "status":"REGISTERED" if status_ok else "REGISTRATION_BLOCKED_BY_VERIFICATION_FAILURE",
        "generated_at_utc":generated,
        "batch_id":args.batch_id,
        "hygiene_lane":"REPORTS_LEGACY / PACK_TO_VAULT",
        "source_head":manifest.get("source_head"),
        "source_short_head":manifest.get("source_short_head"),
        "source_branch":manifest.get("source_branch"),
        "current_h_head":git.get("head"),
        "current_h_short_head":git.get("short_head"),
        "pack_folder":str(pack_folder),
        "pack_zip":str(pack_folder/"EVIDENCE_PACK.zip"),
        "pack_zip_sha256":actual_sha,
        "pack_zip_bytes":zip_info.get("zip_bytes"),
        "packed_total":counts.get("zip_payload_entries_total"),
        "file_index_rows_total":counts.get("file_index_rows_total"),
        "total_bytes":total_bytes,
        "total_bytes_human":human_bytes(total_bytes),
        "verification_report":"EVIDENCE_VAULT_BATCH_001_RECEIPT_VERIFICATION_REPORT.json",
        "source_cleanup_state":"VAULT_COPY_VERIFIED_SOURCE_STILL_PRESENT_CLEANUP_NOT_AUTHORIZED",
        "owner_gate":"Registration permits cleanup proposal planning only; source deletion/move remains blocked.",
    }
    reg_path=out_root/"EVIDENCE_VAULT_BATCH_001_DATA_ATLAS_REGISTRATION.json"

    report={
        "schema":SCHEMA,
        "surface":SURFACE,
        "version":VERSION,
        "status":status,
        "generated_at_utc":generated,
        "patch_id":patch_id,
        "batch_id":args.batch_id,
        "repo":str(repo) if repo else None,
        "git":git,
        "pack_folder":str(pack_folder),
        "pack_zip":str(pack_folder/"EVIDENCE_PACK.zip"),
        "pack_zip_sha256":actual_sha,
        "expected_pack_sha256":expected_sha,
        "packed_total":counts.get("zip_payload_entries_total"),
        "expected_packed_total":expected_packed,
        "total_bytes":total_bytes,
        "total_bytes_human":human_bytes(total_bytes),
        "expected_total_bytes":expected_bytes,
        "sidecars_status":"PASS" if side_ok else "FAIL",
        "hash_status":"PASS" if hash_ok else "FAIL",
        "bytes_status":"PASS" if bytes_ok else "FAIL",
        "sidecars":sidecars,
        "hash_sources":hash_sources,
        "zip":zip_info,
        "sqlite":sqlite_info,
        "counts":counts,
        "data_atlas_registration":str(reg_path),
        "owner_gate":"Verified Vault receipt + Data Atlas registration; no source deletion/move authorized.",
    }

    top=top_dirs(file_rows if file_rows else zip_rows)
    write_json(reg_path, registration)
    write_json(out_root/"EVIDENCE_VAULT_BATCH_001_RECEIPT_VERIFICATION_REPORT.json", report)
    write_jsonl(out_root/"EVIDENCE_VAULT_BATCH_001_ZIP_PAYLOAD_VERIFICATION.jsonl", zip_rows)
    write_csv(out_root/"EVIDENCE_VAULT_BATCH_001_ZIP_PAYLOAD_VERIFICATION.csv", zip_rows, ["relative_path","bytes","expected_sha256","actual_sha256","sha256_matches","status"])
    write_sqlite(out_root/"EVIDENCE_VAULT_BATCH_001_RECEIPT_VERIFICATION.sqlite", report, sidecars, zip_rows, file_rows)
    make_dashboard(out_root/"EVIDENCE_VAULT_BATCH_001_RECEIPT_VERIFICATION_VISUAL_PROOF_DASHBOARD.html", report, sidecars, top, file_rows if file_rows else zip_rows)
    (out_root/"EVIDENCE_VAULT_BATCH_001_RECEIPT_VERIFICATION_TERMINAL_RU_EN.txt").write_text(
        f"""Imperium Evidence Vault Batch 001 Receipt Verification\nStatus: {status}\nPack folder: {pack_folder}\nPayload entries: {counts.get('zip_payload_entries_total')}\nFile index rows: {counts.get('file_index_rows_total')}\nZIP SHA256: {actual_sha}\nTotal bytes: {human_bytes(total_bytes)}\nData Atlas registration: {reg_path}\nOwner gate: registration allows cleanup proposal only; no source deletion/move.\n""", encoding="utf-8")
    print(json.dumps({
        "status":status,
        "pack_folder":str(pack_folder),
        "pack_zip_sha256":actual_sha,
        "packed_total":counts.get("zip_payload_entries_total"),
        "file_index_rows_total":counts.get("file_index_rows_total"),
        "sqlite_pack_items_total":sqlite_info.get("pack_items_count"),
        "total_bytes":total_bytes,
        "sidecars_status":report["sidecars_status"],
        "hash_status":report["hash_status"],
        "zip_status":zip_info.get("status"),
        "sqlite_status":sqlite_info.get("status"),
        "counts_match":counts.get("counts_match"),
        "data_atlas_registration":str(reg_path),
        "dashboard":str(out_root/"EVIDENCE_VAULT_BATCH_001_RECEIPT_VERIFICATION_VISUAL_PROOF_DASHBOARD.html"),
        "owner_gate":report["owner_gate"],
    }, ensure_ascii=False, indent=2))
    return report


def main(argv: Optional[List[str]]=None) -> int:
    ap=argparse.ArgumentParser(description="Verify Evidence Vault Batch 001 receipt and emit Data Atlas registration.")
    ap.add_argument("--repo", default=None)
    ap.add_argument("--pack-folder", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--batch-id", default=BATCH_ID_DEFAULT)
    ap.add_argument("--patch-id", default="SMOKE-V0_9_6-EVIDENCE-VAULT-BATCH-001-RECEIPT-VERIFY-REGISTER")
    ap.add_argument("--expected-pack-sha256", default=EXPECTED_SHA_DEFAULT, help="Expected EVIDENCE_PACK.zip SHA256; pass NONE to disable.")
    ap.add_argument("--expected-packed-total", type=int, default=EXPECTED_PACKED_DEFAULT)
    ap.add_argument("--expected-total-bytes", type=int, default=EXPECTED_BYTES_DEFAULT)
    ap.add_argument("--no-deep-zip-hash", action="store_true", help="Skip per-payload hash verification; not recommended for real receipt verification.")
    args=ap.parse_args(argv)
    build(args)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
