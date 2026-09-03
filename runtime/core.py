from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import unicodedata
import uuid

from .policy import derive_routing, load_policy

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
VALID_HEURISTIC_STATUS = {"candidate", "provisional", "validated", "rejected"}
VALID_SPECIFICITY_STATUS = {"not_tested", "pass", "review", "reject"}
VALID_ROUTING = {"active_lens", "experimental_lens", "generic_absorbed", "excluded"}


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
    return f"scholar-{hashlib.sha1(name.encode('utf-8')).hexdigest()[:10]}"


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

    if not (base / "scholar_profile.json").exists():
        write_json(base / "scholar_profile.json", {
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
            "distillation_grade": "unknown",
            "distillation_grade_rationale": "",
            "evidence_profile": default_evidence_profile(),
            "identity_disambiguation_notes": "",
            "focus": focus,
            "depth": depth
        })

    if not (base / "distillation_manifest.json").exists():
        write_json(base / "distillation_manifest.json", {
            "manifest_version": "0.5",
            "scholar": name,
            "slug": slug,
            "depth": depth,
            "focus": focus,
            "status": "initialized",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source_availability_ceiling": "unknown",
            "distillation_grade": "unknown",
            "minimum_targets": depth_targets(depth),
            "notes": "Adaptive pipeline: warnings degrade capabilities instead of blocking publication."
        })

    if not (base / "source_registry.json").exists():
        write_json(base / "source_registry.json", [])
    if not (base / "PRIMARY_SOURCE_QUEUE.md").exists():
        atomic_write_text(
            base / "PRIMARY_SOURCE_QUEUE.md",
            f"# Primary Source Queue — {name}\n\nAdd unresolved process-evidence objects here.\n"
        )
    return base


def specificity_shape_errors(hid: str, heuristic: dict, slug: str) -> list[str]:
    errors: list[str] = []
    spec = heuristic.get("specificity")
    if not spec:
        return errors
    required = {
        "status", "generic_baseline_overlap", "scholar_specificity",
        "framework_contamination", "scholar_added_delta", "specificity_evidence"
    }
    miss = missing(spec, required)
    if miss:
        errors.append(f"{slug}/{hid}: specificity missing: {', '.join(miss)}")
    if spec.get("status") not in VALID_SPECIFICITY_STATUS:
        errors.append(f"{slug}/{hid}: invalid specificity status")
    return errors


def validate_specificity(hid: str, heuristic: dict, errors: list[str], slug: str) -> None:
    """Backward-compatible structural check. Specificity quality is soft-gated in v0.5."""
    errors.extend(specificity_shape_errors(hid, heuristic, slug))


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
    source_ids: set[str] = set()
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
        if h.get("status") not in VALID_HEURISTIC_STATUS:
            errors.append(f"{slug}/{hid}: invalid status")
        for ref in h.get("supporting_episodes", []) + h.get("counter_episodes", []):
            if ref not in episodes:
                errors.append(f"{slug}/{hid}: unknown episode ref {ref}")
        if hid:
            errors.extend(specificity_shape_errors(hid, h, slug))
        route = h.get("routing")
        if route and route.get("lens_eligibility") not in VALID_ROUTING:
            errors.append(f"{slug}/{hid}: invalid routing lens_eligibility")

    for eid, ep in episodes.items():
        for hid in ep.get("candidate_heuristics", []):
            if hid not in heuristics:
                errors.append(f"{slug}/{eid}: unknown candidate heuristic {hid}")
        for counter in ep.get("counter_episode_refs", []):
            if counter not in episodes:
                errors.append(f"{slug}/{eid}: unknown counter_episode_ref {counter}")
    return errors


def apply_soft_routing(slug: str, root: Path = ROOT) -> int:
    base = scholar_dir(root, slug)
    policy = load_policy(root)
    episodes = {
        ep["episode_id"]: ep
        for ep in [load_json(p) for p in sorted((base / "episodes").glob("*.json"))]
    }
    changed = 0
    for path in sorted((base / "heuristics").glob("*.json")):
        h = load_json(path)
        route = derive_routing(h, episodes, policy)
        routing = {k: route[k] for k in ("lens_eligibility", "destination", "reason")}
        if h.get("lens_family") != route["lens_family"] or h.get("routing") != routing:
            h["lens_family"] = route["lens_family"]
            h["routing"] = routing
            write_json(path, h)
            changed += 1
    return changed


