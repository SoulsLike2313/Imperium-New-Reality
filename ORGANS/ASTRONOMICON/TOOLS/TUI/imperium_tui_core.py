#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IMPERIUM TUI core v0_4 — общее ядро для Throne-TUI и Organ-TUI.

Переносимо (stdlib only). Бэкенд вызывает уже проверенные движки:
  - astra_gate.validate / astra_cycle.Cycle / imperium_roots

UI:
  - curses (вкл. windows-curses) — полноэкранный режим с имперской темой;
  - иначе — текстовое меню без зависимостей.

UI API (единый для curses/plain):
  ui.menu(title, items[(label,value)], footer?) -> value | None
  ui.text(title, lines[str])                    -> None
  ui.ask(prompt, default="")                     -> str | None   (None = отмена)
  ui.confirm(prompt)                             -> bool
"""
import importlib.util
import json
import os
import subprocess
import sys

CANON_ORGANS = [
    "ADMINISTRATUM", "ASTRONOMICON", "CUSTODES", "DOCTRINARIUM",
    "INQUISITION", "MECHANICUS", "OFFICIO_AGENTIS", "SCHOLA_IMPERIALIS",
    "STRATEGIUM",
]
THRONE = "THRONE"
CONFIG_NAME = "imperium_tui.config.json"

CHANGE_KINDS = ["PATCH", "NEW_FILE", "DELETE", "REFACTOR", "DOC"]
SUBMITTERS = ["OWNER_MANUAL", "SERVITOR"]

DEFAULT_BANNER = [
    "   ╔═══════════════════════════════════════╗",
    "   ║        I M P E R I U M   T U I        ║",
    "   ║        Throne over the Organs         ║",
    "   ╚═══════════════════════════════════════╝",
]


def _frame_banner(title, owner, subtitle):
    """Авто-рамка под любую длину имён (выравнивание гарантировано)."""
    body = [" ".join(title)]
    if owner:
        body.append("Император :: " + owner)
    if subtitle:
        body.append(subtitle)
    inner = max([len(s) for s in body] + [38]) + 6
    out = ["   ╔" + "═" * inner + "╗"]
    for s in body:
        pad = inner - len(s)
        left = pad // 2
        out.append("   ║" + " " * left + s + " " * (pad - left) + "║")
    out.append("   ╚" + "═" * inner + "╝")
    return out


def _self_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _load_module(path, name):
    if not path or not os.path.isfile(path):
        return None
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


class Backend:
    """Вся логика без UI — чтобы теститься headless (--selftest)."""

    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.join(_self_dir(), CONFIG_NAME)
        self.cfg = self._load_cfg()
        self.roots = self._load_roots()
        self.gate = self._load_engine("gate_module", "astra_gate")
        self.cycle = self._load_engine("cycle_module", "astra_cycle")

    def _load_cfg(self):
        if os.path.isfile(self.config_path):
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _load_roots(self):
        rp = self._raw("roots_module")
        cand = [rp] if rp else []
        cand.append(os.path.join(_self_dir(), "imperium_roots.py"))
        for c in cand:
            m = _load_module(c, "imperium_roots")
            if m:
                return m
        return None

    def _raw(self, key):
        return (self.cfg.get(key) or "").strip() or None

    def resolve(self, val):
        if not val:
            return val
        if isinstance(val, str) and val.startswith("@") and self.roots:
            try:
                return self.roots.resolve(val)
            except Exception:
                return val
        return os.path.expanduser(os.path.expandvars(val))

    def reality(self):
        return self.resolve(self.cfg.get("reality") or "@REALITY")

    def inbox(self):
        return self.resolve(self.cfg.get("inbox") or "@HARNESS/_INBOX/PACKS")

    def receipts_dir(self):
        return self.resolve(self.cfg.get("receipts") or "@HARNESS/_S3_RECEIPTS")

    def trunk(self):
        return self.cfg.get("trunk") or "master"

    def organ_dir(self, organ):
        r = self.reality()
        return os.path.join(r, "ORGANS", organ) if r else None

    def banner(self):
        bf = self.resolve(self._raw("banner_file"))
        cand = [bf] if bf else []
        cand.append(os.path.join(_self_dir(), "banner.txt"))
        for c in cand:
            if c and os.path.isfile(c):
                try:
                    with open(c, encoding="utf-8") as f:
                        return [ln.rstrip("\n") for ln in f]
                except Exception:
                    pass
        owner = (self.cfg.get("owner") or "").strip()
        title = (self.cfg.get("title") or "IMPERIUM THRONE").strip()
        subtitle = (self.cfg.get("subtitle") or ("Личный лаунчер · Оркестрация" if owner else "Throne over the Organs")).strip()
        return _frame_banner(title, owner, subtitle)

    def _load_engine(self, cfg_key, modname):
        p = self.resolve(self._raw(cfg_key))
        cand = [p] if p else []
        cand.append(os.path.join(_self_dir(), modname + ".py"))
        for c in cand:
            m = _load_module(c, modname)
            if m:
                return m
        return None

    def list_packs(self, organ=None):
        root = self.inbox()
        out = []
        if not root or not os.path.isdir(root):
            return out
        for name in sorted(os.listdir(root)):
            d = os.path.join(root, name)
            mf = os.path.join(d, "TASK_MANIFEST.json")
            if not os.path.isfile(mf):
                continue
            try:
                with open(mf, encoding="utf-8") as f:
                    m = json.load(f)
            except Exception:
                m = {}
            if organ and (m.get("target_organ") != organ):
                continue
            out.append({
                "dir": d,
                "task_id": m.get("task_id", name),
                "title": m.get("title", ""),
                "target_organ": m.get("target_organ"),
                "submitted_by": m.get("submitted_by"),
                "change_kind": m.get("change_kind"),
            })
        return out

    def validate(self, pack_dir):
        if not self.gate:
            return "ERROR", [{"gate": "-", "code": "NO_GATE", "message": "astra_gate не подключён"}], {}
        return self.gate.validate(pack_dir)

    def run_cycle(self, pack_dir, apply=False, throne_permit="GRANTED"):
        if not self.cycle:
            return "NO_CYCLE", {"error": "astra_cycle не подключён", "stages": []}
        log = []
        c = self.cycle.Cycle(pack_dir, self.reality(), self.trunk(),
                             throne_permit, apply, log)
        return c.run()

    def list_receipts(self, limit=20):
        root = self.receipts_dir()
        out = []
        if not root or not os.path.isdir(root):
            return out
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                if fn.endswith(".json") or fn.endswith(".txt"):
                    fp = os.path.join(dirpath, fn)
                    try:
                        out.append((os.path.getmtime(fp), fp))
                    except OSError:
                        pass
        out.sort(reverse=True)
        return [p for _, p in out[:limit]]

    def organ_status(self):
        packs = self.list_packs()
        counts = {o: 0 for o in CANON_ORGANS}
        for p in packs:
            o = p.get("target_organ")
            if o in counts:
                counts[o] += 1
        return counts

    # ---- git / данные ----
    def git_head(self):
        r = self.reality()
        if not r or not os.path.isdir(os.path.join(r, ".git")):
            return None
        try:
            def g(*a):
                return subprocess.run(["git", "-C", r, *a], capture_output=True,
                                      text=True, timeout=10).stdout.strip()
            return {"sha": g("rev-parse", "--short", "HEAD"),
                    "subject": g("log", "-1", "--pretty=%s"),
                    "state": "DIRTY" if g("status", "--porcelain") else "clean"}
        except Exception:
            return None

    def request_data(self, organ):
        lines = []
        gh = self.git_head()
        lines.append("git HEAD: %s" % ("%s (%s) — %s" % (gh["sha"], gh["state"], gh["subject"]) if gh else "(нет git в reality)"))
        od = self.organ_dir(organ)
        lines += ["", "каталог органа: %s" % od]
        if od and os.path.isdir(od):
            any_f = False
            for root, _dirs, files in os.walk(od):
                rel = os.path.relpath(root, od)
                pref = "" if rel == "." else rel.replace(os.sep, "/") + "/"
                for fn in sorted(files):
                    lines.append("  %s%s" % (pref, fn))
                    any_f = True
            if not any_f:
                lines.append("  (пусто)")
        else:
            lines.append("  (каталог отсутствует)")
        packs = self.list_packs(organ)
        lines += ["", "паков в очереди: %d" % len(packs)]
        for p in packs:
            lines.append("  - %s [%s] %s" % (p["task_id"], p["change_kind"] or "-", p["title"]))
        rec = self.list_receipts(8)
        lines += ["", "последние рецепты:"]
        lines += ["  " + x for x in rec] if rec else ["  (пусто)"]
        return lines

    # ---- форма: новый таск-пак ----
    def _skill_store(self):
        try:
            import skills_lib
        except Exception:
            return None
        r = self.reality()
        return skills_lib.SkillStore(r) if r else None

    def list_skills(self, selectable_only=True):
        st = self._skill_store()
        return st.list_skills(selectable_only=selectable_only) if st else []

    def reindex_skills(self):
        st = self._skill_store()
        return st.reindex() if st else None

    def new_task_pack(self, organ, task_id, title, intent,
                      change_kind="PATCH", submitted_by="OWNER_MANUAL",
                      skills=None, participant_organs=None, lead_organ=None):
        inbox = self.inbox()
        if not inbox:
            return None, "inbox не задан в конфиге"
        skills = skills or []
        participant_organs = participant_organs or []
        lead = lead_organ or organ
        st = self._skill_store()
        if st and skills:
            ok, reasons = st.validate_selection(skills)
            if not ok:
                return None, "; ".join(r["message"] for r in reasons)
        safe = "".join(c if (c.isalnum() or c in "-_.") else "-" for c in (task_id or "")).strip("-") or "TASK"
        d = os.path.join(inbox, safe)
        if os.path.exists(d):
            return None, "пак %s уже существует" % safe
        try:
            os.makedirs(os.path.join(d, "files"), exist_ok=True)
            manifest = {
                "schema_version": "imperium.astra_task_pack.v0_1",
                "pack_kind": "ASTRA_TASK",
                "task_id": safe,
                "title": title or safe,
                "submitted_by": submitted_by,
                "target_organ": lead,
                "lead_organ": lead,
                "participant_organs": participant_organs,
                "skills": skills,
                "intent": intent or "",
                "change_kind": change_kind,
                "payload": [],
                "declared_evidence_level": "E1",
            }
            with open(os.path.join(d, "TASK_MANIFEST.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
            with open(os.path.join(d, "PAYLOAD_NOTE.md"), "w", encoding="utf-8") as f:
                f.write("# %s\n\n%s\n\nПоложи изменения в files/ и заполни payload.\n" % (safe, intent or ""))
            if st and skills:
                st.assemble_skills_brief(skills, d)
            return d, None
        except Exception as e:
            return None, str(e)


    def new_logos_pack(self, task_id, intent, lead_organ=None,
                       participant_organs=None, skills=None, constraints=None):
        inbox = self.inbox()
        if not inbox:
            return None, "inbox не задан в конфиге"
        skills = skills or []
        participant_organs = participant_organs or []
        st = self._skill_store()
        if st and skills:
            ok, reasons = st.validate_selection(skills)
            if not ok:
                return None, "; ".join(r["message"] for r in reasons)
        safe = "".join(c if (c.isalnum() or c in "-_.") else "-" for c in (task_id or "")).strip("-") or "LOGOS"
        if not safe.upper().startswith("LOGOS"):
            safe = "LOGOS-" + safe
        d = os.path.join(inbox, safe)
        if os.path.exists(d):
            return None, "пак %s уже существует" % safe
        try:
            os.makedirs(d, exist_ok=True)
            manifest = {
                "schema_version": "imperium.logos_pack.v0_1",
                "pack_kind": "LOGOS_BRIEF",
                "task_id": safe,
                "intent": intent or "",
                "lead_organ": lead_organ,
                "participant_organs": participant_organs,
                "skills": skills,
                "constraints": constraints or "",
            }
            with open(os.path.join(d, "LOGOS_MANIFEST.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
            if st:
                st.assemble_logos_context(d, intent, lead_organ=lead_organ,
                                          participant_organs=participant_organs,
                                          skill_ids=skills, constraints=constraints)
            return d, None
        except Exception as e:
            return None, str(e)


# ===================== UI: curses или текстовый fallback =====================
def curses_available():
    try:
        import curses  # noqa: F401
        return True
    except Exception:
        return False


class PlainUI:
    """Текстовое меню — работает везде (вкл. Windows без curses)."""

    def __init__(self, banner=None):
        self.banner = banner or []

    def menu(self, title, items, footer=None):
        print()
        for ln in self.banner:
            print(ln)
        print("=" * 60)
        print("  " + title)
        print("=" * 60)
        for i, (label, _v) in enumerate(items):
            print("  %2d) %s" % (i + 1, label))
        while True:
            try:
                r = input("выбор (номер, q — назад): ").strip()
            except EOFError:
                return None
            if r.lower() in ("q", ""):
                return None
            if r.isdigit() and 1 <= int(r) <= len(items):
                return items[int(r) - 1][1]
            print("  ? неверный выбор")

    def dashboard(self, title, items, panels, footer=None):
        print()
        for ln in self.banner:
            print(ln)
        print("=" * 64)
        print("  " + title)
        print("=" * 64)
        for heading, lines in panels:
            print("\n  [ " + heading + " ]")
            for ln in lines:
                print("    " + str(ln))
        print("\n  --- НАВИГАЦИЯ ---")
        for i, (label, _v) in enumerate(items):
            print("  %2d) %s" % (i + 1, label))
        while True:
            try:
                r = input("выбор (номер, q — выход): ").strip()
            except EOFError:
                return None
            if r.lower() in ("q", ""):
                return None
            if r.isdigit() and 1 <= int(r) <= len(items):
                return items[int(r) - 1][1]
            print("  ? неверный выбор")

    def form(self, title, fields):
        print()
        for ln in self.banner:
            print(ln)
        print("=" * 64)
        print("  " + title)
        print("=" * 64)
        out = {}
        for f in fields:
            if f.get("type") == "choice":
                v = self.menu(f["label"], [(c, c) for c in f["choices"]])
                if v is None:
                    return None
            else:
                v = self.ask(f["label"], f.get("default", ""))
                if v is None:
                    return None
            out[f["key"]] = v
        return out

    def text(self, title, lines):
        print("\n" + "-" * 60)
        print("  " + title)
        print("-" * 60)
        for ln in lines:
            print(ln)
        try:
            input("\n[Enter] назад...")
        except EOFError:
            pass

    def ask(self, prompt, default=""):
        try:
            r = input("%s%s: " % (prompt, (" [%s]" % default) if default else "")).strip()
        except EOFError:
            return None
        return r or default

    def confirm(self, prompt):
        try:
            r = input("%s [y/N]: " % prompt).strip().lower()
        except EOFError:
            return False
        return r in ("y", "yes", "д", "да")


class CursesUI:
    def __init__(self, stdscr, banner=None):
        self.stdscr = stdscr
        self.banner = banner or []

    def menu(self, title, items, footer="↑↓/jk — выбор   Enter — ок   q — назад"):
        return _curses_menu(self.stdscr, title, items, footer, self.banner)

    def dashboard(self, title, items, panels, footer="↑↓/jk — выбор   Enter — ок   q — выход"):
        return _curses_dashboard(self.stdscr, title, items, panels, footer, self.banner)

    def form(self, title, fields):
        return _curses_form(self.stdscr, title, fields, self.banner)

    def text(self, title, lines):
        return _curses_text(self.stdscr, title, lines)

    def ask(self, prompt, default=""):
        return _curses_ask(self.stdscr, prompt, default, self.banner)

    def confirm(self, prompt):
        r = _curses_menu(self.stdscr, prompt, [("Да", True), ("Нет", False)],
                         "↑↓ — выбор   Enter — ок", self.banner)
        return bool(r)


def run_app(app_fn, banner=None):
    """Запускает app_fn(ui): curses если есть, иначе текстовый режим."""
    banner = banner or []
    if curses_available():
        import curses

        def _w(stdscr):
            curses.curs_set(0)
            stdscr.keypad(True)         # ВАЖНО: стре��ки -> KEY_UP/KEY_DOWN
            try:
                curses.start_color()
                curses.use_default_colors()
                _init_theme(curses)
            except Exception:
                pass
            try:
                curses.mousemask(0)
            except Exception:
                pass
            app_fn(CursesUI(stdscr, banner))
        curses.wrapper(_w)
    else:
        print("(curses недоступен — текстовый режим; для полноэкранного: pip install windows-curses)")
        app_fn(PlainUI(banner))


# ---- имперская тема ----
THEME = {}


def _init_theme(curses):
    pairs = {
        "title": (curses.COLOR_YELLOW, curses.COLOR_RED),
        "sel": (curses.COLOR_BLACK, curses.COLOR_YELLOW),
        "accent": (curses.COLOR_WHITE, -1),
        "footer": (curses.COLOR_CYAN, -1),
        "banner": (curses.COLOR_RED, -1),
        "border": (curses.COLOR_YELLOW, -1),
        "card": (curses.COLOR_YELLOW, -1),
        "ok": (curses.COLOR_GREEN, -1),
        "warn": (curses.COLOR_RED, -1),
        "dim": (curses.COLOR_CYAN, -1),
    }
    i = 1
    for name, (fg, bg) in pairs.items():
        try:
            curses.init_pair(i, fg, bg)
            THEME[name] = curses.color_pair(i)
        except Exception:
            THEME[name] = 0
        i += 1


def _attr(name, fallback=0):
    return THEME.get(name, fallback)


def _safe_addstr(stdscr, y, x, s, attr=0):
    import curses
    h, w = stdscr.getmaxyx()
    if y < 0 or y >= h or x < 0 or x >= w:
        return
    try:
        stdscr.addstr(y, x, str(s)[:max(0, w - x - 1)], attr)
    except curses.error:
        pass


def _draw_header(stdscr, title, banner):
    import curses
    stdscr.erase()
    y = 0
    for ln in banner:
        _safe_addstr(stdscr, y, 2, ln, _attr("banner") | curses.A_BOLD)
        y += 1
    _safe_addstr(stdscr, y, 0, " " + title + " ", _attr("title") | curses.A_BOLD)
    return y + 2


def _read_key(stdscr):
    """ESC-safe: отличает настоящий ESC от escape-последовательности стрелки."""
    k = stdscr.getch()
    if k == 27:
        stdscr.nodelay(True)
        nxt = stdscr.getch()
        if nxt == -1:
            stdscr.nodelay(False)
            return 27
        while stdscr.getch() != -1:
            pass
        stdscr.nodelay(False)
        return None
    return k


def _curses_menu(stdscr, title, items, footer, banner):
    import curses
    idx = 0
    while True:
        top = _draw_header(stdscr, title, banner)
        h, w = stdscr.getmaxyx()
        for i, (label, _v) in enumerate(items):
            y = top + i
            if y >= h - 1:
                break
            if i == idx:
                _safe_addstr(stdscr, y, 2, "> " + str(label), _attr("sel") | curses.A_BOLD)
            else:
                _safe_addstr(stdscr, y, 2, "  " + str(label), _attr("accent"))
        _safe_addstr(stdscr, h - 1, 0, footer, _attr("footer"))
        stdscr.refresh()
        k = _read_key(stdscr)
        if k in (curses.KEY_UP, ord("k"), ord("w")):
            idx = (idx - 1) % len(items)
        elif k in (curses.KEY_DOWN, ord("j"), ord("s")):
            idx = (idx + 1) % len(items)
        elif k in (curses.KEY_ENTER, 10, 13, ord(" ")):
            return items[idx][1]
        elif k in (ord("q"), ord("Q"), 27):
            return None
        elif k == curses.KEY_RESIZE:
            continue


def _box(stdscr, y, x, height, width, title="", battr=0, tattr=0):
    """Рисует рамку-карточку с заголовком в верхней рамке."""
    import curses
    if height < 2 or width < 2:
        return
    _safe_addstr(stdscr, y, x, "┌" + "─" * (width - 2) + "┐", battr)
    for i in range(1, height - 1):
        _safe_addstr(stdscr, y + i, x, "│", battr)
        _safe_addstr(stdscr, y + i, x + width - 1, "│", battr)
    _safe_addstr(stdscr, y + height - 1, x, "└" + "─" * (width - 2) + "┘", battr)
    if title:
        _safe_addstr(stdscr, y, x + 2, " " + str(title) + " ", tattr | curses.A_BOLD)


def _curses_form(stdscr, title, fields, banner):
    """Рич-форма в одном окне: ↑↓ между полями, ←→/Space для выбора."""
    import curses
    vals = [f.get("default", "") or "" for f in fields]
    for i, f in enumerate(fields):
        if f.get("type") == "choice" and vals[i] not in f.get("choices", []):
            vals[i] = (f.get("choices") or [""])[0]
    n = len(fields)
    SUBMIT = n
    idx = 0
    curses.curs_set(0)
    try:
        while True:
            stdscr.erase()
            h, w = stdscr.getmaxyx()
            by = 0
            for ln in banner:
                _safe_addstr(stdscr, by, max(0, (w - len(ln)) // 2), ln, _attr("banner") | curses.A_BOLD)
                by += 1
            _safe_addstr(stdscr, by, 0, (" " + title).ljust(w - 1), _attr("title") | curses.A_BOLD)
            top = by + 2
            cw = min(72, w - 4)
            _box(stdscr, top, 1, n + 4, cw, "ФОРМА", _attr("border"), _attr("card"))
            for i, f in enumerate(fields):
                yy = top + 1 + i
                sel = (i == idx)
                lab = str(f["label"])[:18].ljust(18)
                _safe_addstr(stdscr, yy, 3, lab, (_attr("card") | curses.A_BOLD) if sel else _attr("dim"))
                if f.get("type") == "choice":
                    disp = "< %s >" % vals[i]
                else:
                    disp = vals[i] + ("_" if sel else "")
                _safe_addstr(stdscr, yy, 22, str(disp)[:cw - 24], _attr("sel") if sel else _attr("accent"))
            sy = top + 1 + n + 1
            sattr = (_attr("sel") | curses.A_BOLD) if idx == SUBMIT else (_attr("ok") | curses.A_BOLD)
            _safe_addstr(stdscr, sy, 3, "[ ОТПРАВИТЬ ]", sattr)
            foot = "↑↓ — поле   ←→/Space — выбор   Enter — дальше   ESC — отмена"
            _safe_addstr(stdscr, h - 1, 0, (" " + foot).ljust(w - 1), _attr("footer"))
            stdscr.refresh()
            try:
                kk = stdscr.get_wch()
            except curses.error:
                continue
            if isinstance(kk, str):
                if kk in ("\n", "\r"):
                    if idx == SUBMIT:
                        return {fields[i]["key"]: (vals[i].strip() if isinstance(vals[i], str) else vals[i]) for i in range(n)}
                    idx = min(SUBMIT, idx + 1)
                elif kk == "\x1b":
                    return None
                elif kk == "\t":
                    idx = min(SUBMIT, idx + 1)
                elif idx < n and fields[idx].get("type") == "choice":
                    if kk == " ":
                        ch = fields[idx]["choices"]
                        cur = ch.index(vals[idx]) if vals[idx] in ch else 0
                        vals[idx] = ch[(cur + 1) % len(ch)]
                elif idx < n:
                    if kk in ("\x7f", "\b"):
                        vals[idx] = vals[idx][:-1]
                    elif kk.isprintable():
                        vals[idx] += kk
            else:
                if kk == curses.KEY_UP:
                    idx = (idx - 1) % (SUBMIT + 1)
                elif kk == curses.KEY_DOWN:
                    idx = (idx + 1) % (SUBMIT + 1)
                elif idx < n and fields[idx].get("type") == "choice" and kk in (curses.KEY_LEFT, curses.KEY_RIGHT):
                    ch = fields[idx]["choices"]
                    cur = ch.index(vals[idx]) if vals[idx] in ch else 0
                    step = 1 if kk == curses.KEY_RIGHT else -1
                    vals[idx] = ch[(cur + step) % len(ch)]
                elif idx < n and fields[idx].get("type") != "choice" and kk in (curses.KEY_BACKSPACE, 127, 8):
                    vals[idx] = vals[idx][:-1]
                elif kk == curses.KEY_RESIZE:
                    continue
    finally:
        curses.curs_set(0)


def _curses_dashboard(stdscr, title, items, panels, footer, banner):
    """Домашний экран-лаунчер: карточки данных + навигация (полноэкранно)."""
    import curses
    idx = 0
    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        by = 0
        for ln in banner:
            _safe_addstr(stdscr, by, max(0, (w - len(ln)) // 2), ln, _attr("banner") | curses.A_BOLD)
            by += 1
        _safe_addstr(stdscr, by, 0, (" " + title).ljust(w - 1), _attr("title") | curses.A_BOLD)
        top = by + 2
        region_h = (h - 1) - top
        if region_h < 5 or w < 30:
            _safe_addstr(stdscr, top, 0, "Окно слишком мало — разверни терминал", _attr("warn"))
            _safe_addstr(stdscr, h - 1, 0, footer, _attr("footer"))
            stdscr.refresh()
            k = _read_key(stdscr)
            if k in (ord("q"), ord("Q"), 27):
                return None
            continue
        left_w = min(40, max(24, w // 3))
        _box(stdscr, top, 1, region_h, left_w, "НАВИГАЦИЯ", _attr("border"), _attr("card"))
        for i, (label, _v) in enumerate(items):
            yy = top + 1 + i
            if yy >= top + region_h - 1:
                break
            if i == idx:
                _safe_addstr(stdscr, yy, 3, ("> " + str(label)).ljust(left_w - 4), _attr("sel") | curses.A_BOLD)
            else:
                _safe_addstr(stdscr, yy, 3, "  " + str(label), _attr("accent"))
        rx = left_w + 3
        rw = w - rx - 1
        ry = top
        for heading, lines in panels:
            remaining = (top + region_h) - ry
            if remaining < 3:
                break
            chh = min(len(lines) + 2, remaining)
            _box(stdscr, ry, rx, chh, rw, heading, _attr("border"), _attr("card"))
            for j, ln in enumerate(lines):
                if j >= chh - 2:
                    break
                _safe_addstr(stdscr, ry + 1 + j, rx + 2, str(ln)[:rw - 4], _attr("accent"))
            ry += chh
        _safe_addstr(stdscr, h - 1, 0, (" " + footer).ljust(w - 1), _attr("footer"))
        stdscr.refresh()
        k = _read_key(stdscr)
        if k in (curses.KEY_UP, ord("k"), ord("w")):
            idx = (idx - 1) % len(items)
        elif k in (curses.KEY_DOWN, ord("j"), ord("s")):
            idx = (idx + 1) % len(items)
        elif k in (curses.KEY_ENTER, 10, 13, ord(" ")):
            return items[idx][1]
        elif k in (ord("q"), ord("Q"), 27):
            return None
        elif k == curses.KEY_RESIZE:
            continue


def _curses_text(stdscr, title, lines):
    import curses
    top_line = 0
    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        _safe_addstr(stdscr, 0, 0, (" " + title).ljust(w - 1), _attr("title") | curses.A_BOLD)
        top = 2
        box_h = max(3, h - 3)
        _box(stdscr, top, 1, box_h, w - 2, "", _attr("border"), _attr("card"))
        body_h = box_h - 2
        view = lines[top_line:top_line + body_h]
        for i, ln in enumerate(view):
            _safe_addstr(stdscr, top + 1 + i, 3, str(ln)[:w - 6], _attr("accent"))
        more = "" if top_line + body_h >= len(lines) else "  ↓ещё"
        _safe_addstr(stdscr, h - 1, 0, (" ↑↓/jk — скролл   q — назад" + more).ljust(w - 1), _attr("footer"))
        stdscr.refresh()
        k = _read_key(stdscr)
        if k in (curses.KEY_UP, ord("k"), ord("w")):
            top_line = max(0, top_line - 1)
        elif k in (curses.KEY_DOWN, ord("j"), ord("s")):
            top_line = min(max(0, len(lines) - body_h), top_line + 1)
        elif k == curses.KEY_NPAGE:
            top_line = min(max(0, len(lines) - body_h), top_line + body_h)
        elif k == curses.KEY_PPAGE:
            top_line = max(0, top_line - body_h)
        elif k in (ord("q"), ord("Q"), 27, curses.KEY_ENTER, 10, 13):
            return
        elif k == curses.KEY_RESIZE:
            continue


def _curses_ask(stdscr, prompt, default, banner):
    import curses
    buf = list(default or "")
    curses.curs_set(1)
    try:
        while True:
            top = _draw_header(stdscr, "Ввод", banner)
            h, w = stdscr.getmaxyx()
            _safe_addstr(stdscr, top, 2, prompt, _attr("accent") | curses.A_BOLD)
            _safe_addstr(stdscr, top + 1, 2, "> " + "".join(buf), _attr("sel"))
            _safe_addstr(stdscr, h - 1, 0, "Enter — ок   ESC — отмена   Backspace — стереть", _attr("footer"))
            stdscr.refresh()
            try:
                ch = stdscr.get_wch()
            except curses.error:
                continue
            if isinstance(ch, str):
                if ch in ("\n", "\r"):
                    return "".join(buf).strip() or (default or "")
                if ch == "\x1b":
                    return None
                if ch in ("\x7f", "\b"):
                    if buf:
                        buf.pop()
                    continue
                if ch.isprintable():
                    buf.append(ch)
            else:
                if ch in (curses.KEY_BACKSPACE, 127, 8):
                    if buf:
                        buf.pop()
                elif ch == curses.KEY_ENTER:
                    return "".join(buf).strip() or (default or "")
                elif ch == curses.KEY_RESIZE:
                    continue
    finally:
        curses.curs_set(0)
