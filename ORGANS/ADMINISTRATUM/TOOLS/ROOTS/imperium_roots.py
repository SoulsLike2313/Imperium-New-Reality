#!/usr/bin/env python3
"""IMPERIUM ROOTS v0_2 — переносимый резолвер зон по алиасам (любая машина).
Приоритет по зоне: ENV IMPERIUM_<ALIAS> > конфиг(alias) > BASE-производный > git-toplevel(REALITY) > дефолт.
BASE: config.base > ENV IMPERIUM_HOME > авто (ближайший предок-папка IMPERIUM_*) > диск резолвера.
Путь '@ALIAS/sub' разворачивается в реальный; путь без '@' — как есть."""
import json
import os
import subprocess
import sys

SCHEMA_VERSION = "imperium.roots.v0_2"
CONFIG_NAME = "imperium.roots.json"
CANON = ("REALITY", "WARP", "HARNESS")
CANON_DEFAULTS = {
    "REALITY": r"E:\IMPERIUM_REALITY",
    "WARP": r"E:\IMPERIUM_WARP",
    "HARNESS": r"E:\IMPERIUM_HARNESS",
}


def _self_dir():
    return os.path.dirname(os.path.abspath(__file__))


_ZONE_DIRS = tuple("IMPERIUM_" + z for z in CANON)


def _auto_base():
    # Якоримся ТОЛЬКО на точных именах зон (IMPERIUM_REALITY|WARP|HARNESS),
    # чтобы папки вроде IMPERIUM_PORTABILITY_PACK НЕ принимались за базу.
    cur = _self_dir()
    while True:
        if os.path.basename(cur).upper() in _ZONE_DIRS:
            return os.path.dirname(cur)
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def _candidate_config_paths():
    paths = []
    if os.environ.get("IMPERIUM_ROOTS"):
        paths.append(os.environ["IMPERIUM_ROOTS"])
    paths.append(os.path.join(_self_dir(), CONFIG_NAME))
    if os.environ.get("ProgramData"):
        paths.append(os.path.join(os.environ["ProgramData"], "Imperium", CONFIG_NAME))
    paths.append("/etc/imperium/" + CONFIG_NAME)
    cur = os.path.abspath(os.getcwd())
    while True:
        paths.append(os.path.join(cur, ".imperium", "roots.json"))
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return paths


def _load_config():
    for p in _candidate_config_paths():
        try:
            if p and os.path.isfile(p):
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    continue
                aliases = data.get("aliases", {}) or {}
                norm = {str(k).upper(): str(v) for k, v in aliases.items()}
                base = data.get("base")
                base = str(base) if base else None
                return norm, p, base
        except Exception:
            continue
    return {}, None, None


_CFG = None


def _config():
    global _CFG
    if _CFG is None:
        _CFG = _load_config()
    return _CFG


def resolve_base():
    _, _, cfg_base = _config()
    if cfg_base:
        return cfg_base, "config.base"
    if os.environ.get("IMPERIUM_HOME"):
        return os.environ["IMPERIUM_HOME"], "env:IMPERIUM_HOME"
    auto = _auto_base()
    if auto:
        return auto, "auto"
    drive = os.path.splitdrive(_self_dir())[0]
    return (drive + os.sep if drive else os.sep), "fallback"


def _subst(val, base):
    return val.replace("{BASE}", base).replace("{HOME}", base)


def _git_toplevel():
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             cwd=os.getcwd(), capture_output=True, text=True, timeout=5)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return None


def get_with_source(alias):
    a = str(alias).upper()
    env_key = "IMPERIUM_" + a
    if os.environ.get(env_key):
        return os.environ[env_key], "env:" + env_key
    cfg_map, cfg_path, _ = _config()
    base, base_src = resolve_base()
    if a in cfg_map:
        return _subst(cfg_map[a], base), "config|base=" + base_src
    if a in CANON and base_src != "fallback":
        return os.path.join(base, "IMPERIUM_" + a), "base:" + base_src
    if a == "REALITY":
        top = _git_toplevel()
        if top:
            return top, "git-toplevel"
    if a in CANON:
        return os.path.join(base, "IMPERIUM_" + a), "base:" + base_src
    if a in CANON_DEFAULTS:
        return CANON_DEFAULTS[a], "default"
    return None, None


def get(alias):
    v, _ = get_with_source(alias)
    if v is None:
        raise KeyError("Unknown imperium root alias: %s" % alias)
    return v


def known_aliases():
    cfg_map, _, _ = _config()
    names = set(CANON)
    names.update(cfg_map.keys())
    for k in os.environ:
        if k.startswith("IMPERIUM_") and k not in ("IMPERIUM_ROOTS", "IMPERIUM_HOME"):
            names.add(k[len("IMPERIUM_"):])
    return sorted(names)


def resolve(path):
    if path is None:
        return None
    s = str(path)
    if not s.startswith("@"):
        return s
    rest = s[1:]
    i = 0
    while i < len(rest) and rest[i] not in "/\\":
        i += 1
    alias = rest[:i]
    remainder = rest[i + 1:] if i < len(rest) else ""
    root = get(alias)
    if remainder == "":
        return root
    remainder = remainder.replace("/", os.sep).replace("\\", os.sep)
    return os.path.join(root, remainder)


def _cmd_show():
    cfg_map, cfg_path, _ = _config()
    base, base_src = resolve_base()
    print("schema_version:", SCHEMA_VERSION)
    print("config_file   :", cfg_path or "(none — ENV/auto)")
    print("base          : %s  [%s]" % (base, base_src))
    print("-" * 60)
    for a in known_aliases():
        v, src = get_with_source(a)
        print("  @%-10s = %-34s [%s]" % (a, v, src))
    return 0


def _cmd_get(a):
    print(get(a))
    return 0


def _cmd_resolve(p):
    print(resolve(p))
    return 0


def _cmd_doctor():
    rc = 0
    for a in known_aliases():
        v, src = get_with_source(a)
        ok = os.path.isdir(v) if v else False
        if not ok:
            rc = 2
        print("  [%s] @%-10s -> %s  [%s]" % ("OK " if ok else "MISS", a, v, src))
    print("VERDICT:", "ROOTS_DOCTOR_OK" if rc == 0 else "ROOTS_DOCTOR_WARN")
    return rc


def main(argv):
    if len(argv) < 2:
        print("usage: imperium_roots.py {show|get <ALIAS>|resolve <@ALIAS/path>|doctor|base}", file=sys.stderr)
        return 1
    cmd = argv[1]
    try:
        if cmd == "show":
            return _cmd_show()
        if cmd == "base":
            b, s = resolve_base()
            print("%s  [%s]" % (b, s))
            return 0
        if cmd == "get" and len(argv) >= 3:
            return _cmd_get(argv[2])
        if cmd == "resolve" and len(argv) >= 3:
            return _cmd_resolve(argv[2])
        if cmd == "doctor":
            return _cmd_doctor()
    except KeyError as e:
        print("ERROR:", e, file=sys.stderr)
        return 2
    print("bad usage", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
