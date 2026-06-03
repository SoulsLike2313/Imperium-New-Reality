# Owner Quickstart V0.1

## Goal
- Build and verify a compact dossier ZIP that includes machine evidence plus Owner-facing Russian PDF.

## Minimal flow
1. Detect environment and OSS availability:
```powershell
python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color doctor-oss
```
2. Build dossier:
```powershell
python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color build-dossier --task-id TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1
```
3. Verify dossier:
```powershell
python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color verify-dossier --latest
```

## What to check
- `MANIFEST.json` exists in dossier root.
- `SHA256SUMS.txt` exists and verifies.
- `machine/` JSON files exist.
- `reports_en/` canonical English reports exist.
- `owner_ru/OWNER_DOSSIER_RU.pdf` exists.
- If PDF is missing, fallback file exists and verdict is `WARN`.

## Rules
- Do not treat PDF as sole truth source.
- Canonical truth remains markdown reports and JSON receipt.
- Do not auto-install dependencies from inside these commands.

