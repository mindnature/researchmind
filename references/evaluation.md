# Evaluation Harness

ResearchMind is not evaluated by style imitation.

## 1. Historical reconstruction

Hide the latter part of a known Episode and provide only information available at time T.

Score:
- temporal leakage (0/1)
- plausible next diagnostic action (0-2)
- match to documented decision structure (0-2)
- unsupported specificity penalty (0 to -2)

## 2. Counterexample detection

Present a case that superficially matches a success heuristic but violates a known boundary.

Pass condition: the system invokes the failure/counter Episode and lowers confidence instead of mechanically reusing the success rule.

## 3. Cross-domain transfer

Evaluate:
- source structure
- target structure
- preserved constraints
- broken assumptions
- usefulness of proposed next action
- risk of misleading analogy

A low-confidence transfer must remain a question generator rather than a recommendation.

## 4. Abstention

Ask questions outside the evidence base or with insufficient historical support.

Pass condition: return `INSUFFICIENT_EVIDENCE` or `transfer_confidence: reject/low` rather than inventing a scholar-specific view.

## 5. Generic baseline A/B test

Give the same held-out research task to:

A. Generic ResearchMind / competent domain research advisor.
B. Scholar-specific Research Advisor.

Compare the substantive diagnostic actions, not wording or style.

Required output:
- generic baseline findings;
- scholar-lens findings;
- scholar-added delta;
- findings that are interchangeable and therefore must stay in `DOMAIN_BASELINE`.

If the scholar answer is substantively interchangeable with the generic baseline, the heuristic fails the specificity test.

## 6. Heuristic laundering test

Take each candidate heuristic and remove the scholar's name.

Ask:
1. Would generic research training produce the same rule?
2. Is the rule already required by ResearchMind's own protocol?
3. Does it recur in multiple scholar Episodes as an operational decision pattern?
4. Is there a counter/boundary case that makes the rule discriminative?

A heuristic that mainly restates generic rigor, curiosity, persistence, first-principles thinking, counterexample search, or ResearchMind's own Transfer Validator must be downgraded or rejected unless distinctive operational evidence exists.

## 7. Framework contamination test

Compare each candidate heuristic against:
- ResearchMind core rules;
- target-domain review standards;
- at least one other scholar model when feasible.

Pass condition: the claimed scholar-specific value cannot be explained primarily by the framework that performed the distillation.

## 8. Three-layer advisor separation

For cross-domain review tasks, evaluate whether the answer cleanly separates:

1. `DOMAIN_BASELINE`
2. `SCHOLAR_LENS`
3. `TRANSFER_INFERENCE`

Fail if generic domain standards are relabeled with scholar heuristic IDs.

## v0.4 success criterion

A scholar-specific heuristic is considered technically strong only if it:

1. is supported by traceable evidence;
2. has a counter/failure/boundary Episode when appropriate;
3. passes the Scholar Specificity Gate;
4. shows a meaningful scholar-added delta over the generic baseline;
5. improves a held-out research judgment task without increasing unsupported attribution or false precision.
