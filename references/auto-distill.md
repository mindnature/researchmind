# Auto Distill Orchestrator

ResearchMind v0.5 exposes an agent-driven one-click pipeline while keeping the Python CLI honest about its capabilities.

## User-level entry

```text
$researchmind 蒸馏 Geoffrey Hinton
```

Agent implementations may initialize the job with:

```bash
python scripts/researchmind.py auto-distill "Geoffrey Hinton" --mode fast-auto
```

Supported modes:

- `fast-auto` → quick depth
- `standard-auto` → standard depth
- `deep-auto` → deep depth

## Responsibility split

The CLI does not pretend to have its own web browser or academic search engine.

CLI responsibilities:

- create the staging workspace;
- create and persist `pipeline.json`;
- checkpoint phases;
- structural validation;
- soft routing;
- quality reporting;
- atomic commit;
- build the portable scholar Advisor.

Installed ResearchMind Agent responsibilities:

- identity resolution;
- public web / archive / file retrieval through available tools;
- opening and inspecting sources;
- source registration;
- Episode reconstruction;
- heuristic synthesis;
- specificity assessment;
- Domain Baseline retrieval at Advisor runtime.

## Pipeline phases

The canonical phase order is stored in `config/policy.json` and written to `pipeline.json`:

1. identity
2. source_discovery
3. domain_baseline_mapping
4. episode_extraction
5. heuristic_synthesis
6. specificity_routing
7. quality_validation
8. commit
9. build_skill

Use:

```bash
python scripts/researchmind.py pipeline-status --job-id <job-id>
```

and:

```bash
python scripts/researchmind.py advance-pipeline \
  --job-id <job-id> \
  --phase source_discovery \
  --status completed \
  --note "source registry populated"
```

## Failure behavior

Blocking evidence-integrity errors stop commit.

Quality weakness does not. Low specificity, sparse process evidence or zero active Scholar Lenses produce warnings and capability downgrades. The final Advisor should still build when its data are structurally and evidentially safe.

This is deliberate graceful degradation, not a bypass of evidence discipline.
