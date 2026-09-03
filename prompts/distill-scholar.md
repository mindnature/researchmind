# Universal Scholar Distillation Orchestrator

Use this prompt when the user says `$researchmind 蒸馏 <scholar>` or equivalent.

## Objective

Turn an identifiable scholar plus public/user-provided research materials into a traceable research-judgment advisor. Do not create a personality imitation.

## Execution order

1. Resolve identity and aliases.
2. Initialize or resume `data/<slug>/`.
3. Populate `scholar_profile.json`.
4. Run source reconnaissance using `references/source-discovery.md`.
5. Register sources before synthesizing them.
6. Build a research-life map and candidate Episode list.
7. Select high-signal Episodes according to requested depth.
8. Reconstruct Episodes with Temporal Firewall and Team Attribution.
9. Search deliberately for failure/counter/boundary Episodes.
10. Synthesize candidate heuristics.
11. Run contrastive, historical-holdout, transfer and abstention tests.
12. Promote only heuristics whose evidence supports promotion.
13. Build the portable advisor Skill.
14. Report source ceiling, unresolved blockers and unsafe claims.

## Default depth

`standard` unless the user specifies otherwise.

## Do not block unnecessarily

If the scholar identity is clear, begin work immediately. Do not ask the user to provide a reading list before conducting public source reconnaissance. Ask only if identity is materially ambiguous, access to user-controlled private files is necessary, or a user preference would fundamentally change the corpus.

## Stop conditions

Do not produce a confident research heuristic when:

- the evidence is only generic biography;
- the supposed decision cannot be located in a real Episode;
- team ownership is materially unresolved;
- future knowledge contaminates the historical reconstruction;
- there is no evidence for the claimed alternative or action;
- a cross-domain transfer relies only on surface analogy.

Use `INSUFFICIENT_EVIDENCE` and create a Primary Source Queue item instead.

## End state

A completed run should leave:

```text
data/<slug>/scholar_profile.json
data/<slug>/distillation_manifest.json
data/<slug>/source_registry.json
data/<slug>/episodes/*.json
data/<slug>/heuristics/*.json
generated/<slug>-research-advisor/SKILL.md
```

and a concise audit report explaining what the advisor can and cannot legitimately claim.
