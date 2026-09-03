# Three-Layer Advisor Protocol

Scholar advisors must separate general domain expertise from scholar-specific value.

## Layer 1 — DOMAIN_BASELINE

Audit the user's work using normal standards of the target discipline.

Examples:

- DID requires a defensible treatment/control design and parallel-trends evidence.
- A survey construct requires defensible operationalization and measurement checks.
- A benchmark comparison requires fair baselines and leakage control.

These claims must be labeled `DOMAIN_BASELINE` and must **not** be attached to scholar heuristic IDs merely for rhetorical coherence.

## Layer 2 — SCHOLAR_LENS

Use only heuristics whose `specificity.status = pass` for strong scholar-specific claims.

For each lens report:

- heuristic ID and rule;
- supporting Episode(s);
- counter/boundary Episode(s);
- scholar-added delta;
- why a generic advisor would not produce the same diagnostic in the same way.

Heuristics still marked `not_tested` or `review` may be shown only as experimental lenses and cannot be called distinctive characteristics of the scholar.

## Layer 3 — TRANSFER_INFERENCE

For each attempted cross-domain use, report:

- source_structure;
- target_structure;
- preserved_constraints;
- broken_assumptions;
- transfer_confidence: `high | medium | low | reject`.

Interpretation:

- `high`: may support a recommendation when target-domain evidence also supports it;
- `medium`: diagnostic aid; recommendation needs target-domain corroboration;
- `low`: question generator only;
- `reject`: do not use the analogy.

## Output discipline

A strong answer may contain many DOMAIN_BASELINE findings and only one or two SCHOLAR_LENS findings. This is a feature, not a failure.

The goal is not to maximize scholar-flavored content. The goal is to isolate the genuine epistemic increment supplied by the scholar-specific model.
