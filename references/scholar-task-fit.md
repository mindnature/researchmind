# Scholar–Task Fit & Lens Abstention

ResearchMind v0.6 separates two questions that must not be conflated:

1. Is a heuristic genuinely associated with the scholar?
2. Should that heuristic be activated for this concrete user task?

A scholar can have strong active lenses and still be a poor fit for a particular project.

## Why this gate exists

Without a task-fit gate, an Agent tends to treat the user's request to "use Scholar X" as an instruction to find an analogy. This creates **Forced Lens Activation**: the system searches for some structural resemblance so that the named scholar can contribute, even when the contribution is weak or decorative.

Abstention is therefore a valid and desirable output.

## Four dimensions

Score each 0–100 with explicit rationale and evidence:

### Domain Fit
How close is the scholar's source domain to the target task domain?

### Decision-Structure Fit
Are the underlying decision structures actually similar, beyond vocabulary or surface analogy?

### Evidence Fit
Do the candidate heuristics have enough inspected sources, Episodes, boundaries and counterevidence for this use?

### Added-Value Fit
Compared with Generic ResearchMind or a competent target-domain reviewer, what does this scholar uniquely add to this task?

The machine weights and thresholds are defined only in `config/policy.json`.

## Activation outcomes

### active
The Scholar Lens may be used strongly, but only after Active Lens Provenance and Transfer checks.

### experimental
Use the scholar only to generate diagnostic questions, candidate hypotheses, alternative framings or tests. Do not rewrite the user's theory, identification strategy or research design as established advice.

### abstain
Do not force a scholar-specific section. State that the scholar's public research record does not add reliable task-specific value. Continue with source-backed DOMAIN_BASELINE if useful.

## Cross-domain cap

Cross-domain analogies require unusually strong decision-structure similarity. A low domain-fit score combined with merely moderate structural similarity cannot produce an active recommendation, even if the scholar heuristic itself is well evidenced.

## Transfer action discipline

- high → recommendation allowed
- medium → diagnostic only
- low → question generation only
- reject → abstain

This prevents the common failure in which a report admits `transfer confidence = medium` and then uses the analogy to redesign the user's project anyway.

## Active Lens Provenance Packet

Before a strong scholar lens is used, expose a packet containing:

- heuristic id and rule;
- scholar-added delta;
- supporting and counter Episodes;
- Episode decision actions;
- inspected source locators;
- composition audit.

If the packet is incomplete, downgrade the lens to experimental.

## Composite Heuristic Fabrication

Do not infer ownership of a combined framework from ownership of its components.

Bad pattern:

- source A: scholar discusses participation;
- source B: scholar discusses centralization;
- source C: scholar discusses coverage;
- AI output: "Scholar's Participation × Centralization framework".

Unless one or more Episodes/sources show the scholar actually operating with that combined structure, the framework is AI synthesis, not a strong scholar lens.

Record `composition_audit.components`, `combined_operation_evidence`, `fabrication_risk`, and alternative interpretations.

## Swap-Scholar evaluation

For benchmark or high-stakes tasks, run the same task through:

- Generic ResearchMind;
- the target Scholar Advisor;
- at least one plausible alternative scholar;
- optionally one deliberately poor-fit scholar.

Compare active-lens counts, scholar-added delta, recommended framework and abstention behavior.

Warning signs:

- every scholar produces roughly the same number of active lenses;
- different scholars produce the same "unique" framework;
- scholar-added delta is nearly identical across scholars;
- a deliberately poor-fit scholar still gives confident redesign advice.

The desired system is not one in which every scholar is useful. It is one in which usefulness varies sharply with task fit.
