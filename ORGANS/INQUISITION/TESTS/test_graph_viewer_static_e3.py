#!/usr/bin/env python3
"""E3 static-shape self-test for SUPPORT/viewer/ (Imperium Graph Viewer v0_2).

Validates structural sanity. No JS executed — asserts that the right tokens
and references are present in the right files.

20 tests (T1-T13 inherited from v0_1, T14-T20 new for v0_2):
  T1  index_html_present
  T2  index_html_references_assets       (styles.css + app.js + cytoscape.min.js)
  T3  cy_container_present                (<div id="cy">)
  T4  cytoscape_vendored                  (>100KB + 'cytoscape')   (skippable)
  T5  app_js_view_registry                (V0..V6 all present — 7 views)
  T6  app_js_snapshot_path                (../graph_snapshot.json)
  T7  app_js_annotation_key               (imperium.graph.annotations.v1)
  T8  app_js_url_filters                  (URLSearchParams + v/organ/since/focus/depth)
  T9  app_js_node_edge_taxonomy           (9 nodes + 10 edges)
  T10 styles_eyes_v2_tonal                (violet-tonal hex colors)
  T11 styles_eyes_v2_mark                 (yellow MARK accent)
  T12 nojekyll_present
  T13 viewer_readme
  T14 v0_outline_view                     (V0 Outline overlay + buildOutlineMarkdown)
  T15 minimap_container                   (#minimap + #minimap-cy + #minimap-viewport)
  T16 hover_tooltip                       (#hover-tooltip element + showTooltip in app.js)
  T17 history_back_and_pin                (history stack + togglePin + clearPins)
  T18 llm_context_export                  (buildLlmContext + scope/depth/format)
  T19 annotated_marker                    ('has-annotation' class + ring style)
  T20 keyboard_shortcuts                  (onKeydown handler + key bindings)

Sandbox mode: set IMPERIUM_E3_SANDBOX=1 to skip T4 (vendor fetched at install).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

PASS = "[PASS]"
FAIL = "[FAIL]"
SKIP = "[SKIP]"

NODE_TYPES = ["organ", "sub_organ", "doctrine", "agent", "task",
              "land", "receipt", "sentinel", "thread"]
EDGE_TYPES = ["parent_of", "owns", "declares_base", "lands_after", "ratifies",
              "gates", "produces", "references", "monitors", "succeeds"]
VIEW_IDS = ["V0", "V1", "V2", "V3", "V4", "V5", "V6"]
URL_PARAMS = ["v", "organ", "since", "focus", "depth"]


def find_viewer_dir(start: Path) -> Path | None:
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
    viewer = None
    cur = here
    for _ in range(6):
        viewer = find_viewer_dir(cur)
        if viewer is not None:
            break
        cur = cur.parent
    if viewer is None:
        print(FAIL, "locate_viewer_dir", "SUPPORT/viewer/ not found")
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

    html_text = index_html.read_text(encoding="utf-8") if index_html.exists() else ""
    app_text = app_js.read_text(encoding="utf-8") if app_js.exists() else ""
    css_text = styles_css.read_text(encoding="utf-8") if styles_css.exists() else ""

    # T1
    if index_html.exists():
        print(PASS, "T1_index_html_present")
    else:
        print(FAIL, "T1_index_html_present", str(index_html)); failures.append("T1")

    # T2
    if all(asset in html_text for asset in ["styles.css", "app.js", "cytoscape.min.js"]):
        print(PASS, "T2_index_html_references_assets")
    else:
        print(FAIL, "T2_index_html_references_assets"); failures.append("T2")

    # T3
    if re.search(r'id\s*=\s*"cy"', html_text):
        print(PASS, "T3_cy_container_present")
    else:
        print(FAIL, "T3_cy_container_present"); failures.append("T3")

    # T4
    if sandbox_mode:
        print(SKIP, "T4_cytoscape_vendored", "sandbox mode (IMPERIUM_E3_SANDBOX=1)")
    else:
        if cyto.exists() and cyto.stat().st_size > 100_000:
            head = cyto.read_text(encoding="utf-8", errors="replace")[:4000]
            if "cytoscape" in head.lower():
                print(PASS, "T4_cytoscape_vendored")
            else:
                print(FAIL, "T4_cytoscape_vendored", "'cytoscape' missing in head"); failures.append("T4")
        else:
            size = cyto.stat().st_size if cyto.exists() else 0
            print(FAIL, "T4_cytoscape_vendored", f"file missing or too small ({size} bytes); run FETCH_VENDOR.ps1")
            failures.append("T4")

    # T5 — V0..V6
    missing_views = [v for v in VIEW_IDS if f"'{v}'" not in app_text and f'"{v}"' not in app_text]
    if not missing_views:
        print(PASS, "T5_app_js_view_registry")
    else:
        print(FAIL, "T5_app_js_view_registry", "missing:", missing_views); failures.append("T5")

    # T6
    if "../graph_snapshot.json" in app_text:
        print(PASS, "T6_app_js_snapshot_path")
    else:
        print(FAIL, "T6_app_js_snapshot_path"); failures.append("T6")

    # T7
    if "imperium.graph.annotations.v1" in app_text:
        print(PASS, "T7_app_js_annotation_key")
    else:
        print(FAIL, "T7_app_js_annotation_key"); failures.append("T7")

    # T8
    if "URLSearchParams" in app_text:
        param_hits = [p for p in URL_PARAMS if f"'{p}'" in app_text or f'"{p}"' in app_text]
        if len(param_hits) == len(URL_PARAMS):
            print(PASS, "T8_app_js_url_filters")
        else:
            print(FAIL, "T8_app_js_url_filters", "params:", param_hits); failures.append("T8")
    else:
        print(FAIL, "T8_app_js_url_filters", "URLSearchParams not used"); failures.append("T8")

    # T9
    miss_n = [t for t in NODE_TYPES if f"'{t}'" not in app_text and f'"{t}"' not in app_text]
    miss_e = [t for t in EDGE_TYPES if f"'{t}'" not in app_text and f'"{t}"' not in app_text]
    if not miss_n and not miss_e:
        print(PASS, "T9_app_js_node_edge_taxonomy")
    else:
        print(FAIL, "T9_app_js_node_edge_taxonomy", "nodes:", miss_n, "edges:", miss_e)
        failures.append("T9")

    # T10
    hex_colors = re.findall(r"#([0-9a-fA-F]{6})", css_text)
    tonal_violet = 0
    for h in hex_colors:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        if b > r and b >= g and (b - r) >= 20:
            tonal_violet += 1
    if tonal_violet >= 6:
        print(PASS, "T10_styles_eyes_v2_tonal", f"{tonal_violet} violet-tonal colors")
    else:
        print(FAIL, "T10_styles_eyes_v2_tonal", f"only {tonal_violet}"); failures.append("T10")

    # T11
    yellow_marks = 0
    for h in hex_colors:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        if r > 180 and g > 150 and b < 100:
            yellow_marks += 1
    if yellow_marks >= 1:
        print(PASS, "T11_styles_eyes_v2_mark", f"{yellow_marks} yellow MARK")
    else:
        print(FAIL, "T11_styles_eyes_v2_mark"); failures.append("T11")

    # T12
    if nojekyll.exists():
        print(PASS, "T12_nojekyll_present")
    else:
        print(FAIL, "T12_nojekyll_present"); failures.append("T12")

    # T13
    if readme.exists() and readme.stat().st_size > 100:
        print(PASS, "T13_viewer_readme")
    else:
        print(FAIL, "T13_viewer_readme"); failures.append("T13")

    # T14 — V0 Outline view
    has_outline_overlay = 'id="outline-overlay"' in html_text
    has_outline_fn = "buildOutlineMarkdown" in app_text
    has_v0_btn = 'data-view="V0"' in html_text
    if has_outline_overlay and has_outline_fn and has_v0_btn:
        print(PASS, "T14_v0_outline_view")
    else:
        print(FAIL, "T14_v0_outline_view",
              "overlay", has_outline_overlay, "fn", has_outline_fn, "btn", has_v0_btn)
        failures.append("T14")

    # T15 — minimap
    has_mini_html = all(s in html_text for s in ['id="minimap"', 'id="minimap-cy"', 'id="minimap-viewport"'])
    has_mini_js = "refreshMinimap" in app_text and "updateMinimapViewport" in app_text
    if has_mini_html and has_mini_js:
        print(PASS, "T15_minimap_container")
    else:
        print(FAIL, "T15_minimap_container", "html", has_mini_html, "js", has_mini_js)
        failures.append("T15")

    # T16 — hover tooltip
    has_tt_html = 'id="hover-tooltip"' in html_text
    has_tt_js = "showTooltip" in app_text and "moveTooltip" in app_text
    if has_tt_html and has_tt_js:
        print(PASS, "T16_hover_tooltip")
    else:
        print(FAIL, "T16_hover_tooltip", "html", has_tt_html, "js", has_tt_js)
        failures.append("T16")

    # T17 — history back + pin
    has_history = "state.history" in app_text and "goBack" in app_text
    has_pin = "togglePin" in app_text and "state.pins" in app_text
    if has_history and has_pin:
        print(PASS, "T17_history_back_and_pin")
    else:
        print(FAIL, "T17_history_back_and_pin", "history", has_history, "pin", has_pin)
        failures.append("T17")

    # T18 — LLM context export
    has_build = "buildLlmContext" in app_text
    has_scopes = all(s in app_text for s in ["'selection'", "'view'", "'organ'", "'all'"])
    has_formats = all(f in app_text for f in ["'markdown'", "'json'", "'prompt'"])
    has_overlay = 'id="llm-overlay"' in html_text
    if has_build and has_scopes and has_formats and has_overlay:
        print(PASS, "T18_llm_context_export")
    else:
        print(FAIL, "T18_llm_context_export",
              "build", has_build, "scopes", has_scopes, "formats", has_formats, "overlay", has_overlay)
        failures.append("T18")

    # T19 — annotated marker
    has_anno_cls = "has-annotation" in app_text and "has-annotation" in css_text
    if has_anno_cls:
        print(PASS, "T19_annotated_marker")
    else:
        print(FAIL, "T19_annotated_marker"); failures.append("T19")

    # T20 — keyboard shortcuts
    has_handler = "onKeydown" in app_text and "document.addEventListener('keydown'" in app_text
    has_keys = all(k in app_text for k in ["'?'", "'/'", "'Escape'", "'b'", "'p'", "'c'", "'f'"])
    if has_handler and has_keys:
        print(PASS, "T20_keyboard_shortcuts")
    else:
        print(FAIL, "T20_keyboard_shortcuts", "handler", has_handler, "keys", has_keys)
        failures.append("T20")

    print()
    if failures:
        print("FAILED:", ",".join(failures))
        print("E3 RESULT: FAILED")
        return 1
    total = 20 - (1 if sandbox_mode else 0)
    print(f"{total}/{total} PASSED" + (" (T4 skipped: sandbox)" if sandbox_mode else ""))
    print("E3 RESULT: ALL PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())
