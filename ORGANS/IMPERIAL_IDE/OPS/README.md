# Imperial IDE OPS

OPS is the dry-run operational task console for Imperial IDE.

It provides:

- Task intent classification and validation.
- Astronomicon-compatible taskpack generation.
- Dry-run Astronomicon registration under ORGANS/IMPERIAL_IDE/OPS/STAGING/.
- Launch card rendering.
- Full lifecycle dry-run with anti-fake-green checks.
- Git closure status without pushing.

Real servitor execution, unrestricted shell execution, and live LLM backend are disabled.

## Commands

- Smoke: python ORGANS\IMPERIAL_IDE\OPS\CLI\imperial_ide_ops_cli.py smoke
- TUI smoke: python ORGANS\IMPERIAL_IDE\OPS\TUI\imperial_ide_ops_tui.py --smoke
- Shell smoke: python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py ops-smoke
- Build taskpack: python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py build-taskpack
- Register dry-run: python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py register-taskpack
- Launch card: python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py launch-card
- Lifecycle smoke: python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py lifecycle-smoke

Direct builder example:

python ORGANS\IMPERIAL_IDE\OPS\CLI\imperial_ide_ops_cli.py build-taskpack --title "Example integration task" --goal "Build an Astronomicon-compatible taskpack from OPS" --type integration --scope IMPERIAL_IDE --risk CONTROLLED_WRITE --push VALIDATED_PUSH

## Safety

Validated push is allowed and expected after validation, scope check, secret check, and task policy.

OPS does not perform live registration unless the controlled live gate is explicitly enabled in a future task. Current registration writes only dry-run mirrors under OPS/STAGING.
