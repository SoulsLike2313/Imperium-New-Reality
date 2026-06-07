# Next GUI Workbench Build Plan

## Goal

Build a local GUI workbench over the proven control-shell APIs without bypassing Mechanicus.

## First Workbench Panels

1. Overview and current task.
2. Taskpack and route viewer.
3. Reports and receipts browser.
4. Mechanicus tools, capabilities, and policy.
5. Extension and workspace inspector.
6. Validation replay console.

## Constraints

- use the shell router as the initial backend contract;
- keep tool invocation dry-run first;
- do not add a background daemon without owner approval;
- do not claim full IDE completion from a workbench prototype.
