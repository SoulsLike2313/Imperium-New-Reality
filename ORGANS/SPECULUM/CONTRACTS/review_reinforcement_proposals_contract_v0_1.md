# Review Reinforcement Proposals Contract V0.1

Status: CANDIDATE_V0_1
Owner organ: SPECULUM

## Purpose

Every Speculum architecture review must return exactly three reinforcement proposals tied to practical follow-up action.

## Required Proposal Set

Each review must produce exactly one proposal of each type:

1. skill_api_tool_candidate
2. matrix_gate_improvement
3. cost_context_output_optimization

## Required Fields

Each proposal must include:

- proposal_id
- type
- why_now
- first_use_case
- risk
- admission_mode

## Architecture Guard

Speculum proposals must preserve root scope, evidence boundaries, and the current canon/candidate distinction. Architecture recommendations do not grant install permission by themselves.

## Verdict Rule

A Speculum review is incomplete if it lacks exactly three reinforcement proposals or if two proposals use the same type.

