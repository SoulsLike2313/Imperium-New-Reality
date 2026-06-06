# Organ Life Zone Contract V0.1

Status: CANDIDATE_V0_1
Owner organ: CUSTODES
Support organs: ADMINISTRATUM, SCHOLA_IMPERIALIS, MECHANICUS

## Purpose

An organ life zone is the single durable home or mapped home for one organ's identity, memory, rules, metrics, matrices, schemas, templates, validators, receipts, post-work behavior, learning hooks, and self-checks.

## Minimum V0.1 Fields

Each required organ must be represented in REQUIRED_9_ORGANS_V0_1.json with:

- organ_id;
- root_path;
- life_zone_path;
- primary_duty.

The life zone path must exist. Missing sub-areas are warnings in V0.1 unless they prevent the organ from executing its assigned task duty.

## Non-Goals

V0.1 does not require physical migration of legacy organ files. It records the target and makes gaps visible.

## Receipt Rule

Any task that changes an organ life zone should emit an organ_life_receipt-compatible receipt or record UNKNOWN_WITH_REASON.
