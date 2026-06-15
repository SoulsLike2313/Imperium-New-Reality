# Astronomicon Taskpack Registration Skill Contract

## Name

Astronomicon Taskpack Registration Skill.

## Owner

ASTRONOMICON.

## Purpose

Register taskpack ZIP files through an operator-friendly Skill while preserving Astronomicon as the truth source.

## Required callable modes

- Interactive text TUI or menu-driven CLI.
- Direct command mode with flags if easy and safe.

## Required commands or menu actions

- Select taskpack ZIP.
- Detect TASK_ID from root MANIFEST.json.
- Select contour: PC, VM3, VM2.
- Run preflight.
- Register on target contour.
- Resolve TASK_ID.
- Show launch card.
- Write receipt.

## Truth source

The Skill must call existing Astronomicon intake/resolver tools. It must not duplicate registry truth or let IDE mutate registry directly.

## Later IDE bridge

The Skill must expose a simple backend contract so IDE can call it later. This task does not need to implement the IDE UI.
