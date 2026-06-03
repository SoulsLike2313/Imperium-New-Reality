# Administratum File Atlas V0.1

Task: `TASK-NEWGEN-ADMINISTRATUM-FILE-ATLAS-PASSPORT-INDEX-VM3-V0_1`

This folder provides read-only machine-readable file visibility for five NewGen organs:
- MECHANICUS
- OFFICIO_AGENTIS
- ADMINISTRATUM
- INQUISITION
- ASTRONOMICON

Core outputs:
- `file_passport_schema_v0_1.json`
- `file_passports_v0_1.jsonl`
- `file_atlas_index_v0_1.json`
- organ/surface indexes for role/rule/language/tool/TUI/report/route/pain/gap

Use:
```bash
python3 IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TUI/administratum_file_atlas_tui_v0_1.py --lang en
```

Notes:
- This is indexing and visibility only.
- No IDE/WARP/CLI Worker implementation is included.
- Officio/Inquisition hardening is intentionally not performed in this task.
