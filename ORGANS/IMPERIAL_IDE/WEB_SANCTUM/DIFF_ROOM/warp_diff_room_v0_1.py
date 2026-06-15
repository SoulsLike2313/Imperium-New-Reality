#!/usr/bin/env python3
# WARP Diff Room generator v0_1 (IMPERIAL_IDE / WEB_SANCTUM).
# Observational, READ-ONLY aquarium room. Builds a self-contained HTML that shows:
#   - PREVIOUS and LATEST commit cards (sha/subject/author/date/footprint)
#   - Functional dossier (Appeared / Removed / Modified function-level symbols)
#   - Per-file textual diff (colored, sidebar-filterable)
# Runs only read-only git (rev-parse / log / show / diff). NEVER mutates the repo.
# Subprocess uses BYTES + manual utf-8 decode with errors='replace' so this is
# locale-independent (works on Windows cp1251 consoles).
import os, sys, subprocess, argparse, html, re, json

def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

STAT_LABEL = {"A": "added", "M": "modified", "D": "deleted", "R": "renamed", "C": "copied", "T": "typechange"}

FN_PATTERNS = [
    ("py.def",    re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(")),
    ("cls",       re.compile(r"^\s*class\s+(\w+)\b")),
    ("js.fn",     re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(")),
    ("js.arrow",  re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>")),
    ("ps.fn",     re.compile(r"^\s*function\s+([A-Za-z][\w-]+)\s*[\({]")),
    ("go.fn",     re.compile(r"^\s*func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(")),
]

def find_fn(line):
    out = []
    for kind, pat in FN_PATTERNS:
        m = pat.match(line)
        if m:
            out.append((kind, m.group(1)))
    return out

def color_diff(text):
    out = []
    for ln in text.splitlines():
        e = html.escape(ln)
        if ln.startswith("+++") or ln.startswith("---"):
            out.append('<span class="d-meta">' + e + '</span>')
        elif ln.startswith("@@"):
            out.append('<span class="d-hunk">' + e + '</span>')
        elif ln.startswith("diff --git") or ln.startswith("index ") or ln.startswith("new file") or ln.startswith("deleted file") or ln.startswith("rename ") or ln.startswith("similarity ") or ln.startswith("old mode") or ln.startswith("new mode"):
            out.append('<span class="d-file">' + e + '</span>')
        elif ln.startswith("+"):
            out.append('<span class="d-add">' + e + '</span>')
        elif ln.startswith("-"):
            out.append('<span class="d-del">' + e + '</span>')
        else:
            out.append('<span class="d-ctx">' + (e if e else "&nbsp;") + '</span>')
    return "\n".join(out)

def commit_info(repo, ref):
    sha7 = git(repo, "rev-parse", "--short", ref).strip()
    sha = git(repo, "rev-parse", ref).strip()
    subj = git(repo, "log", "-1", ref, "--pretty=%s").strip()
    body = git(repo, "log", "-1", ref, "--pretty=%b").strip()
    author = git(repo, "log", "-1", ref, "--pretty=%an").strip()
    when = git(repo, "log", "-1", ref, "--pretty=%cI").strip()
    files = [l for l in git(repo, "show", "--pretty=", "--name-only", ref).splitlines() if l.strip()]
    shortstat = git(repo, "show", "--shortstat", "--pretty=", ref).strip()
    return {"sha7": sha7, "sha": sha, "subj": subj, "body": body, "author": author,
            "when": when, "files": files, "shortstat": shortstat}

def render_commit_card(ci, role_label, role_class):
    body_html = ""
    if ci["body"]:
        body_html = '<p class="cc-body">' + html.escape(ci["body"][:280]) + ('\u2026' if len(ci["body"]) > 280 else '') + '</p>'
    stat = html.escape(ci["shortstat"]) if ci["shortstat"] else ("%d file%s" % (len(ci["files"]), "" if len(ci["files"])==1 else "s"))
    return (
        '<article class="commit-card relic-frame ' + role_class + '">'
        + '<header><span class="cc-role">' + html.escape(role_label) + '</span><span class="cc-sha">' + html.escape(ci["sha7"]) + '</span></header>'
        + '<h3 class="cc-subj">' + html.escape(ci["subj"]) + '</h3>'
        + body_html
        + '<dl class="cc-meta"><div><dt>author</dt><dd>' + html.escape(ci["author"]) + '</dd></div>'
        + '<div><dt>when</dt><dd>' + html.escape(ci["when"]) + '</dd></div>'
        + '<div><dt>footprint</dt><dd>' + stat + '</dd></div></dl>'
        + '</article>'
    )

def main():
    ap = argparse.ArgumentParser(description="WARP Diff Room generator (read-only, observational)")
    ap.add_argument("repo")
    ap.add_argument("--rev", default="HEAD~1..HEAD")
    ap.add_argument("--out", default=None)
    ap.add_argument("--title", default="WARP \u00b7 Diff Room")
    ap.add_argument("--shell-css", default=None)
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)

    if ".." in a.rev:
        base_ref, head_ref = a.rev.split("..", 1)
        head_ref = head_ref or "HEAD"
    else:
        base_ref, head_ref = "HEAD~1", "HEAD"
    base_ci = commit_info(repo, base_ref)
    head_ci = commit_info(repo, head_ref)
    branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()

    stat = git(repo, "diff", "--shortstat", a.rev).strip()
    namestat = git(repo, "diff", "--name-status", a.rev).strip()
    fulldiff = git(repo, "diff", "--no-color", a.rev)

    files = []
    for line in namestat.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            files.append((parts[0], parts[-1]))

    # Split full diff into per-file blocks AND collect function-level changes
    blocks = {}
    fn_added = {}    # path -> set of (kind, name)
    fn_removed = {}
    cur_path = None
    buf = []
    for ln in fulldiff.splitlines():
        if ln.startswith("diff --git"):
            if cur_path is not None:
                blocks[cur_path] = "\n".join(buf)
            cur_path = ln.split(" b/")[-1] if " b/" in ln else ln
            fn_added.setdefault(cur_path, set())
            fn_removed.setdefault(cur_path, set())
            buf = [ln]
        else:
            buf.append(ln)
            if cur_path is None: continue
            if ln.startswith("+++") or ln.startswith("---"): continue
            if ln.startswith("+"):
                for kn in find_fn(ln[1:]):
                    fn_added[cur_path].add(kn)
            elif ln.startswith("-"):
                for kn in find_fn(ln[1:]):
                    fn_removed[cur_path].add(kn)
    if cur_path is not None:
        blocks[cur_path] = "\n".join(buf)

    css = ""
    css_path = a.shell_css or os.path.join(repo, "ORGANS/IMPERIAL_IDE/WEB_SANCTUM/DIFF_ROOM/diff_room_shell.css")
    if os.path.isfile(css_path):
        with open(css_path, "rb") as f:
            css = f.read().decode("utf-8", errors="replace")

    def num(pat):
        m = re.search(pat, stat)
        return m.group(1) if m else "0"
    files_changed = num(r"(\d+) files? changed") if stat else str(len(files))
    ins = num(r"(\d+) insertion")
    dele = num(r"(\d+) deletion")

    # Compute Appeared / Removed / Modified across files
    appeared = []   # list of (path, kind, name)
    removed  = []
    modified = []
    for path in sorted(set(list(fn_added.keys()) + list(fn_removed.keys()))):
        added_set = fn_added.get(path, set())
        removed_set = fn_removed.get(path, set())
        both = added_set & removed_set
        for k, n in sorted(added_set - removed_set):
            appeared.append((path, k, n))
        for k, n in sorted(removed_set - added_set):
            removed.append((path, k, n))
        for k, n in sorted(both):
            modified.append((path, k, n))

    def render_fn_group(label, items, css_cls):
        if not items:
            return '<div class="fn-group ' + css_cls + ' empty"><h4>' + label + ' <em>(0)</em></h4><p class="fn-empty">\u2014</p></div>'
        by_file = {}
        for p, k, n in items:
            by_file.setdefault(p, []).append((k, n))
        rows = []
        for p in sorted(by_file.keys()):
            pills = "".join('<span class="fn-pill"><span class="fn-kind">' + html.escape(k) + '</span>' + html.escape(n) + '</span>' for k, n in by_file[p])
            rows.append('<li><span class="fn-file">' + html.escape(p) + '</span><div class="fn-pills">' + pills + '</div></li>')
        return '<div class="fn-group ' + css_cls + '"><h4>' + label + ' <em>(' + str(len(items)) + ')</em></h4><ul>' + "".join(rows) + '</ul></div>'

    # Sidebar + per-file panels
    side = []
    panels = []
    for i, (st, path) in enumerate(files):
        sid = "f%d" % i
        code = st[0]
        lab = STAT_LABEL.get(code, st)
        side.append('<button class="dr-file" data-target="%s"><span class="dr-st s-%s">%s</span>%s</button>'
                    % (sid, code, code, html.escape(path)))
        body = blocks.get(path) or blocks.get(path.split("/")[-1]) or "(no textual diff)"
        panels.append('<section class="panel dr-panel" id="%s"><h3><span class="dr-st s-%s">%s</span> %s</h3><pre class="dr-diff">%s</pre></section>'
                      % (sid, code, lab, html.escape(path), color_diff(body)))
    if not files:
        panels.append('<section class="panel dr-panel dr-empty">No changes in %s.</section>' % html.escape(a.rev))

    P = []
    P.append("<!doctype html><html lang='en'><head><meta charset='utf-8'>")
    P.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    P.append("<title>" + html.escape(a.title) + "</title>")
    P.append("<style>\n" + css + "\n</style></head><body data-quality='performance'>")
    P.append("<div class='bg'></div><div class='cathedral'></div><div class='vault-lines'></div><div class='fog'></div><div class='embers'></div>")
    P.append("<div class='shell'>")
    P.append("<header class='topbar relic-frame'>")
    P.append("<div><div class='eyebrow'>IMPERIUM NEW REALITY \u00b7 WEB SANCTUM</div><h1>" + html.escape(a.title) + "</h1><div class='contour'>read-only \u00b7 aquarium of changes between two commits</div></div>")
    P.append("<div class='pills'><span>" + html.escape(branch or "?") + "</span><span>" + html.escape(base_ci["sha7"]) + " \u2192 " + html.escape(head_ci["sha7"]) + "</span><span class='seal'>" + html.escape(a.rev) + "</span></div>")
    P.append("</header>")
    P.append("<aside class='sidebar relic-frame'>")
    P.append("<button class='dr-file active' data-target='all'>\u25a3 All changed files</button>")
    P.extend(side)
    P.append("</aside>")
    P.append("<main class='main'>")
    # KPI cards
    P.append("<div class='cards three'>")
    P.append("<article class='card relic-frame'><b>" + files_changed + "</b><span>files changed</span></article>")
    P.append("<article class='card relic-frame'><b style='color:#9fe6c0'>+" + ins + "</b><span>insertions</span></article>")
    P.append("<article class='card relic-frame'><b style='color:#f0989b'>-" + dele + "</b><span>deletions</span></article>")
    P.append("</div>")
    # Timeline (two commits)
    P.append("<section class='timeline'>")
    P.append(render_commit_card(base_ci, "Previous \u00b7 base", "is-prev"))
    P.append("<div class='timeline-arrow' aria-hidden='true'>\u2192</div>")
    P.append(render_commit_card(head_ci, "Latest \u00b7 head", "is-head"))
    P.append("</section>")
    # Functional dossier
    P.append("<section class='panel fn-changes relic-frame'>")
    P.append("<h3>Functional changes <span class='fn-sub'>parsed from the diff (Python / JS / TS / PowerShell / Go)</span></h3>")
    P.append("<div class='fn-cols'>")
    P.append(render_fn_group("Appeared", appeared, "g-added"))
    P.append(render_fn_group("Removed", removed, "g-removed"))
    P.append(render_fn_group("Modified", modified, "g-modified"))
    P.append("</div></section>")
    # Per-file diffs
    P.extend(panels)
    P.append("</main></div>")
    P.append("<script>")
    P.append("document.querySelectorAll('.dr-file').forEach(function(b){b.addEventListener('click',function(){var t=b.dataset.target;document.querySelectorAll('.dr-panel').forEach(function(p){p.style.display=(t==='all'||p.id===t)?'block':'none';});document.querySelectorAll('.dr-file').forEach(function(x){x.classList.toggle('active',x===b);});if(t!=='all'){var el=document.getElementById(t);if(el){el.scrollIntoView({behavior:'smooth',block:'start'});}}});});")
    P.append("</script>")
    P.append("</body></html>")
    html_out = "".join(P)

    out = a.out or os.path.join(repo, "..", "_LOCAL_HANDOFF", "WARP_DIFF_ROOM", "WARP_DIFF_ROOM.html")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html_out)

    summary = {
        "out": out, "rev": a.rev,
        "base": base_ci["sha7"], "head": head_ci["sha7"], "branch": branch,
        "base_subject": base_ci["subj"], "head_subject": head_ci["subj"],
        "files": int(files_changed) if files_changed.isdigit() else len(files),
        "insertions": int(ins), "deletions": int(dele),
        "appeared": len(appeared), "removed_fn": len(removed), "modified_fn": len(modified),
        "bytes": len(html_out.encode("utf-8")),
    }
    with open(os.path.join(os.path.dirname(out), "WARP_DIFF_ROOM.summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    sys.stdout.write(json.dumps(summary, ensure_ascii=True) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
