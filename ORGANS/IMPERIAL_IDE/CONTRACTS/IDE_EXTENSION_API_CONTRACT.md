# IDE Extension API Contract

Extensions must declare permissions, tools, panels, commands, risks, receipts, and validation requirements before activation.

## Required Declarations

- `extension_id`
- `status`
- `permissions`
- `panels`
- `commands`
- `tools`
- `risks`
- `receipts`
- `validation`

Extensions start as `CANDIDATE` unless replay and receipts prove otherwise.
