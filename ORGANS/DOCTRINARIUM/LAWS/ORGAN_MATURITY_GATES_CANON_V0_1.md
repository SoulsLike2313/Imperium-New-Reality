# ORGAN MATURITY GATES CANON V0.1

law_id: `ORGAN_MATURITY_GATES_CANON_V0_1`  
status: `CANON_DRAFT`  
owner: `DOCTRINARIUM`  
applies_to: `ALL_ORGANS`  
reference_implementation: `ASTRONOMICON`  
patch_id: `ORGAN-MATURITY-GATES-CANON-0001`

## Prime Law

Organs differ by profile, voice, duties, tools and domain of attention.

Organs do not differ by maturity form.

Every organ of Imperium must be readable through the same six maturity gates. A young organ may stand at a low gate. A strong organ may stand near full local crown confirmation. But no organ may hide its maturity state, borrow trust from another organ, or claim global readiness from local success.

```text
The organ does not need to be complete to exist.
The organ must be honest about what level it has actually proven.
```

## Why this law exists

Imperium is not a loose pile of scripts. It is a MetaOS-forming system of organs, validators, receipts, reports, app surfaces, agentic work and future game projection.

Without a shared maturity form, every organ becomes a private exception. Custodes would need custom accusations for every organ. Throne would need custom crown logic for every organ. Operator UI would become a museum of special cases. Core v1 would not have a repeatable way to know which organs are real, which are described, which are operational, which are externally trusted, and which are merely myth.

This law gives the Great Nine and all supporting organs a common measurement spine.

## Six Gates

### Gate 1 — Identity & Jurisdiction

The organ must know who it is and where its authority begins and ends.

Required proof class:

- `organ_id`
- profile / passport
- purpose
- jurisdiction
- explicit non-jurisdiction
- owner / supervising contour
- relation to Great Nine / Crown / supporting organs

Value:

This prevents the organ from becoming an anonymous folder or claiming another organ's territory.

### Gate 2 — Contract & Evidence

The organ must bind its promises to evidence.

Required proof class:

- duty contract
- claimed capabilities
- not-claimed boundaries
- forbidden claims
- external dependency claims
- evidence map
- file ownership / anatomy

Value:

This converts "the organ says" into "the organ can show". Claims without evidence remain drafts.

### Gate 3 — Operational Surface

The organ must expose usable actions without hiding work.

Required proof class:

- CLI / TUI / app / API action surface
- safe invocation commands
- aquarium logs
- receipts
- reports
- self-validators
- no hidden destructive execution

Value:

This makes the organ usable and observable. A hidden organ cannot be trusted as an operator tool.

### Gate 4 — Advisory & Hardening

The organ must become useful without becoming sovereign.

Required proof class:

- advisory scoring
- risk scoring
- Red Team layer
- Blue Team layer
- hardening synthesis
- warnings / known limitations
- no command authority without Owner/workflow gate

Value:

This lets organs recommend next steps, expose risks and improve resilience without stealing authority from Owner, Custodes or Throne.

### Gate 5 — External Trust

The organ must be judged from outside itself.

Required proof class:

- Custodes prosecution matrix
- Custodes validator pass
- indictment handling
- Throne crown gate matrix
- Throne validator pass
- anti-self-validation proof
- local crown is not global assembled

Value:

This forbids self-trust. An organ may produce evidence; it cannot crown itself.

### Gate 6 — Integration & Maturity Loop

The organ must enter the wider Imperium without freezing into false completion.

Required proof class:

- stage-score integration
- app/operator integration
- event ledger compatibility
- maturity loop
- regression checks
- future-gate path
- local proof does not mutate global core readiness without separate law

Value:

This turns a proven organ into a repeatable, inspectable, upgradable part of the MetaOS.

## Gate Compression Rule

The six gates are not six manual rituals for every patch.

They are the maturity model of an organ.

Small patch work should use the local patch lifecycle. Organ formation and organ upgrade work should update the gate evidence map. Validators read the gate state and decide whether a claim is supported.

## Evidence Law

No score may be granted without evidence.

Accepted evidence types:

- canonical document
- schema
- matrix
- validator output
- receipt
- report
- runtime proof
- test output
- artifact manifest
- app action parity proof
- external review / Owner waiver when explicitly marked

Forbidden evidence types:

- prose-only confidence
- "the model said"
- visual green without receipt
- local pass presented as global assembled
- self-validation presented as external trust

## Score Law

Gate score is advisory unless bound to evidence.

A gate may be:

- `0` — absent
- `1` — drafted
- `2` — evidence-bound
- `3` — operational
- `4` — externally checked
- `5` — locally crown-confirmed

The score is not a decoration. Each point must map to an evidence path.

## Core v1 Relation

Core v1 is not achieved by declaring all gates complete.

Core v1 becomes plausible when the system can repeatedly do this:

```text
task enters
scope is fixed
organ is selected
power is bounded
action runs in controlled surface
aquarium shows work
evidence is written
validators judge
Custodes prosecutes
Throne prevents fake-green
score updates
result can be delivered
```

The six gates are the organ-side structure that makes this chain repeatable.

## Game Projection Law

Future game projection may render gate state as locations, powers, bosses, rewards, corruption, proof XP and crown favor.

But the game layer may not claim truth.

```text
Game layer renders truth.
Core evidence proves truth.
```

No XP without evidence. No boss defeated without validator receipt. No new power without capability proof.

## Not Claimed

This canon does not claim:

- all Great Nine organs are assembled;
- Core v1 is ready;
- Throne is globally complete;
- game projection exists;
- external market workflow is complete;
- organ scores are perfect.

It only defines the shared form by which organs are to be built, measured, accused, crowned and integrated.
