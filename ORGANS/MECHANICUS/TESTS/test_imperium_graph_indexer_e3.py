#!/usr/bin/env python3
"""E3 self-test for MECHANICUS Imperium Graph Indexer v0_1.

10 tests:
  T1  schema_present              snapshot carries imperium.graph.v0_1
  T2  node_types_in_vocabulary    every node.type is in the 9-vocab
  T3  edge_types_in_vocabulary    every edge.type is in the 10-vocab
  T4  idempotent                  two runs with same --frozen-time => byte-identical
  T5  required_organs_present     all 9 canonical organs appear as nodes
  T6  doctrines_detected          EYES_V2 + IMPERIUM_GRAPH found in DOCTRINARIUM
  T7  references_resolved         doctrine->doctrine markdown link resolves
  T8  lands_and_tasks_detected    git log produces land + task nodes via subject regex
  T9  edges_resolve               every edge endpoint is a real node id
  T10 empty_repo_graceful         empty dir yields valid empty snapshot, no crash
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def _load_indexer():
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent / "TOOLS" / "imperium_graph_indexer_v0_1.py",
        here.parent.parent / "MECHANICUS" / "TOOLS" / "imperium_graph_indexer_v0_1.py",
    ]
    for c in candidates:
        if c.exists():
            spec = importlib.util.spec_from_file_location("imperium_graph_indexer_v0_1", c)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise SystemExit("indexer module not found in expected sibling locations")


def _git(repo: Path, *args):
    env = os.environ.copy()
    env.update({
        "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "t@t",
        "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
        "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z",
    })
    return subprocess.run(["git", "-C", str(repo)] + list(args),
                          capture_output=True, text=True, env=env)


def _make_repo(tmp: Path) -> Path:
    repo = tmp / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "master")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "Test")
    organs = [
        "ADMINISTRATUM", "ASTRONOMICON", "CUSTODES", "DOCTRINARIUM",
        "INQUISITION", "MECHANICUS", "OFFICIO_AGENTIS", "SCHOLA_IMPERIALIS",
        "STRATEGIUM",
    ]
    for o in organs:
        (repo / "ORGANS" / o).mkdir(parents=True)
        (repo / "ORGANS" / o / ".keep").write_text("", encoding="utf-8")
    (repo / "ORGANS" / "INQUISITION" / "TOOLS").mkdir()
    (repo / "ORGANS" / "INQUISITION" / "REPORTS").mkdir()
    (repo / "ORGANS" / "DOCTRINARIUM" / "EYES_V2.md").write_text(
        "# EYES V2\n\nSee [GRAPH](IMPERIUM_GRAPH.md) for the graph spec.\n",
        encoding="utf-8",
    )
    (repo / "ORGANS" / "DOCTRINARIUM" / "IMPERIUM_GRAPH.md").write_text(
        "# Imperium Graph\n\n9 node types, 10 edge types.\n",
        encoding="utf-8",
    )
    (repo / "ORGANS" / "INQUISITION" / "TOOLS" / "owner_burnout_sentinel.py").write_text(
        "# sentinel\n", encoding="utf-8",
    )
    receipt_path = repo / "ORGANS" / "INQUISITION" / "REPORTS" / "last_land_gate_receipt.json"
    receipt = {
        "schema_version": "imperium.kernel_write_guard.v0_1",
        "task_id": "TEST-LAND-0002",
        "verdict": "ALLOW",
        "declared_base": "PARENT_PLACEHOLDER",
        "live_head": "PARENT_PLACEHOLDER",
        "verified_at": "2026-01-01T00:00:00Z",
    }
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "TEST-LAND-0001: init canon")
    parent_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    receipt["declared_base"] = parent_sha
    receipt["live_head"] = parent_sha
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "TEST-LAND-0002: second land")
    return repo


PASS = "[PASS]"
FAIL = "[FAIL]"


def run_tests() -> int:
    mod = _load_indexer()
    failures = []

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        repo = _make_repo(tmp)

        g1 = mod.build_graph(repo, frozen_time="2026-01-01T00:00:00Z")
        g2 = mod.build_graph(repo, frozen_time="2026-01-01T00:00:00Z")

        # T1
        if g1.get("schema") == "imperium.graph.v0_1":
            print(PASS, "T1_schema_present")
        else:
            print(FAIL, "T1_schema_present", g1.get("schema"))
            failures.append("T1")

        # T2
        n_types = set(n["type"] for n in g1["nodes"])
        if n_types and n_types.issubset(set(mod.NODE_TYPES)):
            print(PASS, "T2_node_types_in_vocabulary")
        else:
            print(FAIL, "T2_node_types_in_vocabulary", n_types - set(mod.NODE_TYPES))
            failures.append("T2")

        # T3
        e_types = set(e["type"] for e in g1["edges"])
        if e_types and e_types.issubset(set(mod.EDGE_TYPES)):
            print(PASS, "T3_edge_types_in_vocabulary")
        else:
            print(FAIL, "T3_edge_types_in_vocabulary", e_types - set(mod.EDGE_TYPES))
            failures.append("T3")

        # T4 idempotent
        s1 = json.dumps(g1, sort_keys=True)
        s2 = json.dumps(g2, sort_keys=True)
        if s1 == s2:
            print(PASS, "T4_idempotent")
        else:
            print(FAIL, "T4_idempotent")
            failures.append("T4")

        # T5 required organs
        organ_names = set(n["name"] for n in g1["nodes"] if n["type"] == "organ")
        missing = mod.REQUIRED_ORGANS - organ_names
        if not missing:
            print(PASS, "T5_required_organs_present")
        else:
            print(FAIL, "T5_required_organs_present", missing)
            failures.append("T5")

        # T6 doctrines
        d_names = set(n["name"] for n in g1["nodes"] if n["type"] == "doctrine")
        if "EYES_V2" in d_names and "IMPERIUM_GRAPH" in d_names:
            print(PASS, "T6_doctrines_detected")
        else:
            print(FAIL, "T6_doctrines_detected", d_names)
            failures.append("T6")

        # T7 references
        refs = [e for e in g1["edges"] if e["type"] == "references"]
        ok = any(e["src"].endswith("EYES_V2.md") and e["dst"].endswith("IMPERIUM_GRAPH.md")
                 for e in refs)
        if ok:
            print(PASS, "T7_references_resolved")
        else:
            print(FAIL, "T7_references_resolved", refs)
            failures.append("T7")

        # T8 lands + tasks
        tasks = set(n["task_id"] for n in g1["nodes"] if n["type"] == "task")
        lands = [n for n in g1["nodes"] if n["type"] == "land"]
        if "TEST-LAND-0001" in tasks and "TEST-LAND-0002" in tasks and len(lands) == 2:
            print(PASS, "T8_lands_and_tasks_detected")
        else:
            print(FAIL, "T8_lands_and_tasks_detected", tasks, len(lands))
            failures.append("T8")

        # T9 edges resolve
        node_ids = set(n["id"] for n in g1["nodes"])
        bad = [e for e in g1["edges"] if e["src"] not in node_ids or e["dst"] not in node_ids]
        if not bad:
            print(PASS, "T9_edges_resolve")
        else:
            print(FAIL, "T9_edges_resolve", bad[:3])
            failures.append("T9")

        # T10 empty repo
        empty = tmp / "empty"
        empty.mkdir()
        g_empty = mod.build_graph(empty, frozen_time="2026-01-01T00:00:00Z")
        if (g_empty["schema"] == "imperium.graph.v0_1"
                and g_empty["counts"]["nodes"] == 0
                and g_empty["counts"]["edges"] == 0):
            print(PASS, "T10_empty_repo_graceful")
        else:
            print(FAIL, "T10_empty_repo_graceful", g_empty["counts"])
            failures.append("T10")

    print()
    if failures:
        print("FAILED:", ",".join(failures))
        print("E3 RESULT: FAILED")
        return 1
    print("10/10 PASSED")
    print("E3 RESULT: ALL PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())
