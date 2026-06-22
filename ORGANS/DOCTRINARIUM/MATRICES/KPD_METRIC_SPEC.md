# KPD_METRIC_SPEC

```yaml
task_id:        DOCTR-TOOLS-0001
matrix_id:      DOCTR.MATRIX.KPD_METRIC.v1_0
version:        1.0.0
lineage:        master 59159278802dc37da1386ca7451eadd8b96f6f06
authored_by:    NOTION_OPUS (CHAT / Opus 4.5)
target_organ:   DOCTRINARIUM
schema_version: imperium.matrix.v0_1
echolon:        1
status:         DOCTRINAL (alpha v0_1; STRATEGIUM will operationalize)
```

## §0 Doctrinal vs operational

This matrix is the DOCTRINAL specification of the KPD metric: what is
measured, how it is combined, and what counts as a victory. The OPERATIONAL
side (per-pack measurement, baseline collection, dashboard) is owned by
STRATEGIUM via a later `STRATEGIUM-KPD-0001` pack.

DOCTRINARIUM defines the formula; STRATEGIUM applies it.

## §1 What KPD measures

KPD ("Korrelyatsia Produktivnosti Doktriny" / "Doctrine Productivity
Coefficient") is a single scalar measuring how effectively the Imperium
produces canonical work compared to a freeform baseline.

KPD is computed per WINDOW (default: rolling 30 days) and per AGGREGATE
(per organ, per actor, whole-Imperium).

## §2 Component metrics

| Symbol | Name                              | Direction   | Description                                                            |
|--------|-----------------------------------|-------------|------------------------------------------------------------------------|
| FTP    | First-Time Pass                   | higher better | Fraction of packs that landed without a repair build.                |
| FGCR   | Fake-Green Containment Rate       | higher better | Fraction of fake-green attempts caught before land.                  |
| TTT    | Time-To-Token                     | lower better  | Median wall-clock hours from intake to land per pack.                 |
| RI     | Receipt Integrity                 | higher better | Fraction of landed packs with complete CANONICAL_PIPELINE chain.     |
| KPE    | Kernel-Pollution Events           | lower better  | Count of kernel writes without EMPEROR_SEAL (OWNER_MANUAL bypass OK). |
| RC     | Refusal Correctness               | higher better | Fraction of charter refusals upheld by later audit (no false refuse).|

Each metric is normalized to [0, 1] in the formula.

## §3 Combination formula

```
KPD = w_FTP  * norm(FTP)
    + w_FGCR * norm(FGCR)
    + w_TTT  * (1 - norm(TTT))      # TTT is lower-better; invert
    + w_RI   * norm(RI)
    + w_KPE  * (1 - norm(KPE))      # KPE is lower-better; invert
    + w_RC   * norm(RC)

where weights sum to 1.0:

  w_FTP  = 0.25
  w_FGCR = 0.25
  w_TTT  = 0.15
  w_RI   = 0.20
  w_KPE  = 0.10
  w_RC   = 0.05
```

Normalization for higher-better metrics: linear to baseline_max.
Normalization for lower-better metrics: linear to baseline_min, then inverted
in the formula.

## §4 Baselines

- **Baseline window**: rolling 30 days BEFORE charter-era (pre-DOCTR-CHARTER
  era packs serve as the comparison set). When pre-charter data is too thin,
  the baseline is synthesized from packs 1 through N where N >= 20.
- **Baseline expectation**: KPD_baseline ~ 0.4 to 0.5 (mid-range).
- **Victory threshold**: KPD_imperium >= 2.0 * KPD_baseline sustained over
  the rolling window.

## §5 Per-organ KPD

Each of the canonical 9 organs MAY have its own KPD computation with the
same formula but filtered to packs where `target_organ == <organ>`. The
per-organ KPDs are not weighted into the whole-Imperium KPD; they exist for
organ-level performance review.

## §6 Per-actor KPD

Each BOUND actor in ROLE_REGISTRY MAY have its own KPD computed over packs
where `authored_by == <actor>` (LOGOS_PRIME), `executed_by == <actor>`
(SERVITOR_PRIME), or `audited_by == <actor>` (SPECULUM). Per-actor KPD
decomposition is informational only.

## §7 Anti-gaming clauses

- A pack landed in OWNER_MANUAL sovereign bypass counts toward FTP only if
  the bypass is declared in the pack manifest BEFORE land.
- FGCR counts only attempts caught by INQUISITION tools, not attempts
  caught by reviewer prose.
- TTT is measured intake-receipt to land-receipt only; chat thread time
  outside the pipeline does not count.
- KPE counts each kernel-touching commit independently; squashed kernel
  writes do not collapse to one event for KPE accounting.

## §8 Forbidden gaming patterns

- Splitting a single logical change into N packs to inflate FTP.
- Inserting a no-op receipt to extend RI artificially.
- Refusing trivial packs at charter to lower TTT denominator.
- Marking pack as bypass post-hoc to dodge KPE.

These patterns are flagged by STRATEGIUM-KPD-0001 when active.

## §9 Reporting schedule

When STRATEGIUM-KPD-0001 lands, KPD is computed and emitted:

- After each pack land (per-pack delta).
- Weekly aggregate (rolling 7d).
- Monthly aggregate (rolling 30d, primary reporting window).

## §10 Amendment

Amendment to weights (§3) or victory threshold (§4) requires CANONICAL_PIPELINE
charter-admission + STRATEGIUM countersign (when active). Until STRATEGIUM-KPD
lands, OWNER_MANUAL bypass is the effective amendment authority.

## §11 Provenance

```
matrix_id:     DOCTR.MATRIX.KPD_METRIC.v1_0
base_sha:      59159278802dc37da1386ca7451eadd8b96f6f06
authored_at:   captured at pack build (see meta/PROVENANCE.json)
identity_sig:  see meta/PROVENANCE.json
```

*End of KPD_METRIC_SPEC v1.0.0.*
