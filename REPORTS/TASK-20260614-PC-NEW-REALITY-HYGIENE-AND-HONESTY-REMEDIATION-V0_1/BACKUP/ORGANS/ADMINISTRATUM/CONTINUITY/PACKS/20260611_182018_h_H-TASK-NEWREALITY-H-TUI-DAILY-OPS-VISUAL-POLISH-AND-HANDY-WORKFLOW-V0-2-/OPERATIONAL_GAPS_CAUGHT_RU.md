# OPERATIONAL GAPS CAUGHT RU

Этот файл фиксирует провал старого handoff, чтобы он не повторялся.

## Что пошло плохо

- Новый Logos Prime прочитал main repo_root и дал команды применения patch ZIP в main.
- H-contour path не был явно поднят как hard rule.
- Команды предполагали, что ZIP уже лежит в repo root, что вызвало Expand-Archive path error.
- Smoke был запущен на старом launcher, поэтому мог создать ложное ощущение прогресса.
- Следующий task был выбран слишком рано, до фикса continuity полноты.

## Исправление v0.3

- Manifest содержит contours/main/H и h_workflow_rule.
- H protocol и boot checklist включаются в pack как owner-visible документы.
- Next commands разделяют H apply и main acceptance flow.
- Launcher показывает H/main awareness и continuity completeness gates.
