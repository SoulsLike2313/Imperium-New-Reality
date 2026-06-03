# Routing Body Contract V0.1

Route packet defines how Servitor should execute the task.

A valid route packet must include:
- primary organ and support organs;
- ordered execution phases;
- required receipts;
- stop conditions;
- explicit forbidden actions;
- not-proven boundary.

Routing laws:
- No organ route without task essence.
- No PASS route without receipt plan.
- No expansion into out-of-scope systems.
- Future WARP compatibility is template-only in this body.

Output target:
- machine-readable packet (`task_route_packet_schema_v0_1.json`);
- human-facing action plan inside task report.
