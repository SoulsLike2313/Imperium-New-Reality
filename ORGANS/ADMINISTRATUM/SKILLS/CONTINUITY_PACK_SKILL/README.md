# Administratum Continuity Pack Skill

Owner organ: `ADMINISTRATUM`  
Primary term: `Skill`  
Version: `0.1.0`

## Purpose

Build a controlled continuity pack for Logos-Prime/new-chat handoff without full-repo dumps, private-data leakage, or fake-clean PASS claims.

## Entrypoint

```powershell
python IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/SKILLS/CONTINUITY_PACK_SKILL/administratum_continuity_pack_skill_v0_1.py --repo-root .
```

Optional task id override:

```powershell
python IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/SKILLS/CONTINUITY_PACK_SKILL/administratum_continuity_pack_skill_v0_1.py --repo-root . --task-id TASK-NEWGEN-ADMINISTRATUM-CONTINUITY-PACK-SKILL-AND-LOGOS-HANDOFF-BRIDGE-PC-V0_1
```

## Output root

Default output bundle path:

`IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/REPORTS/<TASK_ID>/`

## Guarantees

- Produces machine-readable truth snapshots, caps, and task-chain context.
- Produces RU Owner-facing handoff and EN machine handoff.
- Produces SHA256 + ZIP receipts and validation receipts.
- Keeps clean PASS blocked when global Stage1/IDE/WARP caps are active.
- Supports recipient-target separation (`LOGOS_PRIME`, `INQUISITOR`, `SPECULUM`) through role-pack bridge artifacts without mutating core continuity truth.
