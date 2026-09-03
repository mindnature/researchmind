#!/usr/bin/env python3
"""Dependency-free scaffold, validator and packager for ResearchMind scholar distillations."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
GENERATED_ROOT = ROOT / "generated"

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
PROFILE_REQUIRED = {
    "canonical_name", "slug", "fields", "active_period", "major_research_programs",
    "major_contributions", "major_collaborators", "likely_archives", "source_availability",
    "source_availability_ceiling", "depth"
}
VALID_DEPTHS = {"quick", "standard", "deep", "golden"}
VALID_CEILINGS = {
    "publication_only", "public_retrospective", "process_evidence", "golden_archive", "unknown"
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def missing(obj: dict, required: set[str]) -> list[str]:
    return sorted(required - set(obj))


def slugify(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    if slug:
        return slug
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:10]
    return f"scholar-{digest}"


def scholar_dir(root: Path, slug: str) -> Path:
    return root / "data" / slug


def discover_scholar_slugs(root: Path = ROOT) -> list[str]:
    data_root = root / "data"
    if not data_root.exists():
        return []
    slugs = []
    for p in sorted(data_root.iterdir()):
        if p.is_dir() and (p / "source_registry.json").exists():
            slugs.append(p.name)
    return slugs


def depth_targets(depth: str) -> dict:
    return {
        "quick": {"sources": "5-10", "episodes": 3, "contrastive_pairs": 0, "heuristics": "1-3"},
        "standard": {"sources": "20-40", "episodes": 5, "contrastive_pairs": 2, "heuristics": "3-7"},
        "deep": {"sources": "quality-driven", "episodes": 8, "contrastive_pairs": 2, "heuristics": "evidence-driven"},
        "golden": {"sources": "primary-source-driven", "episodes": 3, "contrastive_pairs": 1, "heuristics": "validation-driven"},
    }[depth]


def init_scholar(name: str, slug: str | None = None, depth: str = "standard", focus: str | None = None,
                 root: Path = ROOT) -> Path:
    if depth not in VALID_DEPTHS:
        raise ValueError(f"invalid depth: {depth}")
    slug = slug or slugify(name)
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise ValueError("slug must use lowercase ASCII letters, digits and hyphens")

    base = scholar_dir(root, slug)
    for sub in ("episodes", "heuristics", "evidence"):
        (base / sub).mkdir(parents=True, exist_ok=True)

    profile_path = base / "scholar_profile.json"
    if not profile_path.exists():
        write_json(profile_path, {
            "canonical_name": name,
            "slug": slug,
            "aliases": [],
            "fields": [],
            "subfields": [],
            "institutions": [],
            "active_period": None,
            "major_research_programs": [],
            "major_contributions": [],
            "major_failures_reversals_disputes": [],
            "major_collaborators": [],
            "likely_archives": [],
            "source_availability": {
                "process_primary": "unknown",
                "publications": "unknown",
                "retrospectives": "unknown",
                "third_party_history": "unknown"
            },
            "source_availability_ceiling": "unknown",
            "identity_disambiguation_notes": "",
            "focus": focus,
            "depth": depth
        })

    manifest_path = base / "distillation_manifest.json"
    if not manifest_path.exists():
        write_json(manifest_path, {
            "manifest_version": "0.3",
            "scholar": name,
            "slug": slug,
            "depth": depth,
            "focus": focus,
            "status": "initialized",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source_availability_ceiling": "unknown",
            "minimum_targets": depth_targets(depth),
            "notes": "Populate profile and source registry after identity/source reconnaissance."
        })

    registry_path = base / "source_registry.json"
    if not registry_path.exists():
        write_json(registry_path, [])

    queue_path = base / "PRIMARY_SOURCE_QUEUE.md"
    if not queue_path.exists():
        queue_path.write_text(
            f"# Primary Source Queue — {name}\n\n"
            "Add unresolved process-evidence objects here. A later historian quoting an object does not close the item; inspect the primary object or a faithful institutional scan/transcript.\n",
            encoding="utf-8"
        )

    return base


def validate_scholar(slug: str, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    base = scholar_dir(root, slug)
    if not base.exists():
        return [f"unknown scholar: {slug}"]

    profile_path = base / "scholar_profile.json"
    manifest_path = base / "distillation_manifest.json"
    registry_path = base / "source_registry.json"
    if not profile_path.exists():
        errors.append(f"{slug}: missing scholar_profile.json")
    if not manifest_path.exists():
        errors.append(f"{slug}: missing distillation_manifest.json")
    if not registry_path.exists():
        errors.append(f"{slug}: missing source_registry.json")
        return errors

    if profile_path.exists():
        profile = load_json(profile_path)
        miss = missing(profile, PROFILE_REQUIRED)
        if miss:
            errors.append(f"{slug}/scholar_profile.json missing: {', '.join(miss)}")
        if profile.get("slug") != slug:
            errors.append(f"{slug}: profile slug mismatch")
        if profile.get("depth") not in VALID_DEPTHS:
            errors.append(f"{slug}: invalid profile depth")
        if profile.get("source_availability_ceiling") not in VALID_CEILINGS:
            errors.append(f"{slug}: invalid source_availability_ceiling")

    source_items = load_json(registry_path)
    if not isinstance(source_items, list):
        errors.append(f"{slug}: source_registry.json must be an array")
        source_items = []
    source_ids = set()
    for i, src in enumerate(source_items):
        miss = missing(src, SOURCE_REQUIRED)
        if miss:
            errors.append(f"{slug}: source[{i}] missing: {', '.join(miss)}")
        sid = src.get("source_id")
        if sid in source_ids:
            errors.append(f"{slug}: duplicate source_id: {sid}")
        if sid:
            source_ids.add(sid)

    episodes = {}
    episode_dir = base / "episodes"
    if episode_dir.exists():
        for path in sorted(episode_dir.glob("*.json")):
            ep = load_json(path)
            miss = missing(ep, EPISODE_REQUIRED)
            if miss:
                errors.append(f"{slug}/{path.name} missing: {', '.join(miss)}")
            eid = ep.get("episode_id")
            if eid in episodes:
                errors.append(f"{slug}: duplicate episode_id: {eid}")
            if eid:
                episodes[eid] = ep
            for ref in ep.get("source_refs", []):
                if ref not in source_ids:
                    errors.append(f"{slug}/{eid}: unknown source_ref {ref}")
            if ep.get("evidence_strength") not in {"high", "medium", "low", "unknown"}:
                errors.append(f"{slug}/{eid}: invalid evidence_strength")

    heuristics = {}
    heuristic_dir = base / "heuristics"
    if heuristic_dir.exists():
        for path in sorted(heuristic_dir.glob("*.json")):
            h = load_json(path)
            miss = missing(h, HEURISTIC_REQUIRED)
            if miss:
                errors.append(f"{slug}/{path.name} missing: {', '.join(miss)}")
            hid = h.get("heuristic_id")
            if hid in heuristics:
                errors.append(f"{slug}: duplicate heuristic_id: {hid}")
            if hid:
                heuristics[hid] = h
            if h.get("status") not in {"candidate", "provisional", "validated", "rejected"}:
                errors.append(f"{slug}/{hid}: invalid status")
            for ref in h.get("supporting_episodes", []) + h.get("counter_episodes", []):
                if ref not in episodes:
                    errors.append(f"{slug}/{hid}: unknown episode ref {ref}")
            if h.get("status") == "validated" and not h.get("counter_episodes"):
                errors.append(f"{slug}/{hid}: validated heuristic requires counter_episodes")

    for eid, ep in episodes.items():
        for hid in ep.get("candidate_heuristics", []):
            if hid not in heuristics:
                errors.append(f"{slug}/{eid}: unknown candidate heuristic {hid}")
        for counter in ep.get("counter_episode_refs", []):
            if counter not in episodes:
                errors.append(f"{slug}/{eid}: unknown counter_episode_ref {counter}")

    return errors


def validate(root: Path = ROOT, scholar: str | None = None) -> list[str]:
    if scholar:
        return validate_scholar(scholar, root)
    errors: list[str] = []
    for slug in discover_scholar_slugs(root):
        errors.extend(validate_scholar(slug, root))
    return errors


def scholar_stats(slug: str, root: Path = ROOT) -> dict:
    base = scholar_dir(root, slug)
    if not base.exists():
        raise FileNotFoundError(slug)
    sources = load_json(base / "source_registry.json") if (base / "source_registry.json").exists() else []
    episodes = [load_json(p) for p in (base / "episodes").glob("*.json")] if (base / "episodes").exists() else []
    heuristics = [load_json(p) for p in (base / "heuristics").glob("*.json")] if (base / "heuristics").exists() else []
    profile = load_json(base / "scholar_profile.json") if (base / "scholar_profile.json").exists() else {}
    source_classes = {c: 0 for c in ("A", "B", "C", "D")}
    for src in sources:
        c = src.get("source_class")
        if c in source_classes:
            source_classes[c] += 1
    return {
        "scholar": slug,
        "canonical_name": profile.get("canonical_name"),
        "depth": profile.get("depth"),
        "source_availability_ceiling": profile.get("source_availability_ceiling"),
        "sources": len(sources),
        "sources_by_class": source_classes,
        "episodes": len(episodes),
        "episodes_needing_primary_review": sum(bool(e.get("needs_primary_source_review")) for e in episodes),
        "heuristics": len(heuristics),
        "validated_heuristics": sum(h.get("status") == "validated" for h in heuristics),
        "provisional_heuristics": sum(h.get("status") == "provisional" for h in heuristics),
        "candidate_heuristics": sum(h.get("status") == "candidate" for h in heuristics),
        "rejected_heuristics": sum(h.get("status") == "rejected" for h in heuristics),
        "contrastive_heuristics": sum(bool(h.get("counter_episodes")) for h in heuristics),
    }


def stats(root: Path = ROOT, scholar: str | None = None) -> dict:
    if scholar:
        return scholar_stats(scholar, root)
    scholar_stats_list = [scholar_stats(slug, root) for slug in discover_scholar_slugs(root)]
    return {
        "scholars": len(scholar_stats_list),
        "scholar_slugs": [s["scholar"] for s in scholar_stats_list],
        "sources": sum(s["sources"] for s in scholar_stats_list),
        "episodes": sum(s["episodes"] for s in scholar_stats_list),
        "heuristics": sum(s["heuristics"] for s in scholar_stats_list),
        "validated_heuristics": sum(s["validated_heuristics"] for s in scholar_stats_list),
        "provisional_heuristics": sum(s["provisional_heuristics"] for s in scholar_stats_list),
        "candidate_heuristics": sum(s["candidate_heuristics"] for s in scholar_stats_list),
    }


def build_skill(slug: str, root: Path = ROOT, output: Path | None = None) -> Path:
    errors = validate_scholar(slug, root)
    if errors:
        raise ValueError("cannot build invalid scholar data:\n" + "\n".join(errors))

    base = scholar_dir(root, slug)
    profile = load_json(base / "scholar_profile.json")
    heuristics = [load_json(p) for p in sorted((base / "heuristics").glob("*.json"))]
    out = output or (root / "generated" / f"{slug}-research-advisor")
    out.mkdir(parents=True, exist_ok=True)

    for filename in ("scholar_profile.json", "source_registry.json"):
        shutil.copy2(base / filename, out / filename)
    for dirname in ("episodes", "heuristics"):
        dest = out / dirname
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(base / dirname, dest)

    name = profile.get("canonical_name", slug)
    ceiling = profile.get("source_availability_ceiling", "unknown")
    heuristic_lines = []
    for h in heuristics:
        heuristic_lines.append(
            f"- `{h.get('status', 'candidate')}` — {h.get('name', h.get('heuristic_id'))}: {h.get('rule', '')}"
        )
    if not heuristic_lines:
        heuristic_lines = ["- No research heuristic has been distilled yet. Do not invent one."]

    skill_text = f'''---
name: {slug}-research-advisor
description: "Source-backed research judgment advisor distilled from public research materials associated with {name}. Use to audit research questions, hypotheses, study designs, anomalies, and continue/stop/pivot decisions using traceable Episodes and bounded heuristics. Never impersonate {name} or present transfer inference as their personal view."
---

# {name} · Research Advisor

This advisor was generated by ResearchMind. It is not {name}, is not authorized to speak for them, and must distinguish historical evidence from AI transfer.

## Evidence ceiling

`{ceiling}`

Never claim a reconstruction deeper than this evidence ceiling supports.

## Mandatory labels

- `DIRECT_EVIDENCE`
- `CROSS_SOURCE_SYNTHESIS`
- `TRANSFER_INFERENCE`
- `INSUFFICIENT_EVIDENCE`

## Research heuristics currently available

{chr(10).join(heuristic_lines)}

Read the full heuristic JSON before applying any rule. Always retrieve its supporting and counter Episodes.

## Advisor workflow

1. Classify the user's research decision.
2. Match only heuristics actually present in `heuristics/`.
3. Read supporting and counter Episodes from `episodes/`.
4. Run a transfer check: source structure, target structure, preserved constraints, broken assumptions, confidence.
5. Give the smallest useful next research action.
6. Cite the registered source/locator behind historical claims.
7. If evidence is insufficient, say so instead of completing the scholar's supposed opinion.

## Non-negotiable safeguards

- Apply the Temporal Firewall to historical reconstruction.
- Preserve team attribution.
- Do not convert retrospective memory into contemporaneous evidence.
- Do not claim that a famous researcher's method is universally optimal.
- Do not transfer substantive domain mechanisms by analogy alone.
'''
    (out / "SKILL.md").write_text(skill_text, encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(prog="researchmind")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init-scholar", help="create a universal scholar distillation workspace")
    p_init.add_argument("name")
    p_init.add_argument("--slug")
    p_init.add_argument("--depth", choices=sorted(VALID_DEPTHS), default="standard")
    p_init.add_argument("--focus")

    p_validate = sub.add_parser("validate", help="validate one scholar or every scholar")
    p_validate.add_argument("--scholar")

    p_stats = sub.add_parser("stats", help="show one scholar or repository-level stats")
    p_stats.add_argument("--scholar")

    p_build = sub.add_parser("build-skill", help="package a scholar dataset as a reusable advisor Skill")
    p_build.add_argument("--scholar", required=True)
    p_build.add_argument("--output")

    sub.add_parser("list-scholars", help="list initialized scholar slugs")

    args = parser.parse_args()

    if args.cmd == "init-scholar":
        base = init_scholar(args.name, args.slug, args.depth, args.focus)
        print(str(base.resolve()))
        return 0

    if args.cmd == "validate":
        errors = validate(ROOT, args.scholar)
        if errors:
            print("Validation failed:")
            for err in errors:
                print(f"- {err}")
            return 1
        print("Validation OK")
        return 0

    if args.cmd == "stats":
        print(json.dumps(stats(ROOT, args.scholar), ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "build-skill":
        output = Path(args.output) if args.output else None
        try:
            out = build_skill(args.scholar, ROOT, output)
        except (ValueError, FileNotFoundError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(str(out.resolve()))
        return 0

    if args.cmd == "list-scholars":
        for slug in discover_scholar_slugs(ROOT):
            print(slug)
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
