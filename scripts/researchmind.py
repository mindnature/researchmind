#!/usr/bin/env python3
"""ResearchMind CLI — v0.5 adaptive distillation runtime."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.core import *  # noqa: F401,F403
from runtime.pipeline import *  # noqa: F401,F403
from runtime.policy import *  # noqa: F401,F403


def _print_quality(report: dict) -> int:
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report.get("errors") else 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="researchmind")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init-scholar")
    p_init.add_argument("name")
    p_init.add_argument("--slug")
    p_init.add_argument("--depth", choices=sorted(VALID_DEPTHS), default="standard")
    p_init.add_argument("--focus")

    p_stage = sub.add_parser("stage-scholar")
    p_stage.add_argument("name")
    p_stage.add_argument("--job-id")
    p_stage.add_argument("--slug")
    p_stage.add_argument("--depth", choices=sorted(VALID_DEPTHS), default="standard")
    p_stage.add_argument("--focus")

    p_auto = sub.add_parser("auto-distill")
    p_auto.add_argument("name")
    p_auto.add_argument("--mode", default="fast-auto")
    p_auto.add_argument("--focus")
    p_auto.add_argument("--slug")

    p_pipe = sub.add_parser("pipeline-status")
    p_pipe.add_argument("--job-id", required=True)

    p_advance = sub.add_parser("advance-pipeline")
    p_advance.add_argument("--job-id", required=True)
    p_advance.add_argument("--phase", required=True)
    p_advance.add_argument("--status", required=True)
    p_advance.add_argument("--note", default="")

    p_commit = sub.add_parser("commit-staged")
    p_commit.add_argument("--job-id", required=True)
    p_commit.add_argument("--scholar", required=True)

    p_abort = sub.add_parser("abort-staged")
    p_abort.add_argument("--job-id", required=True)

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("--scholar")

    p_quality = sub.add_parser("quality-report")
    p_quality.add_argument("--scholar")

    p_epi = sub.add_parser("epistemic-validate")
    p_epi.add_argument("--scholar")

    p_route = sub.add_parser("route-heuristics")
    p_route.add_argument("--scholar", required=True)

    p_stats = sub.add_parser("stats")
    p_stats.add_argument("--scholar")

    p_build = sub.add_parser("build-skill")
    p_build.add_argument("--scholar", required=True)
    p_build.add_argument("--output")

    sub.add_parser("list-scholars")
    args = parser.parse_args()

    try:
        if args.cmd == "init-scholar":
            print(init_scholar(args.name, args.slug, args.depth, args.focus).resolve())
            return 0
        if args.cmd == "stage-scholar":
            job_id, base = stage_scholar(args.name, args.job_id, args.slug, args.depth, args.focus)
            print(json.dumps({"job_id": job_id, "path": str(base.resolve())}, ensure_ascii=False))
            return 0
        if args.cmd == "auto-distill":
            print(json.dumps(auto_distill(args.name, args.mode, args.focus, args.slug), ensure_ascii=False, indent=2))
            return 0
        if args.cmd == "pipeline-status":
            print(json.dumps(load_json(staging_root(ROOT, args.job_id) / "pipeline.json"), ensure_ascii=False, indent=2))
            return 0
        if args.cmd == "advance-pipeline":
            print(json.dumps(update_pipeline(args.job_id, args.phase, args.status, args.note), ensure_ascii=False, indent=2))
            return 0
        if args.cmd == "commit-staged":
            print(commit_staged(args.job_id, args.scholar).resolve())
            return 0
        if args.cmd == "abort-staged":
            abort_staged(args.job_id)
            return 0
        if args.cmd == "validate":
            errors = validate(ROOT, args.scholar)
            if errors:
                print("Validation failed:")
                for error in errors:
                    print(f"- {error}")
                return 1
            print("Validation OK")
            return 0
        if args.cmd in {"quality-report", "epistemic-validate"}:
            return _print_quality(quality_report(ROOT, args.scholar))
        if args.cmd == "route-heuristics":
            print(json.dumps({"changed": apply_soft_routing(args.scholar, ROOT)}, ensure_ascii=False))
            return 0
        if args.cmd == "stats":
            print(json.dumps(stats(ROOT, args.scholar), ensure_ascii=False, indent=2))
            return 0
        if args.cmd == "build-skill":
            output = Path(args.output) if args.output else None
            print(build_skill(args.scholar, ROOT, output).resolve())
            return 0
        if args.cmd == "list-scholars":
            print("\n".join(discover_scholar_slugs(ROOT)))
            return 0
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
