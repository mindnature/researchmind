#!/usr/bin/env python3
"""ResearchMind: scaffold, validate, stage and package scholar distillations."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import unicodedata
import uuid

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
PROFILE_REQUIRED = {
    "canonical_name", "slug", "fields", "active_period", "major_research_programs",
    "major_contributions", "major_collaborators", "likely_archives", "source_availability",
    "source_availability_ceiling", "distillation_grade", "evidence_profile", "depth"
}
VALID_DEPTHS = {"quick", "standard", "deep", "golden"}
VALID_CEILINGS = {
    "publication_only", "public_retrospective", "process_evidence", "golden_archive", "unknown"
}
VALID_GRADES = {"A_archival", "B_process_informed", "C_retrospective", "D_publication_based", "unknown"}
ELIGIBLE_RESEARCH_EPISODE_TYPES = {
    "scientific_decision", "problem_framing", "method_choice", "anomaly_response", "theory_revision"
}
NON_RESEARCH_EPISODE_TYPES = {
    "career_decision", "research_program_strategy", "institution_building", "field_outcome"
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex[:8]}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def write_json(path: Path, obj) -> None:
    atomic_write_text(path, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


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
    return [p.name for p in sorted(data_root.iterdir()) if p.is_dir() and (p / "source_registry.json").exists()]


def depth_targets(depth: str) -> dict:
    return {
        "quick": {"sources": "5-10", "episodes": 3, "contrastive_pairs": 0, "heuristics": "1-3"},
        "standard": {"sources": "20-40", "episodes": 5, "contrastive_pairs": 2, "heuristics": "3-7"},
        "deep": {"sources": "quality-driven", "episodes": 8, "contrastive_pairs": 2, "heuristics": "evidence-driven"},
        "golden": {"sources": "primary-source-driven", "episodes": 3, "contrastive_pairs": 1, "heuristics": "validation-driven"},
    }[depth]


def default_evidence_profile() -> dict:
    return {
        "contemporaneous_process_coverage": "unknown",
        "publication_coverage": "unknown",
        "first_person_retrospective_coverage": "unknown",
        "third_party_dependency": "unknown",
        "micro_decision_reconstruction": "unknown",
        "research_program_reconstruction": "unknown",
        "notes": "Update after source reconnaissance."
    }


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
                "process_primary": "unknown", "publications": "unknown",
                "retrospectives": "unknown", "third_party_history": "unknown"
            },
            "source_availability_ceiling": "unknown",
            "distillation_grade": "unknown",
            "distillation_grade_rationale": "",
            "evidence_profile": default_evidence_profile(),
            "identity_disambiguation_notes": "",
            "focus": focus,
            "depth": depth
        })

    manifest_path = base / "distillation_manifest.json"
    if not manifest_path.exists():
        write_json(manifest_path, {
            "manifest_version": "0.4",
            "scholar": name,
            "slug": slug,
            "depth": depth,
            "focus": focus,
            "status": "initialized",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source_availability_ceiling": "unknown",
            "distillation_grade": "unknown",
            "minimum_targets": depth_targets(depth),
            "notes": "Populate profile and source registry after identity/source reconnaissance."
        })

    if not (base / "source_registry.json").exists():
        write_json(base / "source_registry.json", [])
    if not (base / "PRIMARY_SOURCE_QUEUE.md").exists():
        atomic_write_text(
            base / "PRIMARY_SOURCE_QUEUE.md",
            f"# Primary Source Queue — {name}\n\n"
            "Add unresolved process-evidence objects here. A later historian quoting an object does not close the item; inspect the primary object or a faithful institutional scan/transcript.\n"
        )
    return base


def validate_specificity(hid: str, h: dict, errors: list[str], slug: str) -> None:
    spec = h.get("specificity")
    if h.get("status") == "validated" and not spec:
        errors.append(f"{slug}/{hid}: validated heuristic requires specificity gate")
        return
    if not spec:
        return
    required = {
        "status", "generic_baseline_overlap", "scholar_specificity",
        "framework_contamination", "scholar_added_delta", "specificity_evidence"
    }
    miss = missing(spec, required)
    if miss:
        errors.append(f"{slug}/{hid}: specificity missing: {', '.join(miss)}")
        return
    if spec.get("status") == "pass":
        if spec.get("scholar_specificity") != "high":
            errors.append(f"{slug}/{hid}: specificity pass requires scholar_specificity=high")
        if spec.get("generic_baseline_overlap") == "high":
            errors.append(f"{slug}/{hid}: specificity pass cannot have high generic baseline overlap")
        if spec.get("framework_contamination") not in {"low", "medium"}:
            errors.append(f"{slug}/{hid}: specificity pass requires low/medium framework contamination")
        if not str(spec.get("scholar_added_delta", "")).strip():
            errors.append(f"{slug}/{hid}: specificity pass requires scholar_added_delta")
        if len(spec.get("specificity_evidence", [])) < 2:
            errors.append(f"{slug}/{hid}: specificity pass requires at least two evidence statements")
    if h.get("status") == "validated" and spec.get("status") != "pass":
        errors.append(f"{slug}/{hid}: validated heuristic must pass scholar specificity gate")


def validate_scholar(slug: str, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    base = scholar_dir(root, slug)
    if not base.exists():
        return [f"unknown scholar: {slug}"]

    profile_path = base / "scholar_profile.json"
    manifest_path = base / "distillation_manifest.json"
    registry_path = base / "source_registry.json"
    for path in (profile_path, manifest_path, registry_path):
        if not path.exists():
            errors.append(f"{slug}: missing {path.name}")
    if not registry_path.exists():
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
        if profile.get("distillation_grade") not in VALID_GRADES:
            errors.append(f"{slug}: invalid distillation_grade")

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

    episodes: dict[str, dict] = {}
    for path in sorted((base / "episodes").glob("*.json")) if (base / "episodes").exists() else []:
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
        if ep.get("episode_type") in NON_RESEARCH_EPISODE_TYPES and ep.get("candidate_heuristics"):
            errors.append(f"{slug}/{eid}: non-research episode cannot directly generate research heuristics")

    heuristics: dict[str, dict] = {}
    for path in sorted((base / "heuristics").glob("*.json")) if (base / "heuristics").exists() else []:
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
        if hid:
            validate_specificity(hid, h, errors, slug)

    for eid, ep in episodes.items():
        for hid in ep.get("candidate_heuristics", []):
            if hid not in heuristics:
                errors.append(f"{slug}/{eid}: unknown candidate heuristic {hid}")
        for counter in ep.get("counter_episode_refs", []):
            if counter not in episodes:
                errors.append(f"{slug}/{eid}: unknown counter_episode_ref {counter}")
    return errors


def epistemic_validate_scholar(slug: str, root: Path = ROOT) -> list[str]:
    errors = validate_scholar(slug, root)
    if errors:
        return errors
    base = scholar_dir(root, slug)
    sources = {s["source_id"]: s for s in load_json(base / "source_registry.json")}
    episodes = [load_json(p) for p in sorted((base / "episodes").glob("*.json"))]
    heuristics = [load_json(p) for p in sorted((base / "heuristics").glob("*.json"))]

    for src in sources.values():
        if src.get("source_class") == "A" and src.get("claim_bearing") is True:
            if src.get("inspection_status") != "inspected" or not src.get("stable_locator"):
                errors.append(f"{slug}/{src.get('source_id')}: claim-bearing A source must be inspected with stable locator")
    for ep in episodes:
        if ep.get("evidence_strength") == "high":
            inspected_primary = any(
                sources.get(ref, {}).get("inspection_status") == "inspected"
                and sources.get(ref, {}).get("source_class") in {"A", "B"}
                for ref in ep.get("source_refs", [])
            )
            if not inspected_primary:
                errors.append(f"{slug}/{ep.get('episode_id')}: high evidence requires an inspected A/B source")
    ep_by_id = {e.get("episode_id"): e for e in episodes}
    for h in heuristics:
        if h.get("status") == "validated":
            for ref in h.get("supporting_episodes", []) + h.get("counter_episodes", []):
                et = ep_by_id.get(ref, {}).get("episode_type", "legacy_unspecified")
                if et not in ELIGIBLE_RESEARCH_EPISODE_TYPES:
                    errors.append(f"{slug}/{h.get('heuristic_id')}: validated research heuristic uses ineligible episode type {et}")
    return errors


def validate(root: Path = ROOT, scholar: str | None = None, epistemic: bool = False) -> list[str]:
    fn = epistemic_validate_scholar if epistemic else validate_scholar
    if scholar:
        return fn(scholar, root)
    errors: list[str] = []
    for slug in discover_scholar_slugs(root):
        errors.extend(fn(slug, root))
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
    inspected_classes = {c: 0 for c in ("A", "B", "C", "D")}
    claim_bearing_classes = {c: 0 for c in ("A", "B", "C", "D")}
    for src in sources:
        c = src.get("source_class")
        if c in source_classes:
            source_classes[c] += 1
            if src.get("inspection_status") == "inspected":
                inspected_classes[c] += 1
            if src.get("claim_bearing") is True:
                claim_bearing_classes[c] += 1
    specificity = {"pass": 0, "review": 0, "reject": 0, "not_tested": 0, "missing": 0}
    for h in heuristics:
        s = h.get("specificity", {}).get("status")
        specificity[s if s in specificity else "missing"] += 1
    return {
        "scholar": slug,
        "canonical_name": profile.get("canonical_name"),
        "depth": profile.get("depth"),
        "source_availability_ceiling": profile.get("source_availability_ceiling"),
        "distillation_grade": profile.get("distillation_grade"),
        "sources": len(sources),
        "sources_by_class": source_classes,
        "inspected_sources_by_class": inspected_classes,
        "claim_bearing_sources_by_class": claim_bearing_classes,
        "episodes": len(episodes),
        "episodes_needing_primary_review": sum(bool(e.get("needs_primary_source_review")) for e in episodes),
        "heuristics": len(heuristics),
        "validated_heuristics": sum(h.get("status") == "validated" for h in heuristics),
        "provisional_heuristics": sum(h.get("status") == "provisional" for h in heuristics),
        "candidate_heuristics": sum(h.get("status") == "candidate" for h in heuristics),
        "specificity_gate": specificity
    }


def stats(root: Path = ROOT, scholar: str | None = None) -> dict:
    if scholar:
        return scholar_stats(scholar, root)
    all_stats = [scholar_stats(slug, root) for slug in discover_scholar_slugs(root)]
    return {
        "scholars": len(all_stats),
        "scholar_slugs": [s["scholar"] for s in all_stats],
        "sources": sum(s["sources"] for s in all_stats),
        "episodes": sum(s["episodes"] for s in all_stats),
        "heuristics": sum(s["heuristics"] for s in all_stats),
        "validated_heuristics": sum(s["validated_heuristics"] for s in all_stats)
    }


def staging_root(root: Path, job_id: str) -> Path:
    return root / ".researchmind" / "staging" / job_id


def stage_scholar(name: str, job_id: str | None = None, slug: str | None = None,
                  depth: str = "standard", focus: str | None = None, root: Path = ROOT) -> tuple[str, Path]:
    job_id = job_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    slug = slug or slugify(name)
    job_root = staging_root(root, job_id)
    staged = scholar_dir(job_root, slug)
    if staged.exists():
        raise FileExistsError(f"staging scholar already exists: {job_id}/{slug}")
    current = scholar_dir(root, slug)
    if current.exists():
        staged.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(current, staged)
    else:
        init_scholar(name, slug, depth, focus, root=job_root)
    write_json(job_root / "job.json", {
        "job_id": job_id, "scholar": name, "slug": slug,
        "created_at": datetime.now(timezone.utc).isoformat(), "status": "staged"
    })
    write_json(job_root / "checkpoint.json", {
        "phase": "staged", "validated": False, "epistemic_validated": False
    })
    return job_id, staged


def commit_staged(job_id: str, slug: str, root: Path = ROOT) -> Path:
    job_root = staging_root(root, job_id)
    staged = scholar_dir(job_root, slug)
    if not staged.exists():
        raise FileNotFoundError(f"staged scholar not found: {job_id}/{slug}")
    errors = epistemic_validate_scholar(slug, job_root)
    if errors:
        write_json(job_root / "errors.json", {"errors": errors})
        raise ValueError("staged scholar failed validation:\n" + "\n".join(errors))
    write_json(job_root / "checkpoint.json", {
        "phase": "validated", "validated": True, "epistemic_validated": True
    })

    dest = scholar_dir(root, slug)
    temp_dest = dest.parent / f".{slug}.new-{job_id}"
    backup = root / ".researchmind" / "backups" / job_id / slug
    if temp_dest.exists():
        shutil.rmtree(temp_dest)
    temp_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(staged, temp_dest)
    try:
        if dest.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            if backup.exists():
                shutil.rmtree(backup)
            shutil.move(str(dest), str(backup))
        os.replace(temp_dest, dest)
    except Exception:
        if temp_dest.exists():
            shutil.rmtree(temp_dest)
        if backup.exists() and not dest.exists():
            shutil.move(str(backup), str(dest))
        raise
    write_json(job_root / "checkpoint.json", {
        "phase": "committed", "validated": True, "epistemic_validated": True,
        "committed_at": datetime.now(timezone.utc).isoformat()
    })
    return dest


def abort_staged(job_id: str, root: Path = ROOT) -> None:
    job_root = staging_root(root, job_id)
    if job_root.exists():
        shutil.rmtree(job_root)


def build_skill(slug: str, root: Path = ROOT, output: Path | None = None) -> Path:
    errors = epistemic_validate_scholar(slug, root)
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
    grade = profile.get("distillation_grade", "unknown")
    ceiling = profile.get("source_availability_ceiling", "unknown")
    passed = [h for h in heuristics if h.get("specificity", {}).get("status") == "pass" and h.get("status") != "rejected"]
    experimental = [h for h in heuristics if h not in passed and h.get("status") != "rejected"]
    passed_lines = [f"- `{h.get('status')}` — {h.get('name')}: {h.get('rule')}" for h in passed] or ["- None yet. Do not invent scholar-specific heuristics."]
    experimental_lines = [f"- `{h.get('status')}` / specificity `{h.get('specificity', {}).get('status', 'missing')}` — {h.get('name')}" for h in experimental] or ["- None."]

    skill_text = f'''---
name: {slug}-research-advisor
description: "Source-backed research judgment advisor distilled from public research materials associated with {name}. Separates domain-baseline review from scholar-specific epistemic lenses and transfer inference. Never impersonate {name}."
---

# {name} · Research Advisor

This advisor was generated by ResearchMind. It is not {name} and is not authorized to speak for them.

## Evidence status

- Distillation grade: `{grade}`
- Source availability ceiling: `{ceiling}`

Never claim a reconstruction deeper than these limits support.

## Mandatory labels

- `DOMAIN_BASELINE`
- `SCHOLAR_LENS`
- `TRANSFER_INFERENCE`
- `DIRECT_EVIDENCE`
- `CROSS_SOURCE_SYNTHESIS`
- `INSUFFICIENT_EVIDENCE`

## Scholar-specific heuristics that passed the specificity gate

{chr(10).join(passed_lines)}

## Experimental / not-yet-specificity-validated heuristics

{chr(10).join(experimental_lines)}

Do not present experimental heuristics as uniquely characteristic of {name}.

## Three-layer Advisor workflow

### Layer 1 — DOMAIN_BASELINE
Audit the user's work using the target discipline's ordinary standards. Explicitly state that these points do not come from {name}. Do not attach scholar heuristic IDs to generic domain rules.

### Layer 2 — SCHOLAR_LENS
Use only heuristics that passed the scholar-specificity gate for strong scholar-specific advice. Retrieve the supporting and counter Episodes. State the scholar-added delta: what this lens adds beyond a competent generic research advisor.

### Layer 3 — TRANSFER_INFERENCE
Compare source structure, target structure, preserved constraints and broken assumptions. Return `high / medium / low / reject`. If confidence is low, use the lens only to generate questions, not recommendations.

## Safeguards

- Apply the Temporal Firewall to historical reconstruction.
- Preserve team attribution.
- Do not convert retrospective memory into contemporaneous evidence.
- Do not perform heuristic laundering: generic academic standards must stay in DOMAIN_BASELINE.
- Do not transfer domain mechanisms merely because the analogy sounds scholar-like.
- If evidence or specificity is insufficient, say so.
'''
    atomic_write_text(out / "SKILL.md", skill_text)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(prog="researchmind")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init-scholar")
    p_init.add_argument("name"); p_init.add_argument("--slug"); p_init.add_argument("--depth", choices=sorted(VALID_DEPTHS), default="standard"); p_init.add_argument("--focus")
    p_stage = sub.add_parser("stage-scholar")
    p_stage.add_argument("name"); p_stage.add_argument("--job-id"); p_stage.add_argument("--slug"); p_stage.add_argument("--depth", choices=sorted(VALID_DEPTHS), default="standard"); p_stage.add_argument("--focus")
    p_commit = sub.add_parser("commit-staged")
    p_commit.add_argument("--job-id", required=True); p_commit.add_argument("--scholar", required=True)
    p_abort = sub.add_parser("abort-staged"); p_abort.add_argument("--job-id", required=True)
    p_validate = sub.add_parser("validate"); p_validate.add_argument("--scholar")
    p_epi = sub.add_parser("epistemic-validate"); p_epi.add_argument("--scholar")
    p_stats = sub.add_parser("stats"); p_stats.add_argument("--scholar")
    p_build = sub.add_parser("build-skill"); p_build.add_argument("--scholar", required=True); p_build.add_argument("--output")
    sub.add_parser("list-scholars")
    args = parser.parse_args()

    try:
        if args.cmd == "init-scholar":
            print(init_scholar(args.name, args.slug, args.depth, args.focus).resolve()); return 0
        if args.cmd == "stage-scholar":
            job_id, base = stage_scholar(args.name, args.job_id, args.slug, args.depth, args.focus)
            print(json.dumps({"job_id": job_id, "path": str(base.resolve())}, ensure_ascii=False)); return 0
        if args.cmd == "commit-staged":
            print(commit_staged(args.job_id, args.scholar).resolve()); return 0
        if args.cmd == "abort-staged":
            abort_staged(args.job_id); return 0
        if args.cmd in {"validate", "epistemic-validate"}:
            errors = validate(ROOT, args.scholar, epistemic=args.cmd == "epistemic-validate")
            if errors:
                print("Validation failed:")
                for err in errors: print(f"- {err}")
                return 1
            print("Validation OK"); return 0
        if args.cmd == "stats":
            print(json.dumps(stats(ROOT, args.scholar), ensure_ascii=False, indent=2)); return 0
        if args.cmd == "build-skill":
            out = build_skill(args.scholar, ROOT, Path(args.output) if args.output else None)
            print(out.resolve()); return 0
        if args.cmd == "list-scholars":
            print("\n".join(discover_scholar_slugs(ROOT))); return 0
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        print(str(exc), file=sys.stderr); return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
