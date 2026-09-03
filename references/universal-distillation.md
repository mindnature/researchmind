# Universal Scholar Distillation Protocol

This is the execution protocol for `$researchmind 蒸馏 <scholar>`.

## Phase 0 — Resolve the request

Extract scholar name, optional focus, requested depth (`quick|standard|deep|golden`, default `standard`), user-provided sources, and whether this is a new distillation or update. If identity is unambiguous, do not block on questions.

## Phase 1 — Start a transactional scholar job

For nontrivial work, prefer staging:

```bash
python scripts/researchmind.py stage-scholar "<canonical name>" --depth <depth> [--focus "..."]
```

The staged job lives under `.researchmind/staging/<job-id>/data/<slug>/` and contains a checkpoint. Do not treat staged data as canonical until validation and commit succeed.

## Phase 2 — Identity, grade and source reconnaissance

Populate `scholar_profile.json` after identity reconnaissance. Record:

- canonical identity and aliases;
- field, institutions and active period;
- major research programs and collaborators;
- likely archives;
- source availability;
- `source_availability_ceiling`;
- `distillation_grade`;
- `evidence_profile`.

Follow `source-discovery.md`. Build a source registry before deep synthesis. Distinguish sources that were merely discovered from sources actually inspected and sources that directly support claims.

## Phase 3 — Research-life map

Build a chronological map of major programs, papers/results, failures, reversals, disputes, method/theory shifts, collaborators, archive-rich periods and candidate decision Episodes. This map is navigation, not yet a heuristic list.

## Phase 4 — Candidate Episode selection and type gate

Rank candidate Episodes by decision visibility, evidence quality, contrast value and transfer potential.

Classify `episode_type`.

Research-heuristic eligible by default:

- `scientific_decision`
- `problem_framing`
- `method_choice`
- `anomaly_response`
- `theory_revision`

Not directly eligible for research heuristics:

- `career_decision`
- `research_program_strategy`
- `institution_building`
- `field_outcome`

Do not convert a field-level outcome or institutional decision into the scholar's micro-level research judgment just to create a counterexample.

## Phase 5 — Episode reconstruction

For every Episode:

1. define the research question at that historical moment;
2. enforce the Temporal Firewall;
3. separate known vs unknown at the time;
4. record only evidenced alternatives;
5. identify decision owners and team contributors;
6. state the observable research action;
7. record the result without leaking outcome knowledge backward;
8. list alternative historical interpretations;
9. assign evidence strength;
10. create primary-source blockers for unresolved claims.

## Phase 6 — Contrastive pairing

Search across Episodes for repeated decision structures. Pair success × failure, success × boundary case, early view × later reversal, or the same rule across different research programs. Do not force a pair merely to satisfy a format.

## Phase 7 — Candidate heuristic extraction

A candidate heuristic must contain decision structure, operational rule, actions, supporting Episodes, counter Episodes, boundary conditions, failure signals and evidence class.

Reject generic virtues such as curiosity, rigor, persistence, independent thinking or "ask important questions" unless converted into a discriminative operational program.

## Phase 8 — Scholar Specificity Gate

Follow `scholar-specificity.md` before calling a heuristic distinctive.

For every candidate ask:

1. Would a competent generic research advisor produce substantially the same rule?
2. Is the rule simply ResearchMind's own protocol rediscovered?
3. Is it only a target-domain review standard?
4. Does it recur in multiple scholar Episodes as an operational pattern?
5. What is the scholar-added delta?

Populate the heuristic `specificity` object. A `validated` heuristic must pass the gate.

## Phase 9 — Validation

Run:

### A. Within-person recurrence
Does the decision structure recur?

### B. Contrastive boundary
Does a failure/counter Episode specify when the rule breaks?

### C. Historical holdout
Hide the later part of an Episode and predict a useful next action without future leakage.

### D. Generic baseline A/B
Compare Generic ResearchMind vs Scholar Advisor on the same held-out task. If substantively interchangeable, the heuristic fails specificity.

### E. Framework contamination
Check whether the candidate merely restates ResearchMind's own Transfer Validator, counterexample discipline, evidence rules or generic scientific virtues.

### F. Transfer test
Explicitly list source structure, target structure, preserved constraints and broken assumptions.

### G. Abstention test
Ask an unsupported question; the advisor must refuse attribution.

## Phase 10 — Three-layer Advisor

Follow `advisor-three-layer.md`:

1. `DOMAIN_BASELINE` — target discipline's ordinary standards; explicitly not scholar-specific.
2. `SCHOLAR_LENS` — only specificity-passed heuristics for strong scholar-specific claims.
3. `TRANSFER_INFERENCE` — structural comparison and confidence.

A response with many baseline findings and only one scholar-specific insight is acceptable and often preferable to heuristic laundering.

## Phase 11 — Structural + epistemic validation

Run against the staged workspace before commit. The CLI checks cross-references, grade fields, specificity gates, eligible Episode types for validated heuristics, inspected A/B evidence for high-strength Episodes, and claim-bearing A-source locators.

CLI green status does not verify historical truth. The Agent must still open authoritative sources to verify dates, terminology, attribution and causal claims.

## Phase 12 — Atomic commit

After staged validation succeeds:

```bash
python scripts/researchmind.py commit-staged --job-id <job-id> --scholar <slug>
```

The pipeline backs up the current scholar directory and swaps the staged version into place. On failure it restores the prior version.

## Phase 13 — Generated advisor

Run:

```bash
python scripts/researchmind.py build-skill --scholar <slug>
```

The generated advisor must disclose Distillation Grade and evidence ceiling and inherit the three-layer review protocol.

## Phase 14 — Completion report

Report:

```text
Scholar:
Requested depth:
Distillation Grade:
Source availability ceiling:
Sources discovered A/B/C/D:
Sources inspected A/B/C/D:
Claim-bearing sources A/B/C/D:
Episodes by type:
Contrastive pairs:
Heuristics candidate/provisional/validated:
Specificity pass/review/reject/not-tested:
Primary-source blockers:
Generated skill:
Scholar-added delta:
Claims that remain unsafe to make:
```

## Universal does not mean equal depth

The system can start from any identifiable scholar with public or user-provided material. It cannot guarantee archival-grade reconstruction for every scholar. Output must degrade gracefully from process-level decision reconstruction to retrospective or publication-level analysis when archives do not exist or are inaccessible.
