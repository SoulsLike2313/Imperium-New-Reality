# OPS Task Console: краткая инструкция

OPS нужен, чтобы создавать задачи изнутри Imperial IDE: intent -> taskpack -> dry-run registration -> launch card -> lifecycle -> closure.

Команды общего shell:

- python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py ops
- python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py task-console
- python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py build-taskpack
- python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py register-taskpack
- python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py launch-card
- python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py lifecycle-smoke
- python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py git-closure

Прямой TUI:

python ORGANS\IMPERIAL_IDE\OPS\TUI\imperial_ide_ops_tui.py

Ограничения: real servitor execution выключен, unsafe shell выключен, live LLM backend выключен. Live registration остаётся gated.
