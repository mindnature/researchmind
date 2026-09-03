# Scholar Specificity Gate

ResearchMind must prevent **Heuristic Laundering**: generic research advice must not be relabeled as a famous scholar's distinctive method.

## Core question

Before accepting a heuristic as scholar-specific, ask:

> If the scholar's name were removed, would a competent generic research advisor produce substantially the same rule?

If yes, the heuristic belongs to the generic baseline unless there is strong evidence for a distinctive operational pattern.

## Required specificity fields

Every heuristic may contain a `specificity` object:

- `status`: `not_tested | pass | review | reject`
- `generic_baseline_overlap`: `low | medium | high | unknown`
- `scholar_specificity`: `low | medium | high | unknown`
- `framework_contamination`: `low | medium | high | unknown`
- `scholar_added_delta`: what this scholar adds beyond a competent generic research advisor
- `specificity_evidence`: at least two concrete evidence statements for a passing heuristic
- optional `generic_baseline_comparison`
- optional `other_scholar_overlap`

## Pass rule

A heuristic may pass only when:

1. `scholar_specificity = high`;
2. `generic_baseline_overlap != high`;
3. `framework_contamination` is low or medium;
4. `scholar_added_delta` is explicit;
5. at least two evidence statements support the distinction.

A `validated` heuristic must pass this gate.

## Framework contamination

Framework contamination occurs when ResearchMind's own rules are rediscovered and attributed to the scholar.

Examples:

- ResearchMind already requires Transfer Validator; therefore "preserve structure, not mechanism" cannot automatically be labeled a Yao/Feynman/Hinton heuristic.
- ResearchMind already requires counterexamples; therefore "look for counterexamples" is not scholar-specific without independent behavioral evidence.

When suspected, compare the candidate rule against:

1. ResearchMind's own protocol;
2. a generic research-advisor baseline;
3. at least one other scholar's corpus where feasible.

## Generic virtues are not enough

Reject or downgrade rules such as:

- ask important questions;
- be rigorous;
- persist;
- think independently;
- use first principles;
- follow evidence.

They become useful only when converted into a recurring, discriminative decision program:

`trigger → representation → exclusion rule → action → stop/change condition`.

## A/B evaluation

For held-out tasks, compare:

- Generic ResearchMind answer;
- Scholar Advisor answer.

Record the **scholar-added delta**. If the two answers are substantively interchangeable, the scholar lens has not earned its attribution.
