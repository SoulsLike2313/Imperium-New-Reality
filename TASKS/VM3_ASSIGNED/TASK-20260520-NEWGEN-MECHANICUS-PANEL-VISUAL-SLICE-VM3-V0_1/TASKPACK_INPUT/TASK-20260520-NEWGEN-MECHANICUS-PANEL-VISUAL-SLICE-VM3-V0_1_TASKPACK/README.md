# TASKPACK README

Task ID: `TASK-20260520-NEWGEN-MECHANICUS-PANEL-VISUAL-SLICE-VM3-V0_1`

## Mission

After V0.2R topology hardening, the next allowed step is **one concrete visual unit implementation** through the hardened topology, not a whole frontend rewrite.

This task is the first visual implementation slice:
- subject: `SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL`
- mode: isolated lab inside `IMPERIUM_NEW_GENERATION`
- goal: prove the visual production method can turn topology + owner visual contract + reference assets into a strong, non-generic, reviewable UI slice.

## Why this task

The Owner's main pain is frontend quality and speed. The repo now has hardened topology/registry/truth-map/validator, but still lacks a proven **visual foundry workflow** for one real panel.

This task therefore focuses on:
1. one slice only;
2. strong asset grounding;
3. anti-generic form;
4. truth-safe states;
5. before/after screenshot evidence;
6. minimal blast radius.

## Baseline inputs

Use the recent topology hardening line as baseline:
- `971ed8f80721ddfda82597a4e1cb9aa572fbd5e2`
- `6ca53f6e1f845ea97a6fd9c5dabaa5ed64323d1a`
- `6a87da4e1ead4a20f750fe911428b913b082b2b9`
- `da0a04d39a747dc1ca09bf791e149e10ab511f92`

## This task is not

- not a whole Sanctum rewrite;
- not all 10 organs;
- not a CSS-only polish pass;
- not a concept board;
- not a merge of main/test;
- not a fake-green visual demo.
