# OPS: сначала запустить это

Статус: OPS подключён как dry-run Task Console. Реальное исполнение, live LLM и unsafe shell выключены.

Команды:

- python ORGANS\IMPERIAL_IDE\OPS\CLI\imperial_ide_ops_cli.py smoke
- python ORGANS\IMPERIAL_IDE\OPS\TUI\imperial_ide_ops_tui.py --smoke
- python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py ops-smoke

Открыть OPS CLI:

python ORGANS\IMPERIAL_IDE\OPS\CLI\imperial_ide_ops_cli.py --help

Открыть OPS TUI:

python ORGANS\IMPERIAL_IDE\OPS\TUI\imperial_ide_ops_tui.py

Собрать taskpack:

python ORGANS\IMPERIAL_IDE\OPS\CLI\imperial_ide_ops_cli.py build-taskpack --title "Example integration task" --goal "Build taskpack from OPS" --type integration --scope IMPERIAL_IDE --risk CONTROLLED_WRITE --push VALIDATED_PUSH

Зарегистрировать taskpack в dry-run:

python ORGANS\IMPERIAL_IDE\OPS\CLI\imperial_ide_ops_cli.py register --title "Example integration task" --goal "Build taskpack from OPS" --type integration --scope IMPERIAL_IDE --risk CONTROLLED_WRITE --push VALIDATED_PUSH

Показать launch card:

python ORGANS\IMPERIAL_IDE\OPS\CLI\imperial_ide_ops_cli.py launch-card --title "Example integration task" --goal "Build taskpack from OPS" --type integration --scope IMPERIAL_IDE --risk CONTROLLED_WRITE --push VALIDATED_PUSH

Запустить lifecycle dry-run:

python ORGANS\IMPERIAL_IDE\OPS\CLI\imperial_ide_ops_cli.py lifecycle --title "Example integration task" --goal "Build taskpack from OPS" --type integration --scope IMPERIAL_IDE --risk CONTROLLED_WRITE --push VALIDATED_PUSH

Live registration пока заблокирован gate. Validated push разрешён и ожидается только после validation, scope check, secret check и task policy.
