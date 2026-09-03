# Adaptive Validation — Error / Warning / Info

ResearchMind v0.5 uses graceful degradation. Quality control must not turn ordinary automatic distillation into a manual YAML repair workflow.

## ERROR — blocking

Errors protect data integrity or prevent false evidence claims. They block `commit-staged` and `build-skill`.

Examples:

- malformed or missing required files;
- duplicate or broken source / episode / heuristic references;
- a claim-bearing Class A source is presented as process evidence without direct inspection and a stable locator;
- an Episode is marked `high` evidence without any inspected A/B source;
- invalid enum/status values that make routing ambiguous.

## WARNING — commit allowed, capability reduced

Warnings never block atomic commit. The system records them in `quality_report.json` and lowers the generated Advisor's capabilities.

Examples:

- specificity is low or rejected;
- generic baseline overlap is high;
- framework contamination is high;
- a validated heuristic has no counter Episode;
- a career/institution/field-outcome Episode is connected to a heuristic;
- zero active scholar-specific lenses remain after routing;
- a C/D-grade corpus is being used for micro-decision reconstruction.

## INFO — state disclosure

Info records corpus limitations and experimental lenses without treating them as faults.

## Soft routing

Specificity is orthogonal to evidence maturity.

`status`:

- candidate
- provisional
- validated
- rejected

`routing.lens_eligibility`:

- `active_lens`: may appear in strong `SCHOLAR_LENS` advice;
- `experimental_lens`: may generate questions, clearly labeled experimental;
- `generic_absorbed`: not scholar-specific; may become a `DOMAIN_BASELINE` candidate only after target-domain grounding;
- `excluded`: do not use.

A heuristic can therefore be historically `validated` but still be `generic_absorbed`. This is expected, not an error.

## Why this matters

The system should prefer a complete but honestly degraded Advisor over a failed pipeline or fabricated scholar-specific lens.
