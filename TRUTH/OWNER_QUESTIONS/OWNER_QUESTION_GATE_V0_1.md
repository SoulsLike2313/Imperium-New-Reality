# OWNER QUESTION GATE V0.1

## Purpose

Owner questions must be file-backed, inspectable, and visible in Sanctum NG as bounded truth objects.
This gate defines a foundation-only model for registration, status semantics, priority semantics,
and read-only visualization of Owner-required decisions.

## Scope

This gate covers:
- question registration records;
- status and priority rules;
- evidence references and next required action;
- generated read-only state for Sanctum NG.

This gate does not cover:
- live Owner chat;
- answer submission backend;
- autonomous decision inference;
- production notification or escalation channels.

## Core Invariants

1. `FOUNDATION_ONLY` means no production or autonomy claim.
2. `NO_LIVE_OWNER_CHANNEL` means UI cannot submit answers.
3. `NO_EVIDENCE_NO_STRICT_PROMOTION` means visual green cannot be promoted without evidence.
4. `BLOCKING_OWNER_DECISION_REQUIRED` means action progression is blocked until explicit Owner decision.

## Required Question Shape

Every question record must include:
- `question_id`, `task_id`, `source`, `source_ref`;
- `question_text_ru`, `why_needed_ru`;
- `decision_type`, `blocking_level`, `status`;
- `owner_answer_required`, `allowed_answers`, `evidence_refs`;
- `created_at_utc`, `updated_at_utc`.

## Status Semantics

Primary statuses:
- `OPEN`
- `ANSWERED`
- `DEFERRED`
- `CANCELLED`
- `STALE`
- `FOUNDATION_SAMPLE`

Derived gate statuses:
- `BLOCKING_OWNER_DECISION_REQUIRED`
- `WARN_OWNER_REVIEW_RECOMMENDED`

## Boundary Statement

Sanctum NG Owner Question Gate V0.1 is read-only and foundation-only.
No live Owner interaction channel is claimed.
