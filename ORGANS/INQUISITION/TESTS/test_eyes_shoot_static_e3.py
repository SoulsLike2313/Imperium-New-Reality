#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# E3 static-shape tests for EYES-PLAYWRIGHT-HARNESS-0001.
# Validates the pack's eyes-shoot tree WITHOUT launching Chromium.
# Exit 0 if all 14 tests pass, 1 otherwise.

import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent


def _find_root():
    cur = HERE
    for _ in range(8):
        # pack mode
        if (cur / 'files' / 'SUPPORT' / 'eyes-shoot' / 'shoot.py').is_file():
            return cur, True
        # repo mode
        if (cur / 'SUPPORT' / 'eyes-shoot' / 'shoot.py').is_file():
            return cur, False
        if cur.parent == cur:
            break
        cur = cur.parent
    raise SystemExit('FATAL: could not locate SUPPORT/eyes-shoot/shoot.py')


ROOT, IS_PACK = _find_root()
PREFIX = (ROOT / 'files') if IS_PACK else ROOT
EYES = PREFIX / 'SUPPORT' / 'eyes-shoot'
SHOOT = EYES / 'shoot.py'
INSTALL = EYES / 'INSTALL.ps1'
SHOOT_PS = EYES / 'SHOOT.ps1'
README = EYES / 'README.md'
GITIGNORE = EYES / '.gitignore'

RESULTS = []


def _t(name, ok, detail=''):
    RESULTS.append((name, ok, detail))
    flag = 'PASS' if ok else 'FAIL'
    print(f'[{flag}] {name}{(" :: " + detail) if detail else ""}')


def test_shoot_exists():
    _t('T01 shoot.py exists', SHOOT.is_file(), str(SHOOT))


def test_install_exists():
    _t('T02 INSTALL.ps1 exists', INSTALL.is_file(), str(INSTALL))


def test_shoot_ps_exists():
    _t('T03 SHOOT.ps1 exists', SHOOT_PS.is_file(), str(SHOOT_PS))


def test_readme_exists():
    _t('T04 README.md exists', README.is_file(), str(README))


def test_gitignore_exists():
    _t('T05 .gitignore exists', GITIGNORE.is_file(), str(GITIGNORE))


def test_shoot_compiles():
    r = subprocess.run(['python3', '-m', 'py_compile', str(SHOOT)],
                       capture_output=True, text=True)
    _t('T06 shoot.py compiles', r.returncode == 0, r.stderr.strip())


def test_shoot_has_cli():
    body = SHOOT.read_text(encoding='utf-8')
    needed = ['--repo-root', '--viewer-url', '--out-dir', '--views',
              '--width', '--height', '--scale', '--wait-ms',
              '--settle-ms', '--port']
    missing = [n for n in needed if n not in body]
    _t('T07 shoot.py exposes required CLI flags',
       not missing, f'missing={missing}')


def test_default_views():
    body = SHOOT.read_text(encoding='utf-8')
    _t('T08 default views = V0..V6',
       "['V0', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']" in body)


def test_install_pip_playwright():
    body = INSTALL.read_text(encoding='utf-8')
    _t('T09 INSTALL.ps1 pip install playwright',
       'pip install' in body and 'playwright' in body)


def test_install_chromium():
    body = INSTALL.read_text(encoding='utf-8')
    _t('T10 INSTALL.ps1 playwright install chromium',
       'playwright install chromium' in body)


def test_shoot_ps_invokes_shoot():
    body = SHOOT_PS.read_text(encoding='utf-8')
    _t('T11 SHOOT.ps1 invokes shoot.py',
       'shoot.py' in body and '--repo-root' in body and '--out-dir' in body)


def test_gitignore_excludes_out():
    body = GITIGNORE.read_text(encoding='utf-8')
    _t('T12 .gitignore excludes out/ and *.png',
       'out/' in body and '*.png' in body)


def test_invalid_args_exits_2():
    r = subprocess.run(['python3', str(SHOOT), '--repo-root', '/no/such/dir/xyzzy42'],
                       capture_output=True, text=True, timeout=30)
    _t('T13 invalid --repo-root exits 2', r.returncode == 2, f'rc={r.returncode}')


def test_local_server_module_used():
    # Code must use http.server / socketserver for local hosting,
    # AND find_free_port helper for portless mode.
    body = SHOOT.read_text(encoding='utf-8')
    _t('T14 shoot.py uses http.server + find_free_port',
       'http.server' in body and 'find_free_port' in body and 'SimpleHTTPRequestHandler' in body)


def main():
    print(f'== E3 :: EYES-PLAYWRIGHT-HARNESS-0001 (root={ROOT}, pack_mode={IS_PACK}) ==')
    print(f'  shoot.py:   {SHOOT}')
    print(f'  INSTALL.ps1: {INSTALL}')
    print(f'  SHOOT.ps1:   {SHOOT_PS}')
    print()
    tests = [
        test_shoot_exists, test_install_exists, test_shoot_ps_exists,
        test_readme_exists, test_gitignore_exists, test_shoot_compiles,
        test_shoot_has_cli, test_default_views, test_install_pip_playwright,
        test_install_chromium, test_shoot_ps_invokes_shoot,
        test_gitignore_excludes_out, test_invalid_args_exits_2,
        test_local_server_module_used,
    ]
    for t in tests:
        try:
            t()
        except Exception as e:
            _t(t.__name__, False, f'EXCEPTION: {e}')
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print()
    print(f'== {passed}/{total} passed ==')
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
