#!/usr/bin/env python3
# Trinity Hygiene Scanner v0_1 (Administratum organ).
# Canon: Constitution 9 -> cleanup = classification + staging, NEVER delete.
# Unknown zones BLOCK automation. Moves require owner approval + restore manifest.
import os, sys, json, argparse, fnmatch, shutil, datetime

DEFAULT_POLICY = {
  "protected_prefixes": [".git", ".github", "ORGANS/_CORE_GOVERNANCE", "_CORE_GOVERNANCE"],
  "known_top": ["ORGANS","_CORE_GOVERNANCE","README.md","AGENTS.md","LICENSE",
                ".git",".github",".gitignore",".gitattributes","_LOCAL_HANDOFF"],
  "safe_clutter_globs": ["__pycache__","*.pyc","*.pyo","*.tmp","*.temp","*~",
                         "*.bak","*.orig","*.swp",".DS_Store","Thumbs.db",
                         "desktop.ini",".pytest_cache",".mypy_cache"]
}

def load_policy(repo):
    p = os.path.join(repo, "ORGANS/CUSTODES/POLICY/hygiene_denylist_allowlist_v0_1.json")
    if os.path.isfile(p):
        try:
            j = json.load(open(p, encoding="utf-8"))
            for k in DEFAULT_POLICY:
                j.setdefault(k, DEFAULT_POLICY[k])
            return j
        except Exception:
            pass
    return dict(DEFAULT_POLICY)

def is_protected(rel, policy):
    rp = rel.replace(chr(92), "/")
    for pre in policy["protected_prefixes"]:
        if rp == pre or rp.startswith(pre + "/"):
            return True
    return False

def is_clutter(name, policy):
    for g in policy["safe_clutter_globs"]:
        if fnmatch.fnmatch(name, g):
            return True
    return False

def classify(repo, policy):
    items = []
    known_top = set(policy["known_top"])
    for base, dirs, files in os.walk(repo):
        rel_base = os.path.relpath(base, repo).replace(chr(92), "/")
        if rel_base == ".":
            rel_base = ""
        for d in list(dirs):
            rel = (rel_base + "/" + d).strip("/")
            top = rel.split("/")[0]
            if is_clutter(d, policy):
                prot = is_protected(rel, policy)
                items.append({"path": rel, "type": "dir", "category": "clutter",
                              "rule": "safe_clutter_glob",
                              "proposed_action": "owner_review" if prot else "stage_quarantine",
                              "zone": "protected" if prot else "tree"})
                dirs.remove(d)
            elif rel_base == "" and top not in known_top:
                items.append({"path": rel, "type": "dir", "category": "unknown",
                              "rule": "not_in_known_top", "proposed_action": "owner_review",
                              "zone": "unknown"})
                dirs.remove(d)
        for f in files:
            rel = (rel_base + "/" + f).strip("/")
            top = rel.split("/")[0]
            if is_clutter(f, policy):
                prot = is_protected(rel, policy)
                items.append({"path": rel, "type": "file", "category": "clutter",
                              "rule": "safe_clutter_glob",
                              "proposed_action": "owner_review" if prot else "stage_quarantine",
                              "zone": "protected" if prot else "tree"})
            elif rel_base == "" and top not in known_top:
                items.append({"path": rel, "type": "file", "category": "unknown",
                              "rule": "not_in_known_top", "proposed_action": "owner_review",
                              "zone": "unknown"})
    return items

def build_ledger(repo, policy, mode):
    items = classify(repo, policy)
    counts = {}
    for it in items:
        counts[it["category"]] = counts.get(it["category"], 0) + 1
    blocked = counts.get("unknown", 0)
    return {"ledger_schema": "imperium.quarantine_ledger.v0_1", "repo": repo,
            "generated": datetime.datetime.utcnow().isoformat() + "Z", "mode": mode,
            "counts": counts, "blocked_unknown": blocked,
            "auto_quarantine_allowed": (blocked == 0), "items": items}

def do_quarantine(repo, ledger, qroot, owner_approve):
    if not owner_approve:
        print("REFUSED: quarantine requires --owner-approve (Constitution 9 / Passport 1)")
        return 2
    if ledger["blocked_unknown"] > 0:
        print("REFUSED: %d unknown-zone item(s) block automation; owner must classify first" % ledger["blocked_unknown"])
        return 2
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(qroot, stamp)
    restore = []
    for it in ledger["items"]:
        if it["proposed_action"] != "stage_quarantine":
            continue
        src = os.path.join(repo, it["path"])
        if not os.path.exists(src):
            continue
        d = os.path.join(dest, it["path"])
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.move(src, d)
        restore.append({"from": it["path"], "to": d})
    os.makedirs(dest, exist_ok=True)
    json.dump({"quarantine_root": dest, "restore": restore,
               "note": "MOVE only. Restore by copying 'to' back to 'from'."},
              open(os.path.join(dest, "RESTORE_MANIFEST.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    ledger["mode"] = "quarantine"
    ledger["quarantined"] = len(restore)
    ledger["quarantine_dest"] = dest
    print("quarantined %d item(s) -> %s" % (len(restore), dest))
    return 0

def main():
    ap = argparse.ArgumentParser(description="Trinity Hygiene Scanner v0_1 (classify; never delete)")
    ap.add_argument("repo")
    ap.add_argument("--out", default=None)
    ap.add_argument("--apply-quarantine", action="store_true")
    ap.add_argument("--owner-approve", action="store_true")
    ap.add_argument("--quarantine-root", default=None)
    a = ap.parse_args()
    policy = load_policy(a.repo)
    ledger = build_ledger(a.repo, policy, "dry-run")
    code = 0
    if a.apply_quarantine:
        qroot = a.quarantine_root or os.path.join(a.repo, "..", "_LOCAL_HANDOFF", "QUARANTINE")
        code = do_quarantine(a.repo, ledger, qroot, a.owner_approve)
    if a.out:
        d = os.path.dirname(a.out)
        if d:
            os.makedirs(d, exist_ok=True)
        json.dump(ledger, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"mode": ledger["mode"], "counts": ledger["counts"],
                      "blocked_unknown": ledger["blocked_unknown"],
                      "auto_quarantine_allowed": ledger["auto_quarantine_allowed"]},
                     ensure_ascii=False))
    sys.exit(code)

if __name__ == "__main__":
    main()
