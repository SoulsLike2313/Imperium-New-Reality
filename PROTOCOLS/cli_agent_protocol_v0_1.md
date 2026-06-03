# CLI Agent Protocol V0.1

Commands:
- `agent status --agent <AGENT_ID>`
- `ask --agent <AGENT_ID> --question <question_json_path>`
- `route --task <task_json_path>`

Behavior rules:
- deterministic file-based output
- no network dependency
- every ask/route emits answer JSON + receipt JSON
