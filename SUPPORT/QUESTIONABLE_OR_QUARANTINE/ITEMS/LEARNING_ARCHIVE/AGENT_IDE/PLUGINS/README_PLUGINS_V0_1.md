# Plugin-ready descriptors (V0.1)

V0.1 is plugin-ready by descriptors only.

Allowed:

- JSON schema for provider descriptors.
- Built-in readonly provider registry file.
- Data loader extension via trusted descriptor entries.

Forbidden in V0.1:

- Dynamic import/execution of untrusted plugin code.
- Shell/command execution through plugins.
- File mutation through plugins.
- Network calls from plugins.

Future plugin direction:

- Route provider.
- File Atlas provider.
- Officio rule surface provider.
- Inquisition problem provider.
- Report/receipt provider.
- WARP bridge provider (later task).
