from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import uuid

from .core import (
    ROOT,
    apply_soft_routing,
    atomic_write_text,
    init_scholar,
    load_json,
    quality_report_scholar,
    scholar_dir,
    slugify,
    write_json,
)
from .policy import derive_routing, lens_family_for, load_policy


def staging_root(root: Path, job_id: str) -> Path:
    return root / ".researchmind" / "staging" / job_id


def stage_scholar(name: str, job_id: str | None = None, slug: str | None = None,
                  depth: str = "standard", focus: str | None = None,
                  root: Path = ROOT) -> tuple[str, Path]:
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
        "job_id": job_id,
        "scholar": name,
        "slug": slug,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "staged"
    })
    write_json(job_root / "checkpoint.json", {
        "phase": "staged",
        "validated": False,
        "quality_checked": False
    })
    return job_id, staged


def auto_distill(name: str, mode: str = "fast-auto", focus: str | None = None,
                 slug: str | None = None, root: Path = ROOT) -> dict:
    policy = load_policy(root)
    if mode not in policy.get("auto_modes", {}):
        raise ValueError(f"invalid auto mode: {mode}")
    depth = policy["auto_modes"][mode]["depth"]
    job_id, staged = stage_scholar(name, slug=slug, depth=depth, focus=focus, root=root)
    phases = [{"name": phase, "status": "pending", "note": ""} for phase in policy.get("pipeline_phases", [])]
    if phases:
        phases[0]["status"] = "ready"
    pipeline = {
        "pipeline_version": "0.5",
        "job_id": job_id,
        "scholar": name,
        "slug": staged.name,
        "mode": mode,
        "depth": depth,
        "agent_required": True,
        "agent_contract": "CLI manages workspace/state/validation. Installed ResearchMind agent performs web/file retrieval, source inspection and LLM synthesis.",
        "phases": phases,
        "current_phase": phases[0]["name"] if phases else None,
        "status": "awaiting_agent",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    write_json(staging_root(root, job_id) / "pipeline.json", pipeline)
    return pipeline


def update_pipeline(job_id: str, phase: str, status: str, note: str = "",
                    root: Path = ROOT) -> dict:
    path = staging_root(root, job_id) / "pipeline.json"
    if not path.exists():
        raise FileNotFoundError(f"pipeline not found: {job_id}")
    pipeline = load_json(path)
    found = False
    for item in pipeline.get("phases", []):
        if item.get("name") == phase:
            item["status"] = status
            item["note"] = note
            found = True
            break
    if not found:
        raise ValueError(f"unknown pipeline phase: {phase}")
    pipeline["current_phase"] = phase
    pipeline["updated_at"] = datetime.now(timezone.utc).isoformat()
    if status == "failed":
        pipeline["status"] = "attention_required"
    elif all(item.get("status") in {"completed", "skipped", "warning"} for item in pipeline.get("phases", [])):
        pipeline["status"] = "completed"
    else:
        pipeline["status"] = "running"
    write_json(path, pipeline)
    return pipeline


def commit_staged(job_id: str, slug: str, root: Path = ROOT) -> Path:
    job_root = staging_root(root, job_id)
    staged = scholar_dir(job_root, slug)
    if not staged.exists():
        raise FileNotFoundError(f"staged scholar not found: {job_id}/{slug}")

    apply_soft_routing(slug, job_root)
    report = quality_report_scholar(slug, job_root)
    write_json(job_root / "quality_report.json", report)
    if report["errors"]:
        write_json(job_root / "errors.json", {"errors": report["errors"]})
        raise ValueError("staged scholar failed blocking validation:\n" + "\n".join(report["errors"]))

    write_json(job_root / "checkpoint.json", {
        "phase": "quality_checked",
        "validated": True,
        "quality_checked": True,
        "warnings": len(report["warnings"])
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
        "phase": "committed",
        "validated": True,
        "quality_checked": True,
        "warnings": len(report["warnings"]),
        "committed_at": datetime.now(timezone.utc).isoformat()
    })
    return dest


def abort_staged(job_id: str, root: Path = ROOT) -> None:
    path = staging_root(root, job_id)
    if path.exists():
        shutil.rmtree(path)


def build_skill(slug: str, root: Path = ROOT, output: Path | None = None) -> Path:
    report = quality_report_scholar(slug, root)
    if report["errors"]:
        raise ValueError("cannot build scholar with blocking validation errors:\n" + "\n".join(report["errors"]))

    base = scholar_dir(root, slug)
    profile = load_json(base / "scholar_profile.json")
    heuristics = [load_json(path) for path in sorted((base / "heuristics").glob("*.json"))]
    episodes = {
        ep["episode_id"]: ep
        for ep in [load_json(path) for path in sorted((base / "episodes").glob("*.json"))]
    }
    policy = load_policy(root)
    out = output or (root / "generated" / f"{slug}-research-advisor")
    out.mkdir(parents=True, exist_ok=True)

    for filename in ("scholar_profile.json", "source_registry.json"):
        shutil.copy2(base / filename, out / filename)
    for dirname in ("episodes", "heuristics"):
        dest = out / dirname
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(base / dirname, dest)

    buckets = {"active_lens": [], "experimental_lens": [], "generic_absorbed": [], "excluded": []}
    for heuristic in heuristics:
        route = derive_routing(heuristic, episodes, policy)
        buckets[route["lens_eligibility"]].append(heuristic)

    name = profile.get("canonical_name", slug)
    grade = profile.get("distillation_grade", "unknown")
    ceiling = profile.get("source_availability_ceiling", "unknown")

    def lines(items: list[dict]) -> list[str]:
        return [
            f"- `{lens_family_for(h, policy)}` / `{h.get('status')}` — {h.get('name')}: {h.get('rule')}"
            for h in items
        ] or ["- None."]

    skill_text = f'''---
name: {slug}-research-advisor
description: "Adaptive, source-backed research advisor distilled from public research materials associated with {name}. Separates source-backed domain baselines, scholar-specific lenses and transfer inference. Never impersonate {name}."
---

# {name} · Research Advisor

This advisor was generated by ResearchMind. It is not {name} and is not authorized to speak for them.

## Evidence status
- Distillation grade: `{grade}`
- Source availability ceiling: `{ceiling}`
- Quality warnings at build time: `{len(report['warnings'])}`

## Mandatory output layers

### Layer 1 — `DOMAIN_BASELINE`
Resolve the target discipline first. Ground technical baseline claims in authoritative or user-provided sources when feasible. Every baseline item should state provenance and confidence. If no reliable baseline source is available, label it `MODEL_KNOWLEDGE_UNVERIFIED` and do not present it as a hard disciplinary rule. Generic-absorbed heuristics are only baseline candidates; they require target-domain grounding before use.

### Layer 2 — `SCHOLAR_LENS`
Use only active lenses for strong scholar-specific advice. Experimental lenses may generate questions but must be labeled experimental. If there are zero active lenses, disclose lens scarcity instead of fabricating personality-specific advice.

### Layer 3 — `TRANSFER_INFERENCE`
Compare source structure, target structure, preserved constraints and broken assumptions. `low` means question generation only; `reject` means do not use the analogy.

## Active scholar lenses
{chr(10).join(lines(buckets['active_lens']))}

## Experimental lenses
{chr(10).join(lines(buckets['experimental_lens']))}

## Generic-absorbed heuristic candidates
{chr(10).join(lines(buckets['generic_absorbed']))}

These are not evidence that {name} has a distinctive method. Route them into DOMAIN_BASELINE only after domain-specific grounding.

## Safeguards
- Temporal Firewall and team attribution remain mandatory.
- Evidence maturity (`candidate/provisional/validated`) is separate from scholar specificity and routing.
- Do not perform heuristic laundering.
- Do not let a generic baseline claim inherit authority from the scholar.
- Preserve graceful degradation: a sparse Scholar Lens is preferable to a fabricated one.
'''
    atomic_write_text(out / "SKILL.md", skill_text)
    write_json(out / "build_report.json", report)
    return out
