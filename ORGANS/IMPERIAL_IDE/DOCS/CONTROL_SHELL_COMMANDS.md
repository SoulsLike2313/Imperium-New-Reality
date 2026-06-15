# Control Shell Commands

- `doctor`: validate shell, governance, Mechanicus bridge, extensions, and workspace.
- `status`: show git, governance, and current task status.
- `dashboard`: aggregate core panel summaries.
- `tasks`: list registered Astronomicon tasks.
- `current-task`: show current expected task.
- `reports`: list latest report directories.
- `latest-report`: show the most recently modified report directory.
- `receipts`: list receipt JSON files.
- `tools`: list Mechanicus tool records.
- `capabilities`: list Mechanicus capability records.
- `policy`: show command policy and unsafe-shell state.
- `extensions`: validate extension registry and example extension.
- `workspace`: validate workspace state.
- `validate`: parse shell and Mechanicus model JSON.
- `dry-run-tool <tool_id>`: emit a dry-run receipt without execution.
- `help`: show the command palette.

Unknown or unregistered tool IDs return structured `BLOCKED` status.
