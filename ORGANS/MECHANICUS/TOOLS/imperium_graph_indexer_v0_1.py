#!/usr/bin/env python3
"""MECHANICUS Imperium Graph Indexer v0_1.

Walks the Imperium repo and emits a graph snapshot conforming to schema
`imperium.graph.v0_1` (see ORGANS/DOCTRINARIUM/IMPERIUM_GRAPH.md).

Node types (9): organ, sub_organ, doctrine, agent, task, land, receipt,
sentinel, thread.
Edge types (10): parent_of, owns, declares_base, lands_after, ratifies,
gates, produces, references, monitors, succeeds.

Output is deterministic: nodes sorted by (type, id), edges sorted by
(type, src, dst). Only `generated_at` is non-deterministic; pass
`--frozen-time` to override for idempotency tests.

Usage:
    python3 imperium_graph_indexer_v0_1.py --repo-root . \
        --out SUPPORT/graph_snapshot.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = "imperium.graph.v0_1"
GENERATOR = "mechanicus.imperium_graph_indexer.v0_1"

REQUIRED_ORGANS = {
    "ADMINISTRATUM", "ASTRONOMICON", "CUSTODES", "DOCTRINARIUM", "INQUISITION",
    "MECHANICUS", "OFFICIO_AGENTIS", "SCHOLA_IMPERIALIS", "STRATEGIUM",
}
KNOWN_EXTRA_ORGANS = {"_CORE_GOVERNANCE", "_POST_WORK_RING", "IMPERIAL_IDE", "SPECULUM"}

NODE_TYPES = (
    "organ", "sub_organ", "doctrine", "agent", "task",
    "land", "receipt", "sentinel", "thread",
)
EDGE_TYPES = (
    "parent_of", "owns", "declares_base", "lands_after", "ratifies",
    "gates", "produces", "references", "monitors", "succeeds",
)

LAND_COMMIT_RE = re.compile(r"^([A-Z][A-Z0-9_-]*-\d+):\s")
SENTINEL_NAME_HINT = re.compile(r"sentinel|burnout|monitor|watcher", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def norm_rel(p: Path, repo_root: Path) -> str:
    return str(p.relative_to(repo_root)).replace(chr(92), "/")


def _count_by(items: list, key: str) -> dict:
    out: dict = {}
    for it in items:
        v = it.get(key)
        out[v] = out.get(v, 0) + 1
    return dict(sorted(out.items()))


def git_available(repo_root: Path) -> bool:
    try:
        r = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--git-dir"],
            capture_output=True, text=True, timeout=10,
        )
        return r.returncode == 0
    except Exception:
        return False


def git_log_lands(repo_root: Path) -> list:
    if not git_available(repo_root):
        return []
    try:
        # Use ASCII record separator (0x1e) between commits and tabs between fields.
        fmt = "%H%x09%P%x09%aI%x09%s%x1e"
        r = subprocess.run(
            ["git", "-C", str(repo_root), "log", "--format=" + fmt, "HEAD"],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0:
            return []
        out = []
        for chunk in r.stdout.split("\x1e"):
            chunk = chunk.strip("\n")
            if not chunk:
                continue
            parts = chunk.split("\t")
            if len(parts) < 4:
                continue
            sha = parts[0].strip()
            parents = parts[1].split() if parts[1].strip() else []
            date = parts[2].strip()
            subject = parts[3]
            out.append({
                "sha": sha, "parents": parents, "date": date, "subject": subject,
            })
        return out
    except Exception:
        return []


def git_files_changed(repo_root: Path, sha: str) -> list:
    try:
        r = subprocess.run(
            ["git", "-C", str(repo_root), "show", "--no-patch", "--name-only", "--format=", sha],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0:
            return []
        return [ln.strip().replace(chr(92), "/") for ln in r.stdout.splitlines() if ln.strip()]
    except Exception:
        return []


def walk_organs(repo_root: Path) -> dict:
    organs_dir = repo_root / "ORGANS"
    out = {}
    if not organs_dir.is_dir():
        return out
    for child in sorted(organs_dir.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            continue
        subs = []
        for sub in sorted(child.iterdir(), key=lambda p: p.name):
            if sub.is_dir():
                subs.append(sub.name)
        out[child.name] = {"sub_organs": subs, "path": "ORGANS/" + child.name}
    return out


def walk_doctrines(repo_root: Path) -> list:
    d = repo_root / "ORGANS" / "DOCTRINARIUM"
    out = []
    if not d.is_dir():
        return out
    for f in sorted(d.rglob("*.md"), key=lambda p: str(p)):
        rel = norm_rel(f, repo_root)
        title = f.stem
        try:
            for line in f.read_text(encoding="utf-8-sig").splitlines()[:50]:
                m = re.match(r"^#\s+(.+?)\s*$", line)
                if m:
                    title = m.group(1).strip()
                    break
        except Exception:
            pass
        out.append({"path": rel, "title": title, "name": f.stem})
    return out


def walk_receipts(repo_root: Path) -> list:
    out = []
    organs = repo_root / "ORGANS"
    if not organs.is_dir():
        return out
    for reports in sorted(organs.glob("*/REPORTS"), key=lambda p: str(p)):
        for f in sorted(reports.glob("*.json"), key=lambda p: p.name):
            try:
                data = json.loads(f.read_text(encoding="utf-8-sig"))
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            sv = str(data.get("schema_version", ""))
            if not sv.startswith("imperium.kernel_write_guard"):
                continue
            out.append({
                "path": norm_rel(f, repo_root),
                "task_id": data.get("task_id"),
                "verdict": data.get("verdict"),
                "declared_base": data.get("declared_base"),
                "live_head": data.get("live_head"),
                "verified_at": data.get("verified_at"),
            })
    return out


def walk_sentinels(repo_root: Path) -> list:
    out = []
    organs = repo_root / "ORGANS"
    if not organs.is_dir():
        return out
    for f in sorted(organs.rglob("*.py"), key=lambda p: str(p)):
        if SENTINEL_NAME_HINT.search(f.name):
            out.append({"path": norm_rel(f, repo_root), "name": f.stem})
    return out


def build_graph(repo_root: Path, frozen_time: Optional[str] = None) -> dict:
    nodes: list = []
    edges: list = []

    # ---- structural: organs + sub_organs ----
    organs = walk_organs(repo_root)
    for organ_name, organ_info in organs.items():
        organ_id = "organ:" + organ_name
        nodes.append({
            "id": organ_id,
            "type": "organ",
            "name": organ_name,
            "path": organ_info["path"],
            "canonical": organ_name in REQUIRED_ORGANS,
            "known_extra": organ_name in KNOWN_EXTRA_ORGANS,
        })
        for sub in organ_info["sub_organs"]:
            sub_id = "sub_organ:" + organ_name + "/" + sub
            nodes.append({
                "id": sub_id,
                "type": "sub_organ",
                "name": sub,
                "parent": organ_name,
                "path": "ORGANS/" + organ_name + "/" + sub,
            })
            edges.append({
                "id": "parent_of:" + organ_id + "->" + sub_id,
                "type": "parent_of", "src": organ_id, "dst": sub_id,
            })
            edges.append({
                "id": "owns:" + organ_id + "->" + sub_id,
                "type": "owns", "src": organ_id, "dst": sub_id,
            })

    # ---- doctrines ----
    doctrines = walk_doctrines(repo_root)
    doctrine_by_path = {}
    for d in doctrines:
        d_id = "doctrine:" + d["path"]
        nodes.append({
            "id": d_id,
            "type": "doctrine",
            "name": d["name"],
            "title": d["title"],
            "path": d["path"],
        })
        doctrine_by_path[d["path"]] = d_id
        if "organ:DOCTRINARIUM" in (n["id"] for n in nodes):
            edges.append({
                "id": "parent_of:organ:DOCTRINARIUM->" + d_id,
                "type": "parent_of",
                "src": "organ:DOCTRINARIUM",
                "dst": d_id,
            })

    # ---- references between doctrines (markdown links to *.md in same dir) ----
    for d in doctrines:
        f = repo_root / d["path"]
        try:
            content = f.read_text(encoding="utf-8-sig")
        except Exception:
            continue
        for m in re.finditer(r"\[[^\]]+\]\(([^)]+\.md)\)", content):
            tgt_raw = m.group(1).strip()
            try:
                resolved = (f.parent / tgt_raw).resolve()
                tgt_rel = norm_rel(resolved, repo_root)
            except Exception:
                continue
            if tgt_rel in doctrine_by_path and tgt_rel != d["path"]:
                src_id = "doctrine:" + d["path"]
                dst_id = "doctrine:" + tgt_rel
                edges.append({
                    "id": "references:" + src_id + "->" + dst_id,
                    "type": "references", "src": src_id, "dst": dst_id,
                })

    # ---- sentinels ----
    sentinels = walk_sentinels(repo_root)
    for s in sentinels:
        s_id = "sentinel:" + s["path"]
        nodes.append({
            "id": s_id, "type": "sentinel", "name": s["name"], "path": s["path"],
        })
        # link to owning organ if discoverable from path
        parts = s["path"].split("/")
        if len(parts) >= 2 and parts[0] == "ORGANS":
            o_id = "organ:" + parts[1]
            edges.append({
                "id": "owns:" + o_id + "->" + s_id,
                "type": "owns", "src": o_id, "dst": s_id,
            })
            # sentinel monitors its own organ by default
            edges.append({
                "id": "monitors:" + s_id + "->" + o_id,
                "type": "monitors", "src": s_id, "dst": o_id,
            })

    # ---- receipts ----
    receipts = walk_receipts(repo_root)
    for r in receipts:
        r_id = "receipt:" + r["path"]
        nodes.append({
            "id": r_id,
            "type": "receipt",
            "path": r["path"],
            "task_id": r.get("task_id"),
            "verdict": r.get("verdict"),
            "declared_base": r.get("declared_base"),
            "verified_at": r.get("verified_at"),
        })

    # ---- lands (git commits) ----
    lands = git_log_lands(repo_root)
    land_id_by_sha = {}
    task_ids_seen = set()
    for c in lands:
        sha = c["sha"]
        l_id = "land:" + sha
        land_id_by_sha[sha] = l_id
        m = LAND_COMMIT_RE.match(c["subject"])
        task_id = m.group(1) if m else None
        nodes.append({
            "id": l_id,
            "type": "land",
            "sha": sha,
            "short_sha": sha[:12],
            "subject": c["subject"],
            "task_id": task_id,
            "date": c["date"],
            "parents": c["parents"],
        })
        if task_id and task_id not in task_ids_seen:
            t_id = "task:" + task_id
            nodes.append({
                "id": t_id, "type": "task", "task_id": task_id,
            })
            task_ids_seen.add(task_id)
            edges.append({
                "id": "produces:" + t_id + "->" + l_id,
                "type": "produces", "src": t_id, "dst": l_id,
            })
        # produces edges from land to touched organs
        files = git_files_changed(repo_root, sha)
        produced = set()
        for fp in files:
            ps = fp.split("/")
            if len(ps) >= 2 and ps[0] == "ORGANS":
                org = ps[1]
                if org in produced:
                    continue
                produced.add(org)
                o_id = "organ:" + org
                edges.append({
                    "id": "produces:" + l_id + "->" + o_id,
                    "type": "produces", "src": l_id, "dst": o_id,
                })

    # ---- lands_after (linear history) ----
    for c in lands:
        l_id = land_id_by_sha[c["sha"]]
        for p in c["parents"]:
            if p in land_id_by_sha:
                p_id = land_id_by_sha[p]
                edges.append({
                    "id": "lands_after:" + l_id + "->" + p_id,
                    "type": "lands_after", "src": l_id, "dst": p_id,
                })

    # ---- declares_base + gates edges (receipts <-> lands) ----
    receipt_by_task = {r.get("task_id"): r for r in receipts if r.get("task_id")}
    for r in receipts:
        db = r.get("declared_base")
        if db and db in land_id_by_sha:
            r_id = "receipt:" + r["path"]
            edges.append({
                "id": "declares_base:" + r_id + "->land:" + db,
                "type": "declares_base", "src": r_id, "dst": "land:" + db,
            })
    for c in lands:
        l_id = land_id_by_sha[c["sha"]]
        m = LAND_COMMIT_RE.match(c["subject"])
        if not m:
            continue
        task = m.group(1)
        r = receipt_by_task.get(task)
        if not r:
            continue
        r_id = "receipt:" + r["path"]
        edges.append({
            "id": "gates:" + r_id + "->" + l_id,
            "type": "gates", "src": r_id, "dst": l_id,
        })

    # ---- sort + dedup ----
    # Dedup nodes by id (first wins)
    seen_n = set()
    nodes_uniq = []
    for n in nodes:
        if n["id"] in seen_n:
            continue
        seen_n.add(n["id"])
        nodes_uniq.append(n)
    nodes_sorted = sorted(nodes_uniq, key=lambda n: (n["type"], n["id"]))

    edge_dedup = {}
    for e in edges:
        edge_dedup[e["id"]] = e
    # drop edges with endpoints not in node set
    node_ids = set(n["id"] for n in nodes_sorted)
    edges_resolved = [e for e in edge_dedup.values() if e["src"] in node_ids and e["dst"] in node_ids]
    edges_sorted = sorted(edges_resolved, key=lambda e: (e["type"], e["src"], e["dst"]))

    generated_at = frozen_time if frozen_time else utc_now()

    return {
        "schema": SCHEMA_VERSION,
        "generator": GENERATOR,
        "generated_at": generated_at,
        "repo_name": repo_root.name,
        "counts": {
            "nodes": len(nodes_sorted),
            "edges": len(edges_sorted),
            "by_node_type": _count_by(nodes_sorted, "type"),
            "by_edge_type": _count_by(edges_sorted, "type"),
        },
        "nodes": nodes_sorted,
        "edges": edges_sorted,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="MECHANICUS Imperium Graph Indexer v0_1")
    p.add_argument("--repo-root", required=True, help="path to Imperium repo root")
    p.add_argument("--out", default="", help="output path (default: <repo>/SUPPORT/graph_snapshot.json)")
    p.add_argument("--frozen-time", default="", help="override generated_at for deterministic tests")
    p.add_argument("--print-only", action="store_true", help="emit to stdout, do not write file")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        print(json.dumps({"error": "repo_root not a directory: " + str(repo_root)}))
        return 2
    graph = build_graph(repo_root, frozen_time=args.frozen_time or None)
    text = json.dumps(graph, ensure_ascii=True, indent=2, sort_keys=False)
    if args.print_only:
        print(text)
        return 0
    out = Path(args.out) if args.out else (repo_root / "SUPPORT" / "graph_snapshot.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    counts = graph["counts"]
    print("[indexer] wrote %s (nodes=%d edges=%d)" % (out, counts["nodes"], counts["edges"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
