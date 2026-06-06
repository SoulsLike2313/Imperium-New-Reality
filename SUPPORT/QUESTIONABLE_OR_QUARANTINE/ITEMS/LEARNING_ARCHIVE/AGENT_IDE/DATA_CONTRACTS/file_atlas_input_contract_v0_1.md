# File Atlas Input Contract V0.1

The read-only Agent IDE consumes Administratum File Atlas outputs.

## Required sources

- `file_passports_v0_1.jsonl` (required)
- `file_atlas_index_v0_1.json` (required)
- `organ_file_map_v0_1.json` (required)

## Optional but expected sources

- `role_rule_surface_index_v0_1.json`
- `language_gate_surface_index_v0_1.json`
- `tui_surface_index_v0_1.json`
- `checker_tool_index_v0_1.json`
- `report_receipt_index_v0_1.json`
- `route_connection_surface_index_v0_1.json`
- `owner_pain_to_file_map_v0_1.json`
- `gap_success_index_v0_1.json`

## Behavior on missing source

- Do not crash.
- Record warning in session warnings list.
- Keep panel visible with fallback message.
- Keep read-only guarantees.

## Parser policy

- `json` for index files.
- `jsonl` for file passports.
- UTF-8 decoding with strict error handling.
