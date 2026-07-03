# TESTS — ORGAN-MATURITY-GATES-CANON-0001

The runner lands the canon files and executes:

```powershell
python ORGANS\DOCTRINARIUM\VALIDATORS\validate_organ_maturity_gates_canon.py --repo-root . --apply
python ORGANS\CUSTODES\VALIDATORS\validate_organ_maturity_prosecutor_matrix.py --repo-root . --apply
python ORGANS\THRONE\VALIDATORS\validate_organ_maturity_crown_gate_matrix.py --repo-root . --apply
```

The patch passes only if:

- the Doctrinarium law exists and contains the six gates;
- the schema contains exactly six canonical gates in order;
- every gate has evidence classes;
- the score matrix covers all gates;
- Custodes receives prosecutor questions and blocking findings for every gate;
- Throne receives crown laws blocking local-to-global fake readiness.
