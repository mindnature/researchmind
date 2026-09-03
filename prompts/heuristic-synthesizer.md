# Heuristic Synthesizer Prompt

Given multiple Research Decision Episodes:

1. Identify repeated decision structures, not repeated slogans.
2. Formulate each heuristic as an if/then or trigger/action rule.
3. Bind the heuristic to supporting episodes.
4. Search explicitly for a counter/failure episode.
5. State boundary conditions and failure signals.
6. Reject generic advice that would apply to nearly every competent researcher.
7. Do not claim causality unless the historical evidence supports it.
8. A heuristic without counter-evidence is at most `provisional`.

Output must conform to `schemas/heuristic.schema.json`.
