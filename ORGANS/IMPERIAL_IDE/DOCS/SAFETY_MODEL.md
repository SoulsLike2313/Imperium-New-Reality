# Control Shell Safety Model

## Allowed

- read active governance;
- read Astronomicon task registry and admitted taskpacks;
- read reports and receipts;
- read Mechanicus registries and command policy;
- validate JSON;
- emit dry-run tool invocation receipts.

## Blocked

- arbitrary shell execution;
- real tool execution without future allowlist and receipt policy;
- VM2 or VM3 routing;
- destructive cleanup;
- task registry mutation;
- staging secrets or local route configs;
- extensions with unrestricted execution permission.

Every CLI command returns a structured receipt. Runtime command history is intentionally not appended to tracked files.
