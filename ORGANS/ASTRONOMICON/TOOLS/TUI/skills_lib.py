#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IMPERIUM skills library v0_1.

Скиллы — личные инструкции владельца. Тела живут под MECHANICUS
(смотритель работоспособности), индекс статусов ведёт ADMINISTRATUM.
Выбрать в задачу можно только ACTIVE/EXPERIMENTAL.
Чистый stdlib. Ядро E3 (selftest реально гоняется).
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

SKILL_SCHEMA = "imperium.skill.v0_1"
INDEX_SCHEMA = "imperium.skills_index.v0_1"

STATUSES = ["DRAFT", "ACTIVE", "EXPERIMENTAL", "DEPRECATED", "BROKEN"]
SELECTABLE = ("ACTIVE", "EXPERIMENTAL")
NEEDS_REPAIR = ("DRAFT", "DEPRECATED", "BROKEN")

SKILLS_REL = os.path.join("ORGANS", "MECHANICUS", "SKILLS")
INDEX_REL = os.path.join("ORGANS", "ADMINISTRATUM", "INDEX", "skills_index.json")


def _utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class SkillStore:
    def __init__(self, reality):
        self.reality = os.path.abspath(reality)
        self.skills_dir = os.path.join(self.reality, SKILLS_REL)
        self.index_path = os.path.join(self.reality, INDEX_REL)

    def _skill_dirs(self):
        if not os.path.isdir(self.skills_dir):
            return []
        out = []
        for name in sorted(os.listdir(self.skills_dir)):
            d = os.path.join(self.skills_dir, name)
            if os.path.isdir(d) and os.path.isfile(os.path.join(d, "SKILL.json")):
                out.append(d)
        return out

    def _read_manifest(self, skill_dir):
        with open(os.path.join(skill_dir, "SKILL.json"), encoding="utf-8") as f:
            return json.load(f)

    def _checksum(self, skill_dir, man):
        h = hashlib.sha256()
        for rel in ["SKILL.json", man.get("body_file") or "SKILL.md"]:
            fp = os.path.join(skill_dir, rel)
            if os.path.isfile(fp):
                with open(fp, "rb") as f:
                    h.update(rel.encode("utf-8"))
                    h.update(f.read())
        return "sha256:" + h.hexdigest()

    def _health(self, skill_dir, man):
        hc = man.get("health") or {}
        htype = hc.get("type", "none")
        if htype == "checklist":
            ref = hc.get("ref", "")
            ok = bool(ref) and os.path.isfile(os.path.join(skill_dir, ref))
            return ("OK" if ok else "FAIL", "checklist:" + (ref or "-"))
        if htype == "script":
            ref = hc.get("ref", "")
            fp = os.path.join(skill_dir, ref)
            if not os.path.isfile(fp):
                return ("FAIL", "script not found: " + ref)
            try:
                r = subprocess.run([sys.executable, fp], cwd=skill_dir,
                                   capture_output=True, text=True, timeout=30)
                return ("OK" if r.returncode == 0 else "FAIL", "script rc=%d" % r.returncode)
            except Exception as e:
                return ("FAIL", "script error: %s" % e)
        return ("UNKNOWN", "no health check")

    def reindex(self):
        skills = []
        for d in self._skill_dirs():
            rel_home = os.path.relpath(d, self.reality).replace(os.sep, "/")
            try:
                man = self._read_manifest(d)
            except Exception as e:
                skills.append({
                    "skill_id": os.path.basename(d), "title": "(битый SKILL.json)",
                    "version": None, "declared_status": "BROKEN", "status": "BROKEN",
                    "selectable": False, "tags": [], "applies_to": {}, "home": rel_home,
                    "body_file": "SKILL.md", "checksum": None,
                    "last_health": "FAIL", "health_note": "manifest: %s" % e, "updated": _utc(),
                })
                continue
            health, note = self._health(d, man)
            declared = man.get("status", "DRAFT")
            if declared not in STATUSES:
                declared = "DRAFT"
            eff = "BROKEN" if health == "FAIL" else declared
            skills.append({
                "skill_id": man.get("skill_id", os.path.basename(d)),
                "title": man.get("title", os.path.basename(d)),
                "version": man.get("version"),
                "declared_status": declared,
                "status": eff,
                "selectable": eff in SELECTABLE,
                "tags": man.get("tags", []),
                "applies_to": man.get("applies_to", {}),
                "home": rel_home,
                "body_file": man.get("body_file") or "SKILL.md",
                "checksum": self._checksum(d, man),
                "last_health": health,
                "health_note": note,
                "updated": _utc(),
            })
        index = {
            "schema_version": INDEX_SCHEMA, "generated_utc": _utc(),
            "reality": self.reality, "count": len(skills),
            "statuses": STATUSES, "selectable_statuses": list(SELECTABLE),
            "skills": skills,
        }
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        return index

    def load_index(self):
        if not os.path.isfile(self.index_path):
            return {"schema_version": INDEX_SCHEMA, "count": 0, "skills": []}
        with open(self.index_path, encoding="utf-8") as f:
            return json.load(f)

    def list_skills(self, selectable_only=False):
        sk = self.load_index().get("skills", [])
        if selectable_only:
            sk = [s for s in sk if s.get("status") in SELECTABLE]
        return sk

    def get(self, skill_id):
        for s in self.load_index().get("skills", []):
            if s.get("skill_id") == skill_id:
                return s
        return None

    def body(self, skill_id):
        s = self.get(skill_id)
        if not s:
            return None
        fp = os.path.join(self.reality, s["home"].replace("/", os.sep),
                          s.get("body_file", "SKILL.md"))
        if os.path.isfile(fp):
            with open(fp, encoding="utf-8") as f:
                return f.read()
        return None

    def validate_selection(self, skill_ids):
        reasons = []
        for sid in skill_ids or []:
            s = self.get(sid)
            if not s:
                reasons.append({"gate": "SKILLS", "code": "SKILL_UNKNOWN",
                                "message": "скилл %r нет в индексе ADMINISTRATUM" % sid})
            elif s.get("status") not in SELECTABLE:
                reasons.append({"gate": "SKILLS", "code": "SKILL_NOT_SELECTABLE",
                                "message": "скилл %r в статусе %s — выбрать нельзя (только %s)"
                                % (sid, s.get("status"), "/".join(SELECTABLE))})
        return (not reasons), reasons

    def assemble_skills_brief(self, skill_ids, dest_dir):
        ok, reasons = self.validate_selection(skill_ids)
        if not ok:
            return None, reasons
        lines = ["# SKILLS BRIEF", "",
                 "_Подано MECHANICUS. Сервитор обязан учесть эти скиллы._", ""]
        for sid in skill_ids:
            s = self.get(sid)
            body = self.body(sid) or "(тело отсутствует)"
            lines += ["---", "## %s — %s" % (s["skill_id"], s.get("title", "")),
                      "- статус: %s · версия: %s" % (s.get("status"), s.get("version")),
                      "- источник: %s" % s.get("home"),
                      "- checksum: %s" % s.get("checksum"), "", body, ""]
        os.makedirs(dest_dir, exist_ok=True)
        path = os.path.join(dest_dir, "SKILLS_BRIEF.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return path, []

    def assemble_logos_context(self, dest_dir, intent, lead_organ=None,
                               participant_organs=None, skill_ids=None, constraints=None):
        participant_organs = participant_organs or []
        skill_ids = skill_ids or []
        ok, reasons = self.validate_selection(skill_ids)
        if not ok:
            return None, reasons
        lines = ["# LOGOS CONTEXT", "", "## Интент", intent or "(пусто)", "",
                 "## Органы", "- ведущий: %s" % (lead_organ or "-"),
                 "- участники: %s" % (", ".join(participant_organs) or "-"), ""]
        if constraints:
            lines += ["## Ограничения / доп. условия", constraints, ""]
        lines += ["## Скиллы (от MECHANICUS)"]
        if skill_ids:
            for sid in skill_ids:
                s = self.get(sid)
                body = self.body(sid) or "(тело отсутствует)"
                lines += ["", "### %s — %s (%s)" % (s["skill_id"], s.get("title", ""), s.get("status")),
                          body]
        else:
            lines += ["(не выбраны)"]
        os.makedirs(dest_dir, exist_ok=True)
        path = os.path.join(dest_dir, "LOGOS_CONTEXT.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return path, []


def _demos():
    return [
        {"man": {"schema_version": SKILL_SCHEMA, "skill_id": "MECH-SKILL-PORTABILITY-0001",
                 "title": "Портативные пути без хардкода", "version": "0.1", "status": "ACTIVE",
                 "tags": ["paths", "python", "powershell"],
                 "applies_to": {"organs": ["ADMINISTRATUM"], "change_kinds": ["REFACTOR", "PATCH"]},
                 "body_file": "SKILL.md", "author": "OWNER_MANUAL",
                 "health": {"type": "checklist", "ref": "checks/CHECKLIST.md"}},
         "body": "# Портативные пути\n\n- Никогда не хардкодить диск.\n- Резолвить корни через @REALITY/@HARNESS.\n- Нет конфига — явная ошибка, не fallback.\n",
         "checklist": "# CHECKLIST\n- [x] нет хардкод-литералов диска\n"},
        {"man": {"schema_version": SKILL_SCHEMA, "skill_id": "MECH-SKILL-WILD-0002",
                 "title": "Экспериментальный рефактор", "version": "0.1", "status": "EXPERIMENTAL",
                 "tags": ["experimental"], "applies_to": {"organs": [], "change_kinds": []},
                 "body_file": "SKILL.md", "author": "OWNER_MANUAL", "health": {"type": "none"}},
         "body": "# Эксперимент\n\nНеобычный подход, доп. условия применяются осторожно.\n",
         "checklist": None},
        {"man": {"schema_version": SKILL_SCHEMA, "skill_id": "MECH-SKILL-OLDLINT-0003",
                 "title": "Старый линтер", "version": "0.1", "status": "ACTIVE",
                 "tags": ["lint"], "applies_to": {"organs": [], "change_kinds": []},
                 "body_file": "SKILL.md", "author": "OWNER_MANUAL",
                 "health": {"type": "checklist", "ref": "checks/CHECKLIST.md"}},
         "body": "# Старый линтер\n\nЗаявлен ACTIVE, но health-чек провалится -> станет BROKEN.\n",
         "checklist": None},
        {"man": {"schema_version": SKILL_SCHEMA, "skill_id": "MECH-SKILL-LEGACY-0004",
                 "title": "Устаревший приём", "version": "0.1", "status": "DEPRECATED",
                 "tags": ["legacy"], "applies_to": {"organs": [], "change_kinds": []},
                 "body_file": "SKILL.md", "author": "OWNER_MANUAL", "health": {"type": "none"}},
         "body": "# Устаревший приём\n\nБольше не выбирается для задач.\n",
         "checklist": None},
    ]


def seed_demo(reality):
    base = os.path.join(reality, SKILLS_REL)
    created = []
    for d in _demos():
        man = d["man"]
        sid = man["skill_id"]
        sdir = os.path.join(base, sid)
        if os.path.isdir(sdir):
            continue
        os.makedirs(os.path.join(sdir, "checks"), exist_ok=True)
        with open(os.path.join(sdir, "SKILL.json"), "w", encoding="utf-8") as f:
            json.dump(man, f, ensure_ascii=False, indent=2)
        with open(os.path.join(sdir, man.get("body_file", "SKILL.md")), "w", encoding="utf-8") as f:
            f.write(d["body"])
        if d.get("checklist"):
            with open(os.path.join(sdir, "checks", "CHECKLIST.md"), "w", encoding="utf-8") as f:
                f.write(d["checklist"])
        created.append(sid)
    return created


def selftest():
    tmp = tempfile.mkdtemp(prefix="imp_skills_")
    ok = True
    try:
        reality = os.path.join(tmp, "REALITY")
        os.makedirs(reality, exist_ok=True)
        seed_demo(reality)
        st = SkillStore(reality)
        idx = st.reindex()

        def check(name, cond):
            print("  [%s] %s" % ("OK" if cond else "FAIL", name))
            return cond

        ok &= check("индекс: 4 скилла", idx["count"] == 4)
        sel = {s["skill_id"] for s in st.list_skills(selectable_only=True)}
        ok &= check("выбираемы: PORTABILITY + WILD",
                    sel == {"MECH-SKILL-PORTABILITY-0001", "MECH-SKILL-WILD-0002"})
        broken = st.get("MECH-SKILL-OLDLINT-0003")
        ok &= check("health FAIL -> BROKEN", bool(broken) and broken["status"] == "BROKEN")
        depr = st.get("MECH-SKILL-LEGACY-0004")
        ok &= check("DEPRECATED не выбираем",
                    bool(depr) and depr["status"] == "DEPRECATED" and not depr["selectable"])
        ok1, r1 = st.validate_selection(["MECH-SKILL-OLDLINT-0003"])
        ok &= check("BROKEN -> SKILL_NOT_SELECTABLE",
                    (not ok1) and bool(r1) and r1[0]["code"] == "SKILL_NOT_SELECTABLE")
        ok2, r2 = st.validate_selection(["NOPE"])
        ok &= check("неизвестный -> SKILL_UNKNOWN",
                    (not ok2) and bool(r2) and r2[0]["code"] == "SKILL_UNKNOWN")
        pack = os.path.join(tmp, "pack")
        os.makedirs(pack, exist_ok=True)
        bp, _ = st.assemble_skills_brief(
            ["MECH-SKILL-PORTABILITY-0001", "MECH-SKILL-WILD-0002"], pack)
        bc = open(bp, encoding="utf-8").read() if bp else ""
        ok &= check("SKILLS_BRIEF.md собран", bool(bp) and "PORTABILITY" in bc and "WILD" in bc)
        lp, _ = st.assemble_logos_context(
            pack, "тест интента", lead_organ="STRATEGIUM",
            participant_organs=["MECHANICUS", "ADMINISTRATUM"],
            skill_ids=["MECH-SKILL-WILD-0002"], constraints="только stdlib")
        lc = open(lp, encoding="utf-8").read() if lp else ""
        ok &= check("LOGOS_CONTEXT.md собран", bool(lp) and "LOGOS CONTEXT" in lc and "WILD" in lc)
        print("== skills_lib selftest: %s ==" % ("ВСЁ ЗЕЛЕНО" if ok else "ЕСТЬ ПАДЕНИЯ"))
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="IMPERIUM skills library v0_1")
    ap.add_argument("--reality", help="корень REALITY")
    ap.add_argument("--reindex", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--selectable", action="store_true", help="только выбираемые")
    ap.add_argument("--seed", action="store_true", help="засеять примеры скиллов")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.reality:
        sys.stderr.write("ERROR: укажи --reality (или --selftest)\n")
        return 1
    st = SkillStore(args.reality)
    if args.seed:
        created = seed_demo(args.reality)
        print("seeded: %s" % (", ".join(created) or "(уже есть)"))
    if args.reindex or args.seed:
        idx = st.reindex()
        print("reindex: %d скилл(ов) -> %s" % (idx["count"], st.index_path))
    if args.list or args.selectable:
        for s in st.list_skills(selectable_only=args.selectable):
            print("  %-32s %-12s health=%-7s %s"
                  % (s["skill_id"], s["status"], s.get("last_health"), s.get("title")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
