# Astronomicon Taskpack Registration Skill

Owner organ: `ASTRONOMICON`  
Primary term: `Skill`  
Version: `0.1.0`

## Purpose

Register taskpack ZIP files through an operator-friendly Skill while keeping Astronomicon intake/resolver as the only registry truth source.

## Entrypoints

Interactive:

```powershell
python ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/astronomicon_taskpack_registration_skill_v0_1.py --interactive
```

Direct command:

```powershell
python ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/astronomicon_taskpack_registration_skill_v0_1.py --zip-path C:\path\TASKPACK.zip --contour PC
```

## Contours

- `PC`: live local registration through Astronomicon intake + resolver.
- `VM3`: route-aware remote mode (live only when route config is present and `--live-remote` is provided).
- `VM2`: same behavior as VM3.

## Route Config

Copy and customize:

`contour_route_config.example.json` -> `contour_route_config.json`

Discovery order is explicit `--route-config`, `ASTRONOMICON_ROUTE_CONFIG`,
current-root `ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/contour_route_config.json`,
then old-prefix compatibility fallback with a warning. PC registration does not require route config.

If route config is missing or disabled, VM routes emit explicit `ROUTE_MISSING` receipts and do not claim live success.

## Launch Card

The Skill always emits launch-card evidence.  
For VM contours, if terminal opening is unavailable, a limitation receipt is produced and final verdict is downgraded.
