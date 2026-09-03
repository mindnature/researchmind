# Evidence Model

## Source classes

| Class | Meaning | Typical material | Default weight |
|---|---|---|---:|
| A | contemporaneous process evidence | notebook, lab log, draft, correspondence | 4 |
| B | contemporaneous formal output | paper, preprint, supplement, dataset | 3 |
| C | retrospective self-account | lecture, interview, autobiography | 2 |
| D | third-party reconstruction | biography, history, colleague recollection | 1 |

Weights are not truth scores. They only control how much a source can support a reconstruction before corroboration.

## Claim statuses

### DIRECT_EVIDENCE
The claim is explicit in an inspected source and has a stable locator.

Required:
- source_id
- locator (page, paragraph, timestamp, figure, record id, or stable URL section)
- short paraphrase; quote only when needed

### CROSS_SOURCE_SYNTHESIS
The claim is an analytical synthesis.

Required:
- at least two supporting evidence refs when the claim is central
- no language implying the scientist literally said the synthesis
- alternative interpretation when plausible

### TRANSFER_INFERENCE
A validated heuristic is applied to a new problem.

Required:
- heuristic_id
- source and target structure
- preserved constraints
- broken assumptions
- confidence

### INSUFFICIENT_EVIDENCE
Use when attribution, timing, causal interpretation, or source location is unresolved.

This is a successful output, not an error.

## Evidence strength

- `high`: direct contemporaneous evidence plus corroboration, or multiple converging primary records.
- `medium`: one strong primary source plus compatible secondary/context evidence.
- `low`: retrospective or secondary reconstruction without adequate contemporaneous confirmation.
- `unknown`: source not inspected or locator not verified.

## Precision rule

Never produce a page, notebook number, timestamp, quotation, experiment number, date, or causal sequence that has not been inspected. If a secondary source says such a record exists, register the source and set `needs_primary_source_review: true` until the actual item is checked.
