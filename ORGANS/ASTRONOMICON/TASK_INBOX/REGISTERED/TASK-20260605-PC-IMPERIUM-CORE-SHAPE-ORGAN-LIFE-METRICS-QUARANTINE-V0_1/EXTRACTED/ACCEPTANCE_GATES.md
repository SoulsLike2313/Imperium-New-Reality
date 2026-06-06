# ACCEPTANCE GATES

Task ID: `TASK-20260605-PC-IMPERIUM-CORE-SHAPE-ORGAN-LIFE-METRICS-QUARANTINE-V0_1`

## Admission gates

- The Servitor must start from Astronomicon registered task context.
- OFFICIO role entry must happen before implementation.
- Owner-facing final output must be Russian through OFFICIO authority.
- Machine artifacts must be ENGLISH UTF8 NO_BOM.

## Core shape gates

1. `ORGANS/_CORE_GOVERNANCE/` exists.
2. `SUPPORT/COMMON_IMPERIUM_SUPPORT/` exists.
3. `SUPPORT/QUESTIONABLE_OR_QUARANTINE/` exists.
4. `REQUIRED_9_ORGANS_V0_1.json` defines exactly 9 organs:
   - ADMINISTRATUM
   - ASTRONOMICON
   - CUSTODES
   - DOCTRINARIUM
   - INQUISITION
   - MECHANICUS
   - OFFICIO_AGENTIS
   - SCHOLA_IMPERIALIS
   - STRATEGIUM
5. Throne is explicitly future laptop-only scope and not part of the 9-organ core.

## Organ life gates

6. Organ life zone contract exists.
7. Organ card schema exists.
8. Organ life receipt schema exists.
9. Organ card template exists.
10. Organ life receipt template exists.
11. Custodes organ life audit matrix exists.

## Support and quarantine gates

12. Support zone contract exists.
13. Quarantine active-use ban contract exists.
14. Quarantine index exists.
15. Inquisition quarantine violation matrix exists.
16. Active use of quarantine is forbidden unless explicit salvage/admission receipt exists.

## Metrics and matrices gates

17. Metrics registry exists.
18. At least 7 metrics are defined:
    - organ self-sufficiency;
    - context locality;
    - script-first ratio;
    - servitor load reduction;
    - quarantine pressure;
    - learning capture rate;
    - known alert prevention.
19. Metrics are machine-readable JSON where applicable.
20. Matrices are machine-readable JSON where applicable.

## Administratum gates

21. Core address book contract exists.
22. Address book seed exists.
23. File ownership map seed exists.
24. Support zone map seed exists.
25. Unclassified files report exists.

## Tooling gates

26. `core_shape_self_checker_v0_1.py` exists and runs.
27. `core_file_classifier_dry_run_v0_1.py` exists and runs without moving or deleting files.
28. `organ_life_validator_v0_1.py` exists and runs.
29. Each tool writes or can print machine-readable JSON evidence.
30. Tool cards or Mechanicus registration evidence must be produced for new useful tools, or a clear reason must be recorded.

## Anti-chaos gates

31. No mass repository migration.
32. No deletion of legacy files.
33. No import path rewrite sweep.
34. No full cleanup claim.
35. No full semantic validation claim.
36. No active use of quarantine path as source of truth.
37. Unknown evidence is recorded as UNKNOWN_WITH_REASON.

## Bundle closure gates

38. Post-work bundle V0.2 closure is used.
39. 9-organ post-work receipt ring exists for this task.
40. Inquisition contradiction scan exists.
41. Custodes organ/matrix audit exists.
42. Schola aggressive learning receipt exists.
43. Strategium cost/KPD receipt exists.
44. Git closure receipt exists.
45. Remote closure proof exists or the self-reference boundary is explicitly recorded with post-push proof route.
46. Final owner summary is Russian.
47. Commit and normal non-force push are performed if accepted changes exist.
48. If any required gate cannot be met, the Servitor must create a repair request instead of claiming PASS.

## Definition of done

The task is accepted only if Imperium gains machine-checkable authority over core shape, organ life zones, support classification, quarantine ban, metrics/matrices, and dry-run cleanup planning without dangerous physical migration.
