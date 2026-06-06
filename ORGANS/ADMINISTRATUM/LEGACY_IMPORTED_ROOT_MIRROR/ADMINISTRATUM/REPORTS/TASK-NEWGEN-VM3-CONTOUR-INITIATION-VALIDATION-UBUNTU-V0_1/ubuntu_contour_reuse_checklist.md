# Ubuntu Contour Reuse Checklist

Task baseline: `TASK-NEWGEN-VM3-CONTOUR-INITIATION-VALIDATION-UBUNTU-V0_1`

## Reuse Steps

1. Confirm direct taskpack delivery into VM inbox and record ZIP SHA256.
2. Obtain explicit `REQUIRED_HEAD` from Owner launch message.
3. Run git truth sync: fetch, checkout master, reset to REQUIRED_HEAD, verify local/origin equality.
4. Capture Ubuntu environment snapshot (`uname`, distro, shell, Python, Git).
5. Run NewGen Doctrinarium preflight before edits.
6. Run Officio boot ack generation before task outputs.
7. Probe Mechanicus tool capabilities without uncontrolled installs.
8. Create contour card, route receipt, sync receipt, officio settings, purity report.
9. Classify old Doctrinarium-first bootstrap references as `LEGACY_STALE_POLICY_REFERENCE` unless explicitly re-admitted.
10. Verify touched paths remain inside scoped report folder.
11. Produce compact final report in Russian with scoped verdict.

## Fast-Fail Triggers

- Missing REQUIRED_HEAD.
- Git truth mismatch after reset.
- Dirty start state not classified.
- Forbidden path mutation required.
- PASS claim without receipts.
