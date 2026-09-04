from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_policy(root: Path = ROOT) -> dict:
    candidates = [root / "config" / "policy.json", ROOT / "config" / "policy.json"]
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError("config/policy.json not found")


def lens_family_for(heuristic: dict, policy: dict) -> str:
    family = heuristic.get("lens_family") or policy.get("default_lens_family", "scientific_judgment")
    if family in policy.get("lens_families", {}):
        return family
    return policy.get("default_lens_family", "scientific_judgment")


def episode_type_allowed_for_lens(episode_type: str, lens_family: str, policy: dict) -> bool:
    allowed = policy.get("lens_families", {}).get(lens_family, {}).get("episode_types", [])
    return episode_type in allowed


def derive_routing(heuristic: dict, episodes: dict[str, dict] | None = None, policy: dict | None = None) -> dict:
    policy = policy or load_policy()
    family = lens_family_for(heuristic, policy)
    if heuristic.get("status") == "rejected":
        return {
            "lens_eligibility": "excluded",
            "destination": "excluded",
            "lens_family": family,
            "reason": "heuristic status is rejected"
        }

    spec = heuristic.get("specificity") or {}
    spec_status = spec.get("status", "not_tested")
    generic = spec.get("generic_baseline_overlap", "unknown")
    scholar = spec.get("scholar_specificity", "unknown")
    contamination = spec.get("framework_contamination", "unknown")

    if spec_status == "pass" and scholar == "high" and generic != "high" and contamination != "high":
        eligibility = "active_lens"
        reason = "specificity gate passed"
    elif spec_status == "reject" or generic == "high" or scholar == "low" or contamination == "high":
        eligibility = "generic_absorbed"
        reason = "low scholar specificity or high generic/framework overlap"
    else:
        eligibility = "experimental_lens"
        reason = "specificity not strong enough for active scholar lens"

    if episodes and eligibility == "active_lens":
        refs = heuristic.get("supporting_episodes", []) + heuristic.get("counter_episodes", [])
        incompatible = [
            ref for ref in refs
            if ref in episodes
            and not episode_type_allowed_for_lens(
                episodes[ref].get("episode_type", "legacy_unspecified"), family, policy
            )
        ]
        if incompatible:
            eligibility = "experimental_lens"
            reason = "episode-type mismatch for lens family: " + ", ".join(incompatible)

    # v0.6: a strong scholar lens cannot be created by merely combining individually true
    # components. The corpus must show that the combined decision structure itself occurred.
    if eligibility == "active_lens":
        audit = heuristic.get("composition_audit")
        if not audit:
            eligibility = policy.get("composite_heuristic", {}).get("missing_audit_action", "experimental_lens")
            reason = "composition audit missing; combined heuristic ownership is unverified"
        elif audit.get("fabrication_risk") == "high" or not audit.get("combined_operation_evidence"):
            eligibility = policy.get("composite_heuristic", {}).get("high_risk_action", "experimental_lens")
            reason = "composite heuristic fabrication risk: combined operation not demonstrated"

    destination = policy.get("routing", {}).get(eligibility, {}).get("destination", eligibility)
    return {
        "lens_eligibility": eligibility,
        "destination": destination,
        "lens_family": family,
        "reason": reason
    }
