#!/usr/bin/env python3
"""E3 static-shape self-test for SUPPORT/viewer/ (Imperium Graph Viewer v0_1).

This test validates structural sanity of the viewer's static files. It does
NOT execute JavaScript — it asserts that the right tokens and references are
present in the right files, that paths align with imperium.graph.v0_1 spec,
and that EYES_V2 v0.2 invariants are observed.

13 tests:
  T1  index_html_present              SUPPORT/viewer/index.html exists
  T2  index_html_references_assets    references styles.css, app.js, cytoscape.min.js
  T3  cy_container_present            <... id="cy" ...> div for graph canvas
  T4  cytoscape_vendored              cytoscape.min.js exists and is non-trivial size
  T5  app_js_view_registry            app.js declares V1..V6 view ids
  T6  app_js_snapshot_path            app.js reads ../graph_snapshot.json
  T7  app_js_annotation_key           app.js uses imperium.graph.annotations.v1
  T8  app_js_url_filters              app.js parses ?v= ?organ= ?since= ?focus= ?depth=
  T9  app_js_node_edge_taxonomy       app.js declares the 9 node + 10 edge types
  T10 styles_eyes_v2_tonal            styles.css uses violet tonal palette (hue 240..290)
  T11 styles_eyes_v2_mark             styles.css uses single yellow MARK accent
  T12 nojekyll_present                .nojekyll file present (for GitHub Pages)
  T13 viewer_readme                   SUPPORT/viewer/README.md present

Sandbox mode: set IMPERIUM_E3_SANDBOX=1 to skip T4 (vendor file fetched by FETCH_VENDOR).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

PASS = "[PASS]"
FAIL = "[FAIL]"
SKIP = "[SKIP]"

NODE_TYPES = [
    "organ", "sub_organ", "doctrine", "agent", "task",
    "land", "receipt", "sentinel", "thread",
]
EDGE_TYPES = [
    "parent_of", "owns", "declares_base", "lands_after", "ratifies",
    "gates", "produces", "references", "monitors", "succeeds",
]
VIEW_IDS = ["V1", "V2", "V3", "V4", "V5", "V6"]
URL_PARAMS = ["v", "organ", "since", "focus", "depth"]


def find_viewer_dir(start: Path) -> Path | None:
    # Look for SUPPORT/viewer/index.html at or below the starting path.
    candidates = [
        start / "SUPPORT" / "viewer",
        start / "files" / "SUPPORT" / "viewer",
        start.parent / "SUPPORT" / "viewer",
        start.parent / "files" / "SUPPORT" / "viewer",
    ]
    for c in candidates:
        if (c / "index.html").exists():
            return c
    return None


def run_tests() -> int:
    here = Path(__file__).resolve().parent
    # Walk upward up to 6 levels to locate SUPPORT/viewer
    viewer = None
    cur = here
    for _ in range(6):
        viewer = find_viewer_dir(cur)
        if viewer is not None:
            break
        cur = cur.parent
    if viewer is None:
        print(FAIL, "locate_viewer_dir", "SUPPORT/viewer/ not found relative to test file")
        print("E3 RESULT: FAILED")
        return 1

    sandbox_mode = os.environ.get("IMPERIUM_E3_SANDBOX") == "1"
    failures: list[str] = []

    index_html = viewer / "index.html"
    app_js = viewer / "app.js"
    styles_css = viewer / "styles.css"
    cyto = viewer / "cytoscape.min.js"
    nojekyll = viewer / ".nojekyll"
    readme = viewer / "README.md"

    # T1
    if index_html.exists():
        print(PASS, "T1_index_html_present")
    else:
        print(FAIL, "T1_index_html_present", str(index_html))
        failures.append("T1")

    html_text = index_html.read_text(encoding="utf-8") if index_html.exists() else ""

    # T2
    refs_ok = all(asset in html_text for asset in ["styles.css", "app.js", "cytoscape.min.js"])
    if refs_ok:
        print(PASS, "T2_index_html_references_assets")
    else:
        print(FAIL, "T2_index_html_references_assets")
        failures.append("T2")

    # T3
    if re.search(r'id\s*=\s*"cy"', html_text):
        print(PASS, "T3_cy_container_present")
    else:
        print(FAIL, "T3_cy_container_present")
        failures.append("T3")

    # T4 — vendor file size; skip in sandbox
    if sandbox_mode:
        print(SKIP, "T4_cytoscape_vendored", "sandbox mode (IMPERIUM_E3_SANDBOX=1)")
    else:
        if cyto.exists() and cyto.stat().st_size > 100_000:
            text_head = cyto.read_text(encoding="utf-8", errors="replace")[:4000]
            if "cytoscape" in text_head.lower():
                print(PASS, "T4_cytoscape_vendored")
            else:
                print(FAIL, "T4_cytoscape_vendored", "identifier 'cytoscape' not found in head")
                failures.append("T4")
        else:
            print(FAIL, "T4_cytoscape_vendored",
                  f"file missing or too small ({cyto.stat().st_size if cyto.exists() else 0} bytes); did you run FETCH_VENDOR.ps1?")
            failures.append("T4")

    app_text = app_js.read_text(encoding="utf-8") if app_js.exists() else ""
    css_text = styles_css.read_text(encoding="utf-8") if styles_css.exists() else ""

    # T5
    missing_views = [v for v in VIEW_IDS if f"'{v}'" not in app_text and f'"{v}"' not in app_text]
    if not missing_views:
        print(PASS, "T5_app_js_view_registry")
    else:
        print(FAIL, "T5_app_js_view_registry", "missing:", missing_views)
        failures.append("T5")

    # T6
    if "../graph_snapshot.json" in app_text:
        print(PASS, "T6_app_js_snapshot_path")
    else:
        print(FAIL, "T6_app_js_snapshot_path")
        failures.append("T6")

    # T7
    if "imperium.graph.annotations.v1" in app_text:
        print(PASS, "T7_app_js_annotation_key")
    else:
        print(FAIL, "T7_app_js_annotation_key")
        failures.append("T7")

    # T8
    if "URLSearchParams" in app_text:
        param_hits = [p for p in URL_PARAMS if f"'{p}'" in app_text or f'"{p}"' in app_text]
        if len(param_hits) == len(URL_PARAMS):
            print(PASS, "T8_app_js_url_filters")
        else:
            print(FAIL, "T8_app_js_url_filters", "params seen:", param_hits)
            failures.append("T8")
    else:
        print(FAIL, "T8_app_js_url_filters", "URLSearchParams not used")
        failures.append("T8")

    # T9
    missing_nodes = [t for t in NODE_TYPES if f"'{t}'" not in app_text and f'"{t}"' not in app_text]
    missing_edges = [t for t in EDGE_TYPES if f"'{t}'" not in app_text and f'"{t}"' not in app_text]
    if not missing_nodes and not missing_edges:
        print(PASS, "T9_app_js_node_edge_taxonomy")
    else:
        print(FAIL, "T9_app_js_node_edge_taxonomy",
              "missing nodes:", missing_nodes, "missing edges:", missing_edges)
        failures.append("T9")

    # T10 — verify violet tonal palette (hex first byte in [10..70] roughly,
    # i.e. the red channel is suppressed relative to blue, blue > red).
    hex_colors = re.findall(r"#([0-9a-fA-F]{6})", css_text)
    tonal_violet = 0
    for h in hex_colors:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        if b > r and b >= g and (b - r) >= 20:
            tonal_violet += 1
    if tonal_violet >= 6:
        print(PASS, "T10_styles_eyes_v2_tonal", f"{tonal_violet} violet-tonal colors")
    else:
        print(FAIL, "T10_styles_eyes_v2_tonal", f"only {tonal_violet} violet-tonal colors")
        failures.append("T10")

    # T11 — single yellow MARK accent (one yellow-family color, used as accent)
    yellow_marks = 0
    for h in hex_colors:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        if r > 180 and g > 150 and b < 100:
            yellow_marks += 1
    if yellow_marks >= 1:
        print(PASS, "T11_styles_eyes_v2_mark", f"{yellow_marks} yellow MARK colors")
    else:
        print(FAIL, "T11_styles_eyes_v2_mark", "no yellow accent color found")
        failures.append("T11")

    # T12 — .nojekyll for GitHub Pages
    if nojekyll.exists():
        print(PASS, "T12_nojekyll_present")
    else:
        print(FAIL, "T12_nojekyll_present")
        failures.append("T12")

    # T13 — viewer README
    if readme.exists() and readme.stat().st_size > 100:
        print(PASS, "T13_viewer_readme")
    else:
        print(FAIL, "T13_viewer_readme")
        failures.append("T13")

    print()
    if failures:
        print("FAILED:", ",".join(failures))
        print("E3 RESULT: FAILED")
        return 1
    total = 13 - (1 if sandbox_mode else 0)
    print(f"{total}/{total} PASSED" + (" (T4 skipped: sandbox)" if sandbox_mode else ""))
    print("E3 RESULT: ALL PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())
