# Receipts Contract

Every operation creates a receipt JSON with:

- task id or command id
- UTC timestamp
- command name
- input args
- output artifact paths
- verdict (`PASS|WARN|BLOCKED|FAIL`)
- notes

Receipts are evidence for gate and requirement status.

