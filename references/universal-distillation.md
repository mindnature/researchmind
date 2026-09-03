# Universal Scholar Distillation Protocol

This is the execution protocol for `$researchmind 蒸馏 <scholar>`.

## Phase 0 — Resolve the request

Extract:

- scholar name;
- optional focus;
- requested depth (`quick|standard|deep|golden`), default `standard`;
- user-provided local/public sources if any;
- whether this is a new distillation or an update.

If the scholar is unambiguous, do not block on questions.

## Phase 1 — Scaffold the scholar workspace

Create a slug and initialize:

```bash
python scripts/researchmind.py init-scholar "<canonical name>" --depth <depth> [--focus "..."]
```

The command creates:

```text
data/<slug>/
  scholar_profile.json
  distillation_manifest.json
  source_registry.json
  episodes/
  heuristics/
  evidence/
  PRIMARY_SOURCE_QUEUE.md
```

Then populate `scholar_profile.json` after identity reconnaissance.

## Phase 2 — Source reconnaissance

Follow `source-discovery.md`.

Create a source registry before deep synthesis. Every source receives:

- unique source_id;
- A/B/C/D class;
- date and author;
- URL/archive location;
- stable locator if known;
- inspection status;
- what the source can and cannot establish.

Do not treat search-result snippets as inspected sources.

## Phase 3 — Research-life map

Build a chronological map containing:

- major research programs;
- important collaborators;
- major papers/results;
- known failures/reversals/disputes;
- method or theory shifts;
- archive-rich periods;
- candidate decision episodes.

This map is navigation, not yet a heuristic list.

## Phase 4 — Candidate Episode selection

Rank candidate Episodes using four criteria:

1. Decision visibility — can we reconstruct an actual choice/action?
2. Evidence quality — are primary/process sources available?
3. Contrast value — is there a success/failure/boundary counterpart?
4. Transfer potential — is the decision structure useful beyond the historical case?

Choose the smallest high-signal set appropriate to depth.

Suggested minimums:

- quick: 3 Episodes
- standard: 5 Episodes
- deep: 8 Episodes or justified saturation
- golden: evidence quality matters more than count

## Phase 5 — Episode reconstruction

For every Episode:

1. define the research question at that historical moment;
2. enforce the Temporal Firewall;
3. separate known vs unknown at the time;
4. record alternatives actually evidenced; do not invent a menu of options;
5. identify decision owners and team contributors;
6. state the observable research action;
7. record the result without making outcome knowledge leak backward;
8. list alternative historical interpretations;
9. assign evidence strength;
10. create primary-source blockers for unresolved key claims.

## Phase 6 — Contrastive pairing

Search across Episodes for repeated decision structures.

Pair:

- success × failure;
- success × boundary case;
- early view × later reversal;
- same heuristic across different research programs;
- same research problem handled differently by collaborators/competitors when useful.

Do not force a pair merely to satisfy a format.

## Phase 7 — Heuristic extraction

A heuristic must contain:

- decision structure;
- operational rule;
- actions;
- supporting Episodes;
- counter Episodes;
- boundary conditions;
- failure signals;
- evidence class;
- status.

Reject generic virtues such as curiosity, persistence, rigor, creativity unless they are converted into observable decision rules supported by Episodes.

## Phase 8 — Validation

Before promotion to `validated`, test:

### A. Within-person recurrence

Does the decision structure recur across more than one Episode?

### B. Contrastive boundary

Does a failure/counter Episode specify when the rule breaks?

### C. Historical holdout

Hide the later part of an Episode and ask whether the heuristic predicts a useful next action without using future information.

### D. Transfer test

Apply the rule to a structurally similar new research problem and explicitly list preserved constraints and broken assumptions.

### E. Abstention test

Ask an intentionally unsupported question. The advisor must refuse to attribute an answer to the scholar.

## Phase 9 — Generated advisor

Run:

```bash
python scripts/researchmind.py build-skill --scholar <slug>
```

The generated advisor should be usable independently. It must not claim authorization or identity with the scholar.

## Phase 10 — Completion report

Report:

```text
Scholar:
Depth:
Focus:
Source availability ceiling:
Sources A/B/C/D:
Episodes:
Contrastive pairs:
Heuristics: candidate / provisional / validated
Primary-source blockers:
Generated skill:
Strongest supported research behaviors:
Claims that remain unsafe to make:
```

## Update mode

If `data/<slug>/` exists:

- do not overwrite inspected source records;
- add new sources with new IDs;
- revise Episodes only when stronger evidence changes the reconstruction;
- record why heuristic status changed;
- regenerate the advisor after validation.

## Universal does not mean equal depth

The system can start from any identifiable scholar with public or user-provided material. It cannot guarantee `golden_archive` quality for every scholar. The output must degrade gracefully from process-level decision reconstruction to publication-level analysis when archives do not exist or are inaccessible.
