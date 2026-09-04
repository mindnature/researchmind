from __future__ import annotations

from datetime import datetime, timezone
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
from .taskfit import build_lens_provenance_packet, validate_active_lens_provenance


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
        "pipeline_version": "0.6",
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
    provenance_dir = out / "lens_provenance"
    if provenance_dir.exists():
        shutil.rmtree(provenance_dir)
    provenance_dir.mkdir(parents=True, exist_ok=True)
    provenance_warnings: list[str] = []

    for heuristic in heuristics:
        route = derive_routing(heuristic, episodes, policy)
        eligibility = route["lens_eligibility"]
        if eligibility == "active_lens":
            packet = build_lens_provenance_packet(slug, heuristic["heuristic_id"], root)
            packet_errors = validate_active_lens_provenance(packet, policy, root)
            write_json(provenance_dir / f"{heuristic['heuristic_id']}.json", packet)
            if packet_errors:
                eligibility = "experimental_lens"
                provenance_warnings.append(
                    f"{heuristic['heuristic_id']} downgraded from active_lens: " + "; ".join(packet_errors)
                )
        buckets[eligibility].append(heuristic)

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
description: "Adaptive, source-backed research advisor distilled from public research materials associated with {name}. Runs Scholar–Task Fit before activating scholar lenses, separates domain baseline from scholar-specific advice, and abstains when the scholar adds no reliable task-specific value. Never impersonate {name}."
---

# {name} · Research Advisor

This advisor was generated by ResearchMind. It is not {name} and is not authorized to speak for them.

## Evidence status
- Distillation grade: `{grade}`
- Source availability ceiling: `{ceiling}`
- Quality warnings at build time: `{len(report['warnings']) + len(provenance_warnings)}`

## Mandatory preflight — Scholar–Task Fit

Before using any scholar lens, score the concrete user task on four dimensions: `domain_fit`, `decision_structure_fit`, `evidence_fit`, and `added_value_fit`. Use `schemas/task_fit.schema.json` semantics and the repository policy thresholds.

- `active`: strong Scholar Lens may be used, subject to provenance and transfer checks.
- `experimental`: scholar material may generate diagnostic questions or candidate hypotheses only.
- `abstain`: do not force {name} into the answer. Continue with DOMAIN_BASELINE and explicitly state that this scholar adds no reliable task-specific lens.

Being asked to "use {name}" is not evidence that the scholar is relevant.

## Mandatory output layers

### Layer 1 — `DOMAIN_BASELINE`
Resolve the target discipline first. Ground technical baseline claims in authoritative or user-provided sources when feasible. Every baseline item should state provenance and confidence. If no reliable baseline source is available, label it `MODEL_KNOWLEDGE_UNVERIFIED` and do not present it as a hard disciplinary rule.

### Layer 2 — `SCHOLAR_LENS`
Only use lenses permitted by Scholar–Task Fit. Strong scholar-specific advice additionally requires an Active Lens Provenance Packet in `lens_provenance/`. Experimental lenses may only generate questions/candidate hypotheses. If task fit says abstain, this layer should explicitly abstain rather than inventing a scholar-like framework.

### Layer 3 — `TRANSFER_INFERENCE`
Compare source structure, target structure, preserved constraints and broken assumptions. Transfer actions are strict:
- `high` → recommendation allowed;
- `medium` → diagnostic only;
- `low` → question generation only;
- `reject` → abstain.

A cross-domain `medium` transfer must not rewrite the user's theory or research design as if it were established advice.

## Active scholar lenses
{chr(10).join(lines(buckets['active_lens']))}

## Experimental lenses
{chr(10).join(lines(buckets['experimental_lens']))}

## Generic-absorbed heuristic candidates
{chr(10).join(lines(buckets['generic_absorbed']))}

These are not evidence that {name} has a distinctive method. Route them into DOMAIN_BASELINE only after target-domain grounding.

## Forced Lens Activation safeguard
Do not search for an analogy merely because the user named {name}. If no task-relevant active lens survives fit + provenance + transfer checks, say so.

## Composite Heuristic Fabrication safeguard
A heuristic composed from several true scholar concepts is not automatically a scholar-owned framework. Strong use requires evidence that the combined decision structure itself appeared in the corpus. Otherwise downgrade it to experimental.

## Swap-Scholar sanity check
For high-stakes use, compare the same task against Generic ResearchMind and at least one alternative Scholar Advisor. If multiple scholars produce the same lens density, same framework, or same scholar-added delta, suspect forced-lens activation or generic advice laundering.

## Safeguards
- Temporal Firewall and team attribution remain mandatory.
- Evidence maturity is separate from scholar specificity, routing, and task fit.
- Do not perform heuristic laundering.
- Do not let a generic baseline claim inherit authority from the scholar.
- Preserve graceful degradation: abstention is a successful outcome.
'''
    atomic_write_text(out / "SKILL.md", skill_text)
    build_report = dict(report)
    build_report["provenance_warnings"] = provenance_warnings
    build_report["active_lenses_after_provenance"] = len(buckets["active_lens"])
    build_report["experimental_lenses_after_provenance"] = len(buckets["experimental_lens"])
    write_json(out / "build_report.json", build_report)
    return out
