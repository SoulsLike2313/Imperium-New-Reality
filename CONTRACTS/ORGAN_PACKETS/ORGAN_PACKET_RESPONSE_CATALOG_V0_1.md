# ORGAN PACKET RESPONSE CATALOG V0.1

## Purpose
This catalog defines expected packet intent per in-scope organ for `ORGAN_PACKET_V0_1`.

## Universal packet constraints
- `schema_version`: `0.1`
- `task_id`: bound to one task
- `live_status`: must be explicit
- `confidence`: must use controlled enum
- `proof`: basis paths, basis commands, limitations are mandatory

## Organ response focus

### ASTRONOMICON
- stage map and decomposition guidance
- bounded sequencing advice
- inter-organ question routing suggestions

### OFFICIO_AGENTIS
- role/mode pointer requirements
- response contract and language constraints
- required ack/status gates before execution

### DOCTRINARIUM
- gate and law references
- no-fake-green guard clauses
- stop-condition enforcement flags

### ADMINISTRATUM
- required report and receipt paths
- evidence packaging and chronology expectations
- change log and handoff bundle requirements

### MECHANICUS
- required validators and tools
- capability and dependency warnings
- script maturity classification requirements

### INQUISITION
- contradiction and risk alerts
- fake certainty detection hints
- forbidden assumption checks

### STRATEGIUM
- priority sequencing
- tradeoff articulation
- continue/stop decision contour

### SCHOLA_IMPERIALIS
- skill prerequisites
- training or context gaps
- recommended examples and known pitfalls

## Example-only status policy for this task
For `TASK-20260521-NEWGEN-ORGAN-PACKET-CONTRACT-PC-V0_1`, packet set outputs are contract examples only.
Allowed stance:
- `set_live_status`: `EXAMPLE_ONLY` or `NOT_IMPLEMENTED`
- per-packet `live_status`: `EXAMPLE_ONLY` or `NOT_IMPLEMENTED`

Not allowed in this task:
- claiming runtime organ communication as live
- using `LIVE` without executable evidence and receipts

