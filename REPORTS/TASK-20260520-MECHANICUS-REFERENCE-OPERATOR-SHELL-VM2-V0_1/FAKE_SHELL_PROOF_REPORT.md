# FAKE SHELL PROOF REPORT

- task_id: `TASK-20260520-MECHANICUS-REFERENCE-OPERATOR-SHELL-VM2-V0_1`
- inferred_visual_status: `PASS_RICH_OPERATOR_SHELL`

## Proof Matrix
| Check | Result |
|---|---|
| layout_labels_present_all_transcripts | PASS |
| rich_or_plain_layout_visible | PASS |
| tool_registry_connected | PASS |
| identity_mission_visible | PASS |
| backend_truth_visible | PASS |
| command_palette_visible | PASS |
| five_shell_once_transcripts_present | PASS |
| no_unknown_visual_status_tokens | PASS |

## Why This Is Not Fake Shell
- Shell transcripts contain structured operator layout sections (top/left/right/bottom).
- `tools` transcript includes live tool registry payload with registry path and availability fields.
- `status` transcript includes backend truth (HEAD/branch/dirty state).
- `identity` transcript includes Mechanicus mission string.
- Renderer diagnostic is produced as a machine-readable artifact.
