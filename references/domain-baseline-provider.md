# Domain Baseline Provider

`DOMAIN_BASELINE` must not become an ungrounded LLM opinion layer.

## Runtime contract

Before issuing technical baseline criticism, resolve the target discipline and gather the best available baseline evidence through normal access paths. Prefer:

1. official reporting / submission / evaluation guidance;
2. established handbooks or methodological standards;
3. authoritative methods papers or consensus guidance;
4. user-provided project rules or journal instructions;
5. model knowledge only when fresh/source-backed retrieval is unavailable.

## Baseline claim format

Use `schemas/domain_baseline.schema.json`.

Every material baseline claim should include:

- domain;
- claim;
- provenance status;
- confidence;
- source title / URL / locator when source-backed;
- applicability or known exceptions.

`provenance_status`:

- `source_backed`
- `user_provided`
- `model_knowledge_unverified`

If the claim is `model_knowledge_unverified`, do not present it as a hard rule. Phrase it as a provisional methods check and verify it before making a high-stakes recommendation.

## Generic-absorbed heuristics

A heuristic routed as `generic_absorbed` is not automatically a valid domain baseline. It is only a candidate question or rule. It enters `DOMAIN_BASELINE` only when the target domain has independent support for that rule.

Example:

`Be rigorous about assumptions` is generic and should not be attributed to Yao. It also should not appear as a concrete econometric baseline until the relevant assumption requirement is grounded in the target research design.

## Separation rule

Never let the authority of the scholar raise the confidence of a domain baseline claim. Domain evidence and scholar evidence are independent channels.