def quality_report_scholar(slug: str, root: Path = ROOT) -> dict:
    errors = validate_scholar(slug, root)
    warnings: list[str] = []
    info: list[str] = []
    if errors:
        return {"scholar": slug, "errors": errors, "warnings": warnings, "info": info, "active_lenses": 0}

    base = scholar_dir(root, slug)
    policy = load_policy(root)
    sources = {s["source_id"]: s for s in load_json(base / "source_registry.json")}
    episodes = [load_json(p) for p in sorted((base / "episodes").glob("*.json"))]
    ep_by_id = {e.get("episode_id"): e for e in episodes}
    heuristics = [load_json(p) for p in sorted((base / "heuristics").glob("*.json"))]
    profile = load_json(base / "scholar_profile.json")

    for src in sources.values():
        if src.get("source_class") == "A" and src.get("claim_bearing") is True:
            if src.get("inspection_status") != "inspected" or not src.get("stable_locator"):
                errors.append(
                    f"{slug}/{src.get('source_id')}: claim-bearing A source must be inspected with stable locator"
                )

    for ep in episodes:
        if ep.get("evidence_strength") == "high":
            inspected_primary = any(
                sources.get(ref, {}).get("inspection_status") == "inspected"
                and sources.get(ref, {}).get("source_class") in {"A", "B"}
                for ref in ep.get("source_refs", [])
            )
            if not inspected_primary:
                errors.append(f"{slug}/{ep.get('episode_id')}: high evidence requires an inspected A/B source")
        if ep.get("episode_type") in policy.get("excluded_episode_types", []) and ep.get("candidate_heuristics"):
            warnings.append(
                f"{slug}/{ep.get('episode_id')}: excluded episode type cannot produce active scholar lenses; downstream heuristics will be downgraded"
            )

    active = 0
    for h in heuristics:
        hid = h.get("heuristic_id")
        spec = h.get("specificity") or {}
        route = derive_routing(h, ep_by_id, policy)
        if route["lens_eligibility"] == "active_lens":
            active += 1
        if h.get("status") == "validated" and not h.get("counter_episodes"):
            warnings.append(
                f"{slug}/{hid}: validated heuristic has no counter episode; boundary validation remains incomplete"
            )
        if h.get("status") == "validated" and spec.get("status") != "pass":
            warnings.append(
                f"{slug}/{hid}: evidence-validated but not scholar-specific; routed away from active scholar lens"
            )
        if route["lens_eligibility"] == "generic_absorbed":
            warnings.append(f"{slug}/{hid}: heuristic absorbed as generic baseline candidate ({route['reason']})")
        elif route["lens_eligibility"] == "experimental_lens":
            info.append(f"{slug}/{hid}: experimental lens ({route['reason']})")

    if active == 0:
        warnings.append(f"{slug}: no active scholar-specific lens; advisor must disclose lens scarcity")

    grade = profile.get("distillation_grade", "unknown")
    if grade in {"C_retrospective", "D_publication_based"}:
        info.append(f"{slug}: {grade} corpus; micro-decision reconstruction confidence should remain limited")

    return {
        "scholar": slug,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "active_lenses": active
    }


def validate(root: Path = ROOT, scholar: str | None = None, epistemic: bool = False) -> list[str]:
    """Structural validation. epistemic=True is retained as a compatibility alias for blocking quality errors only."""
    slugs = [scholar] if scholar else discover_scholar_slugs(root)
    if not epistemic:
        errors: list[str] = []
        for slug in slugs:
            errors.extend(validate_scholar(slug, root))
        return errors
    report = quality_report(root, scholar)
    return report["errors"]


def quality_report(root: Path = ROOT, scholar: str | None = None) -> dict:
    slugs = [scholar] if scholar else discover_scholar_slugs(root)
    reports = [quality_report_scholar(slug, root) for slug in slugs]
    return {
        "reports": reports,
        "errors": [e for r in reports for e in r["errors"]],
        "warnings": [w for r in reports for w in r["warnings"]],
        "info": [i for r in reports for i in r["info"]]
    }


def scholar_stats(slug: str, root: Path = ROOT) -> dict:
    base = scholar_dir(root, slug)
    if not base.exists():
        raise FileNotFoundError(slug)
    sources = load_json(base / "source_registry.json") if (base / "source_registry.json").exists() else []
    episodes = [load_json(p) for p in (base / "episodes").glob("*.json")] if (base / "episodes").exists() else []
    heuristics = [load_json(p) for p in (base / "heuristics").glob("*.json")] if (base / "heuristics").exists() else []
    profile = load_json(base / "scholar_profile.json") if (base / "scholar_profile.json").exists() else {}
    policy = load_policy(root)

    source_classes = {c: 0 for c in "ABCD"}
    inspected = {c: 0 for c in "ABCD"}
    claim_bearing = {c: 0 for c in "ABCD"}
    for src in sources:
        c = src.get("source_class")
        if c in source_classes:
            source_classes[c] += 1
            if src.get("inspection_status") == "inspected":
                inspected[c] += 1
            if src.get("claim_bearing") is True:
                claim_bearing[c] += 1

    routes = {k: 0 for k in VALID_ROUTING}
    families = {k: 0 for k in policy.get("lens_families", {})}
    ep_by_id = {e.get("episode_id"): e for e in episodes}
    for h in heuristics:
        route = derive_routing(h, ep_by_id, policy)
        routes[route["lens_eligibility"]] += 1
        families[route["lens_family"]] = families.get(route["lens_family"], 0) + 1

    return {
        "scholar": slug,
        "canonical_name": profile.get("canonical_name"),
        "depth": profile.get("depth"),
        "source_availability_ceiling": profile.get("source_availability_ceiling"),
        "distillation_grade": profile.get("distillation_grade"),
        "sources": len(sources),
        "sources_by_class": source_classes,
        "inspected_sources_by_class": inspected,
        "claim_bearing_sources_by_class": claim_bearing,
        "episodes": len(episodes),
        "heuristics": len(heuristics),
        "validated_heuristics": sum(h.get("status") == "validated" for h in heuristics),
        "routing": routes,
        "lens_families": families
    }


def stats(root: Path = ROOT, scholar: str | None = None) -> dict:
    if scholar:
        return scholar_stats(scholar, root)
    items = [scholar_stats(slug, root) for slug in discover_scholar_slugs(root)]
    return {
        "scholars": len(items),
        "scholar_slugs": [x["scholar"] for x in items],
        "sources": sum(x["sources"] for x in items),
        "episodes": sum(x["episodes"] for x in items),
        "heuristics": sum(x["heuristics"] for x in items)
    }
