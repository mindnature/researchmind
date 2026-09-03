# Episode Extractor Prompt

You are extracting a Research Decision Episode, not writing a biography.

Rules:
1. Freeze the timeline. Do not use facts discovered after the decision date in `known_at_the_time`.
2. Attribute each action to the correct person or team.
3. Prefer operational verbs and observable decisions.
4. Separate source fact from reconstruction.
5. If a field cannot be supported, leave it empty/null or mark review required.
6. Never invent notebook/page/timestamp/quote locators.
7. Capture plausible alternative interpretations.

Output must conform to `schemas/episode.schema.json`.
