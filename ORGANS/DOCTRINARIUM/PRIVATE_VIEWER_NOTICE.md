# PRIVATE_VIEWER_NOTICE

_doctrinal record :: VIEWER-REPO-REMOVAL-V0_3-0001 / K12_

## Decision

From **K12** onward, `SUPPORT/viewer/` is **forbidden in master**.
The viewer is owner-private cognitive instrumentation, not a public artifact.

- It surfaces doctrine bodies, owner-profile fragments, in-flight receipts, current-tip pointers, full doctrine prose via the LLM Exporter (V0.3+).
- Public GitHub Pages would expose those to anyone with the URL.
- The viewer lives locally on the owner's machine, distributed as `VIEWER-LOCAL-V0_3-PORTABLE.zip` (non-LAND, non-repo).

## What changed at K12

1. `SUPPORT/viewer/` removed from master in full.
2. `.gitignore` blocks `SUPPORT/viewer/` from ever re-entering tracking.
3. This notice landed in `ORGANS/DOCTRINARIUM/PRIVATE_VIEWER_NOTICE.md`.
4. Sentinel test `ORGANS/INQUISITION/TESTS/test_viewer_removed_e3.py` enforces the rule; any future LAND must pass it.
5. GitHub Pages disabled by owner manually (repo Settings -> Pages -> Source: None).

## What stays public in master

- `SUPPORT/graph_snapshot.json` (the graph itself is canon and indexed by the kernel).
- `SUPPORT/eyes-shoot/` (Playwright harness; renders a local viewer to PNG; introduced in K11).
- All `ORGANS/` doctrine and tooling.

## What is forbidden in master

- `SUPPORT/viewer/` (the HTML/JS/CSS/vendor of the actual rendering UI).
- Any equivalent renderer that exposes the LLM Exporter UI publicly.
- Re-enabling GitHub Pages on this repo without a follow-up doctrine update.

## Allowed exception path

If at some future point the owner explicitly decides to publish a sanitized, public-safe viewer:

1. A new doctrine update must supersede this notice.
2. The new viewer must exclude: owner profile, in-flight receipts, doctrine prose, LLM Exporter UI.
3. A new LAND-pack must land the public viewer alongside an updated notice referencing the supersession.

Until then: viewer = local only.

## Pointers

- Local distribution artifact: `VIEWER-LOCAL-V0_3-PORTABLE.zip` (shipped separately by the agent).
- Local default install path (owner's convention): `E:\IMPERIUM_HARNESS\viewer\`.
- Playwright driver (still in master): `SUPPORT/eyes-shoot/shoot.py` accepts `--viewer-url file:///...\index.html` or `--repo-root` overrides.
- Sentinel: `ORGANS/INQUISITION/TESTS/test_viewer_removed_e3.py` (run periodically by INQUISITION).

_~ DOCTRINARIUM, K12_
