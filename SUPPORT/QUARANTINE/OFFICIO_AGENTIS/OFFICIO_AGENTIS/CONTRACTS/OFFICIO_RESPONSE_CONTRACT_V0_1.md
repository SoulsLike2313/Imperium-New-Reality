# OFFICIO RESPONSE CONTRACT V0.1

## Purpose

Define reusable Owner-facing response shape for Officio-governed tasks.

## Owner-facing language

- Live progress: Russian.
- Final response: Russian.
- Technical machine artifacts: English-safe.

## Required final response shape

Owner-facing final response uses exactly 4 numbered parts:

1. Step name.
2. Full path to primary report/bundle.
3. Verdict.
4. 3-4 short Russian owner comments.

## Required quality clauses

- Do not claim PASS without evidence paths.
- Do not claim full system readiness beyond scoped outputs.
- Declare not-run critical checks explicitly.
- If language drift happened, include correction note.

## Violation handling

- Missing 4-part shape: `FAIL`.
- Missing RU owner summary: `FAIL`.
- Minor formatting mismatch with evidence intact: `WARN`.
