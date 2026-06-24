#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# imperium eyes shoot -- playwright harness for the viewer.
#
# Drives a headless Chromium through Playwright over V0..V6 of the
# Imperium graph viewer and saves one PNG per view to --out-dir.
#
# By default spins up a temporary HTTP server (Python stdlib) bound to
# 127.0.0.1 on a free port, rooted at --repo-root. Pass --viewer-url to
# point at a remote viewer (GitHub Pages, etc.) instead.
#
# Exit codes:
#   0  all views shot
#   2  bad arguments
#   3  i/o or browser error

import argparse
import contextlib
import http.server
import pathlib
import socket
import socketserver
import sys
import threading
import time

VIEWS_DEFAULT = ['V0', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']


def find_free_port():
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def serve_dir(root, port):
    root_str = str(root)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=root_str, **kw)

        def log_message(self, *a, **kw):
            return

    httpd = socketserver.ThreadingTCPServer(('127.0.0.1', port), Handler)
    httpd.allow_reuse_address = True
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, t


def shoot(viewer_url, out_dir, views, width, height, wait_ms, settle_ms, scale):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('ERR: playwright not installed. Run INSTALL.ps1 first.', file=sys.stderr)
        return 3

    out_dir.mkdir(parents=True, exist_ok=True)
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                viewport={'width': width, 'height': height},
                device_scale_factor=scale,
            )
            page = context.new_page()
            page.set_default_timeout(wait_ms)

            for v in views:
                sep = '&' if '?' in viewer_url else '?'
                url = f'{viewer_url}{sep}v={v}'
                t0 = time.time()
                print(f'[shoot] {v}: GET {url}')
                try:
                    page.goto(url, wait_until='networkidle', timeout=wait_ms)
                except Exception as e:
                    print(f'[shoot] {v}: navigation timeout / error: {e}')

                # Wait for cytoscape to have nodes mounted; tolerate absence.
                try:
                    page.wait_for_function(
                        'window.cy && window.cy.elements && window.cy.elements().length > 0',
                        timeout=wait_ms,
                    )
                except Exception:
                    # Fallback: at least wait for the cy container to be in DOM.
                    try:
                        page.wait_for_selector('#cy', timeout=10000)
                    except Exception:
                        pass

                # Let cose / layout settle.
                page.wait_for_timeout(settle_ms)

                out_path = out_dir / f'{v}.png'
                page.screenshot(path=str(out_path), full_page=False)
                size = out_path.stat().st_size if out_path.is_file() else 0
                dt = time.time() - t0
                print(f'[shoot] {v}: OK {out_path} ({size} bytes, {dt:.1f}s)')
                results.append((v, str(out_path), size, dt))

            context.close()
        finally:
            browser.close()

    print()
    print('== shoot summary ==')
    for v, p_, size, dt in results:
        print(f'  {v}: {size:>9} bytes  {dt:5.1f}s  {p_}')
    print(f'  TOTAL: {len(results)} view(s)')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Playwright harness for the Imperium graph viewer.')
    parser.add_argument('--repo-root', default='.',
                        help='Repo root to serve via local http.server (default: .)')
    parser.add_argument('--viewer-url', default=None,
                        help='Override: full viewer URL (skips local http.server)')
    parser.add_argument('--out-dir', default=None,
                        help='Output directory (default: <repo>/SUPPORT/eyes-shoot/out)')
    parser.add_argument('--views', default=','.join(VIEWS_DEFAULT),
                        help='Comma-separated view ids (default: V0,V1,V2,V3,V4,V5,V6)')
    parser.add_argument('--width', type=int, default=1920)
    parser.add_argument('--height', type=int, default=1200)
    parser.add_argument('--scale', type=int, default=2,
                        help='device_scale_factor (default: 2 for retina-quality PNGs)')
    parser.add_argument('--wait-ms', type=int, default=60000,
                        help='Per-step timeout (default: 60000)')
    parser.add_argument('--settle-ms', type=int, default=3000,
                        help='Extra delay after layout to let cose settle (default: 3000)')
    parser.add_argument('--port', type=int, default=None,
                        help='Port for local http.server (default: random free)')
    args = parser.parse_args(argv)

    repo = pathlib.Path(args.repo_root).resolve()
    if not repo.is_dir():
        print(f'ERR: --repo-root not a directory: {repo}', file=sys.stderr)
        return 2

    out_dir = pathlib.Path(args.out_dir).resolve() if args.out_dir \
        else (repo / 'SUPPORT' / 'eyes-shoot' / 'out')

    views = [v.strip() for v in args.views.split(',') if v.strip()]
    if not views:
        print('ERR: --views resolved to empty list', file=sys.stderr)
        return 2

    server = None
    viewer_url = args.viewer_url
    if not viewer_url:
        viewer_check = repo / 'SUPPORT' / 'viewer' / 'index.html'
        if not viewer_check.is_file():
            print(f'ERR: viewer not found at {viewer_check}; pass --viewer-url to override.',
                  file=sys.stderr)
            return 2
        port = args.port or find_free_port()
        server, _ = serve_dir(repo, port)
        viewer_url = f'http://127.0.0.1:{port}/SUPPORT/viewer/'
        print(f'[serve] http://127.0.0.1:{port}/  (root={repo})')
        print(f'[serve] viewer: {viewer_url}')

    try:
        rc = shoot(viewer_url, out_dir, views,
                   args.width, args.height, args.wait_ms,
                   args.settle_ms, args.scale)
    finally:
        if server is not None:
            try:
                server.shutdown()
            except Exception:
                pass
    return rc


if __name__ == '__main__':
    sys.exit(main())
