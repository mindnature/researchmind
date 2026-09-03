#!/usr/bin/env python3
"""Dependency-free structural validator for the ResearchMind MVP."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

EPISODE_REQUIRED = {
    "episode_id", "scientist", "title", "decision_date", "research_question",
    "source_refs", "known_at_the_time", "unknown_at_the_time", "decision_action",
    "observed_result", "evidence_strength", "needs_primary_source_review"
}
HEURISTIC_REQUIRED = {
    "heuristic_id", "name", "status", "decision_structure", "rule",
    "supporting_episodes", "boundary_conditions", "failure_signals"
}
SOURCE_REQUIRED = {"source_id", "title", "source_class", "url", "inspection_status"}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def missing(obj: dict, required: set[str]) -> list[str]:
    return sorted(required - set(obj))


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    source_items = load_json(root / "data/pauling/source_registry.json")
    source_ids = set()
    for i, src in enumerate(source_items):
        miss = missing(src, SOURCE_REQUIRED)
        if miss:
            errors.append(f"source[{i}] missing: {', '.join(miss)}")
        sid = src.get("source_id")
        if sid in source_ids:
            errors.append(f"duplicate source_id: {sid}")
        source_ids.add(sid)

    episodes = {}
    for path in sorted((root / "data/pauling/episodes").glob("*.json")):
        ep = load_json(path)
        miss = missing(ep, EPISODE_REQUIRED)
        if miss:
            errors.append(f"{path.name} missing: {', '.join(miss)}")
        eid = ep.get("episode_id")
        if eid in episodes:
            errors.append(f"duplicate episode_id: {eid}")
        episodes[eid] = ep
        for ref in ep.get("source_refs", []):
            if ref not in source_ids:
                errors.append(f"{eid}: unknown source_ref {ref}")
        if ep.get("evidence_strength") not in {"high", "medium", "low", "unknown"}:
            errors.append(f"{eid}: invalid evidence_strength")

    heuristics = {}
    for path in sorted((root / "data/pauling/heuristics").glob("*.json")):
        h = load_json(path)
        miss = missing(h, HEURISTIC_REQUIRED)
        if miss:
            errors.append(f"{path.name} missing: {', '.join(miss)}")
        hid = h.get("heuristic_id")
        if hid in heuristics:
            errors.append(f"duplicate heuristic_id: {hid}")
        heuristics[hid] = h
        if h.get("status") not in {"candidate", "provisional", "validated", "rejected"}:
            errors.append(f"{hid}: invalid status")
        for ref in h.get("supporting_episodes", []) + h.get("counter_episodes", []):
            if ref not in episodes:
                errors.append(f"{hid}: unknown episode ref {ref}")
        if h.get("status") == "validated" and not h.get("counter_episodes"):
            errors.append(f"{hid}: validated heuristic requires counter_episodes")

    for eid, ep in episodes.items():
        for hid in ep.get("candidate_heuristics", []):
            if hid not in heuristics:
                errors.append(f"{eid}: unknown candidate heuristic {hid}")

    return errors


def stats(root: Path = ROOT) -> dict:
    sources = load_json(root / "data/pauling/source_registry.json")
    episodes = [load_json(p) for p in (root / "data/pauling/episodes").glob("*.json")]
    heuristics = [load_json(p) for p in (root / "data/pauling/heuristics").glob("*.json")]
    return {
        "sources": len(sources),
        "episodes": len(episodes),
        "episodes_needing_primary_review": sum(bool(e.get("needs_primary_source_review")) for e in episodes),
        "heuristics": len(heuristics),
        "validated_heuristics": sum(h.get("status") == "validated" for h in heuristics),
        "provisional_heuristics": sum(h.get("status") == "provisional" for h in heuristics),
        "candidate_heuristics": sum(h.get("status") == "candidate" for h in heuristics),
    }


def main() -> int:
    parser = argparse.ArgumentParser(prog="researchmind")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    sub.add_parser("stats")
    args = parser.parse_args()

    if args.cmd == "validate":
        errors = validate()
        if errors:
            print("Validation failed:")
            for err in errors:
                print(f"- {err}")
            return 1
        print("Validation OK")
        return 0

    if args.cmd == "stats":
        print(json.dumps(stats(), ensure_ascii=False, indent=2))
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
