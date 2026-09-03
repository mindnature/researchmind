# Transactional Scholar Write Pipeline

ResearchMind should not leave half-written scholar datasets when an Agent tool call times out or a multi-file write fails.

## Staging model

Use:

```text
.researchmind/staging/<job-id>/
├── job.json
├── checkpoint.json
├── errors.json              # only when validation fails
└── data/<scholar-slug>/
```

The Agent writes and revises the staged scholar workspace first.

## Commit rule

Before data enters `data/<scholar-slug>/`:

1. run structural validation;
2. run epistemic consistency validation;
3. write checkpoint state;
4. copy staged data to a same-filesystem temporary directory;
5. move the current scholar directory to a backup when updating;
6. atomically rename the new directory into place;
7. roll back the backup if the final swap fails.

## CLI

```bash
python scripts/researchmind.py stage-scholar "Geoffrey Hinton"
python scripts/researchmind.py epistemic-validate --scholar geoffrey-hinton
python scripts/researchmind.py commit-staged --job-id <job-id> --scholar geoffrey-hinton
```

For writes performed inside a staging job, run validation against the staging root before commit.

Abort with:

```bash
python scripts/researchmind.py abort-staged --job-id <job-id>
```

## Atomic JSON writes

Individual JSON/text writes use temporary sibling files plus `os.replace`, preventing partially written files from becoming canonical.

## Why not SQLite yet?

The JSON/Git layout remains transparent and reviewable for an open-source Skill. SQLite may become useful when the corpus grows to thousands of Episodes, but v0.4 first fixes partial-write failure with transactional staging and atomic file replacement.
