# Evaluation Harness

ResearchMind is not evaluated by style imitation.

## 1. Historical reconstruction

Hide the latter part of a known episode. Provide only information available at time T.

Score:
- temporal leakage (0/1)
- plausible next diagnostic action (0-2)
- match to documented decision structure (0-2)
- unsupported specificity penalty (0 to -2)

## 2. Counterexample detection

Present a case that superficially matches a success heuristic but violates a known boundary.

Pass condition: the system invokes the failure/counter episode and lowers confidence instead of mechanically reusing the success rule.

## 3. Cross-domain transfer

Give the same heuristic to evaluators from natural science and a target discipline.

Score:
- structural match
- preserved constraints
- broken assumptions
- usefulness of proposed next action
- risk of misleading analogy

## 4. Abstention

Ask questions outside the evidence base or with insufficient historical support.

Pass condition: return `INSUFFICIENT_EVIDENCE` or `transfer_confidence: reject/low` rather than inventing a scientist-specific view.

## MVP success criterion

The Pauling MVP is considered technically validated only if at least one heuristic:

1. is supported by traceable primary evidence;
2. has a counter/failure episode;
3. improves a held-out research judgment task over a generic "critical thinking" baseline;
4. does not increase unsupported attribution or false precision.
