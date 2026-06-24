#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Sentinel: SUPPORT/viewer/ must NOT exist in the repo.
# Lives post-LAND of VIEWER-REPO-REMOVAL-V0_3-0001 (K12+).
# Runs against the repo working tree, NOT against a pack.
#
# Re-introducing SUPPORT/viewer/ into master is forbidden by
# ORGANS/DOCTRINARIUM/PRIVATE_VIEWER_NOTICE.md.
#
# Exit 0 on PASS, 1 on FAIL.

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def _find_repo_root():
    cur = HERE
    for _ in range(8):
        if (cur / '.git').is_dir() or (cur / 'ORGANS').is_dir() and (cur / 'SUPPORT').is_dir():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return HERE.parent.parent.parent  # ORGANS/INQUISITION/TESTS/.. = repo root


REPO = _find_repo_root()
RESULTS = []


def _t(name, ok, detail=''):
    RESULTS.append((name, ok, detail))
    flag = 'PASS' if ok else 'FAIL'
    print(f'[{flag}] {name}{(" :: " + detail) if detail else ""}')


def test_viewer_dir_absent():
    p = REPO / 'SUPPORT' / 'viewer'
    _t('T01 SUPPORT/viewer/ does not exist in repo',
       not p.exists(),
       f'unexpected path: {p}' if p.exists() else str(p))


def test_no_index_html():
    p = REPO / 'SUPPORT' / 'viewer' / 'index.html'
    _t('T02 SUPPORT/viewer/index.html absent', not p.exists())


def test_no_app_js():
    p = REPO / 'SUPPORT' / 'viewer' / 'app.js'
    _t('T03 SUPPORT/viewer/app.js absent', not p.exists())


def test_no_styles_css():
    p = REPO / 'SUPPORT' / 'viewer' / 'styles.css'
    _t('T04 SUPPORT/viewer/styles.css absent', not p.exists())


def test_no_vendor():
    p = REPO / 'SUPPORT' / 'viewer' / 'vendor'
    _t('T05 SUPPORT/viewer/vendor/ absent', not p.exists())


def test_gitignore_blocks_viewer():
    gi = REPO / '.gitignore'
    if not gi.is_file():
        _t('T06 .gitignore blocks SUPPORT/viewer/', False, f'no .gitignore at {gi}')
        return
    body = gi.read_text(encoding='utf-8', errors='replace')
    _t('T06 .gitignore blocks SUPPORT/viewer/',
       'SUPPORT/viewer/' in body or 'SUPPORT/viewer' in body)


def test_notice_present():
    p = REPO / 'ORGANS' / 'DOCTRINARIUM' / 'PRIVATE_VIEWER_NOTICE.md'
    _t('T07 DOCTRINARIUM/PRIVATE_VIEWER_NOTICE.md present', p.is_file(), str(p))


def test_eyes_shoot_still_present():
    # eyes-shoot must NOT be collateral damage; it's the local-viewer driver.
    p = REPO / 'SUPPORT' / 'eyes-shoot' / 'shoot.py'
    _t('T08 SUPPORT/eyes-shoot/shoot.py preserved', p.is_file(), str(p))


def test_graph_snapshot_still_present():
    p = REPO / 'SUPPORT' / 'graph_snapshot.json'
    _t('T09 SUPPORT/graph_snapshot.json preserved', p.is_file(), str(p))


def test_doctrine_eyes_still_present():
    p = REPO / 'ORGANS' / 'DOCTRINARIUM' / 'EYES_V2.md'
    _t('T10 DOCTRINARIUM/EYES_V2.md preserved', p.is_file(), str(p))


def main():
    print(f'== sentinel :: viewer removed (repo={REPO}) ==')
    tests = [
        test_viewer_dir_absent, test_no_index_html, test_no_app_js,
        test_no_styles_css, test_no_vendor, test_gitignore_blocks_viewer,
        test_notice_present, test_eyes_shoot_still_present,
        test_graph_snapshot_still_present, test_doctrine_eyes_still_present,
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
