# Changelog

## 0.3.0-universal-scholar-distiller

- Repositioned ResearchMind from a Pauling-centered prototype to a universal scholar Skill generator.
- Added name-only entry: `$researchmind 蒸馏 <scholar>`.
- Added scholar identity/profile stage and `schemas/scholar_profile.schema.json`.
- Added universal source discovery protocol with A/B/C/D evidence classes.
- Added explicit search for failures, reversals, abandoned directions and collaborator evidence.
- Added `quick`, `standard`, `deep`, and `golden` distillation depths.
- Added source-availability ceilings: `publication_only`, `public_retrospective`, `process_evidence`, `golden_archive`.
- Generalized data layout to `data/<scholar-slug>/`.
- Generalized CLI with `init-scholar`, `list-scholars`, scholar-scoped `validate`/`stats`, and `build-skill`.
- Added automatic packaging of a scholar corpus into a portable `<slug>-research-advisor` Skill.
- Added universal scaffold/build unit tests.
- Added GitHub Actions CI workflow.
- Converted Pauling into the first Golden Set reference dataset rather than a hard-coded implementation.

## 0.2.0-evidence-pass-1

- Upgraded the Pauling source registry with inspected primary publications and archival/participant sources.
- Strengthened the alpha-helix, DNA triple-helix and sickle-cell Episodes.
- Added a contrastive validation record for `LP-H01-HARD-CONSTRAINT-FIRST`.
- Added `PRIMARY_SOURCE_QUEUE.md` for unresolved process-level archival blockers.
- Kept the central heuristic `provisional` until contemporaneous process objects are directly inspected.

## 0.1.0-mvp

- Added ResearchMind Skill specification.
- Added four-level evidence attribution model.
- Added Temporal Firewall and Team Attribution rules.
- Added contrastive heuristic synthesis and Transfer Validator.
- Added Pauling source registry.
- Added three Pauling episode skeletons: alpha helix, sickle-cell molecular disease, DNA triple helix.
- Added two candidate/provisional heuristics.
- Added dependency-free validation CLI and tests.
- Deliberately left exact primary-source locators unresolved rather than fabricating precision.
