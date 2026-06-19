#!/usr/bin/env python3
"""IMPERIUM ROOTS — единый адаптивный резолвер зон по алиасам.
Алиасы: REALITY, WARP, HARNESS (+ любые из конфига).
Приоритет: ENV IMPERIUM_<ALIAS>  >  конфиг imperium.roots.json  >  встроенный дефолт.
Путь с префиксом @ALIAS разворачивается в реальный путь."""
import json
import os
import sys

SCHEMA_VERSION = "imperium.roots.v0_1"
CONFIG_NAME = "imperium.roots.json"
CANON_DEFAULTS = {
    "REALITY": r"E:\IMPERIUM_REALITY",
    "WARP": r"E:\IMPERIUM_WARP",
    "HARNESS": r"E:\IMPERIUM_HARNESS",
}


def _candidate_config_paths():
    paths = []
    env_file = os.environ.get("IMPERIUM_ROOTS")
    if env_file:
        paths.append(env_file)
    here = os.path.dirname(os.path.abspath(__file__))
    paths.append(os.path.join(here, CONFIG_NAME))
    progdata = os.environ.get("ProgramData")
    if progdata:
        paths.append(os.path.join(progdata, "Imperium", CONFIG_NAME))
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
                aliases = data.get("aliases", {}) if isinstance(data, dict) else {}
                norm = {str(k).upper(): str(v) for k, v in aliases.items()}
                return norm, p
        except Exception:
            continue
    return {}, None


_CONFIG_CACHE = None


def _config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is None:
        _CONFIG_CACHE = _load_config()
    return _CONFIG_CACHE


def get_with_source(alias):
    a = str(alias).upper()
    env_key = "IMPERIUM_" + a
    if os.environ.get(env_key):
        return os.environ[env_key], "env:" + env_key
    cfg, cfg_path = _config()
    if a in cfg:
        return cfg[a], "config:" + (cfg_path or "?")
    if a in CANON_DEFAULTS:
        return CANON_DEFAULTS[a], "default"
    return None, None


def get(alias):
    val, _ = get_with_source(alias)
    if val is None:
        raise KeyError("Unknown imperium root alias: %s" % alias)
    return val


def known_aliases():
    cfg, _ = _config()
    names = set(CANON_DEFAULTS.keys())
    names.update(cfg.keys())
    for k in os.environ:
        if k.startswith("IMPERIUM_") and k != "IMPERIUM_ROOTS":
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
    cfg, cfg_path = _config()
    print("schema_version:", SCHEMA_VERSION)
    print("config_file   :", cfg_path or "(none — ENV/defaults)")
    print("-" * 56)
    for a in known_aliases():
        val, src = get_with_source(a)
        print("  @%-10s = %-32s [%s]" % (a, val, src))
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
        val, src = get_with_source(a)
        ok = os.path.isdir(val) if val else False
        flag = "OK " if ok else "MISS"
        if not ok:
            rc = 2
        print("  [%s] @%-10s -> %s  [%s]" % (flag, a, val, src))
    print("VERDICT:", "ROOTS_DOCTOR_OK" if rc == 0 else "ROOTS_DOCTOR_WARN")
    return rc


def main(argv):
    if len(argv) < 2:
        print("usage: imperium_roots.py {show|get <ALIAS>|resolve <@ALIAS/path>|doctor}", file=sys.stderr)
        return 1
    cmd = argv[1]
    try:
        if cmd == "show":
            return _cmd_show()
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
