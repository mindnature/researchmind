from __future__ import annotations

from pathlib import Path

from .core import ROOT, load_json, scholar_dir
from .policy import load_policy


def _bounded_score(value) -> float:
    score = float(value)
    if score < 0 or score > 100:
        raise ValueError("fit scores must be between 0 and 100")
    return score


def evaluate_task_fit(assessment: dict, policy: dict | None = None, root: Path = ROOT) -> dict:
    """Evaluate whether a scholar-specific lens should be activated for one concrete task.

    The Agent supplies evidence-backed component scores. The CLI/runtime only applies the
    machine policy and does not invent the fit assessment.
    """
    policy = policy or load_policy(root)
    cfg = policy["scholar_task_fit"]
    dims = ["domain_fit", "decision_structure_fit", "evidence_fit", "added_value_fit"]
    scores = {name: _bounded_score(assessment.get(name, 0)) for name in dims}
    weights = cfg["weights"]
    overall = round(sum(scores[name] * float(weights[name]) for name in dims), 1)

    active_threshold = float(cfg["thresholds"]["active"])
    experimental_threshold = float(cfg["thresholds"]["experimental"])
    if overall >= active_threshold:
        level = "active"
    elif overall >= experimental_threshold:
        level = "experimental"
    else:
        level = "abstain"

    cross = cfg.get("cross_domain_rule", {})
    if (
        scores["domain_fit"] < float(cross.get("domain_fit_below", -1))
        and scores["decision_structure_fit"] < float(cross.get("unless_decision_structure_fit_at_least", 101))
        and level == "active"
    ):
        level = cross.get("maximum_activation", "experimental")

    return {
        "scholar": assessment.get("scholar"),
        "task": assessment.get("task"),
        "target_domain": assessment.get("target_domain"),
        "scores": scores,
        "overall_fit": overall,
        "activation_level": level,
        "activation_policy": cfg["activation"][level],
        "rationale": assessment.get("rationale", ""),
        "evidence_refs": assessment.get("evidence_refs", []),
    }


def transfer_action(confidence: str, policy: dict | None = None, root: Path = ROOT) -> str:
    policy = policy or load_policy(root)
    try:
        return policy["transfer_policy"][confidence]
    except KeyError as exc:
        raise ValueError(f"invalid transfer confidence: {confidence}") from exc


def composition_audit_result(heuristic: dict, policy: dict | None = None, root: Path = ROOT) -> dict:
    """Detect the most common composite-heuristic fabrication failure mode."""
    policy = policy or load_policy(root)
    audit = heuristic.get("composition_audit")
    if not audit:
        return {
            "status": "missing",
            "risk": "unknown",
            "action": policy["composite_heuristic"]["missing_audit_action"],
            "reason": "no composition audit; combined framework ownership is unverified",
        }

    risk = audit.get("fabrication_risk", "unknown")
    combined = bool(audit.get("combined_operation_evidence"))
    if risk == "high" or not combined:
        return {
            "status": "fail",
            "risk": risk,
            "action": policy["composite_heuristic"]["high_risk_action"],
            "reason": "components may be individually sourced but the combined heuristic is not demonstrated",
        }
    return {
        "status": "pass",
        "risk": risk,
        "action": "keep_current_routing",
        "reason": "combined operation has explicit corpus evidence",
    }


def build_lens_provenance_packet(slug: str, heuristic_id: str, root: Path = ROOT) -> dict:
    base = scholar_dir(root, slug)
    heuristics = [load_json(p) for p in sorted((base / "heuristics").glob("*.json"))]
    heuristic = next((h for h in heuristics if h.get("heuristic_id") == heuristic_id), None)
    if heuristic is None:
        raise FileNotFoundError(f"heuristic not found: {slug}/{heuristic_id}")

    episodes = {
        ep["episode_id"]: ep
        for ep in [load_json(p) for p in sorted((base / "episodes").glob("*.json"))]
    }
    sources = {s["source_id"]: s for s in load_json(base / "source_registry.json")}
    support_ids = set(heuristic.get("supporting_episodes", []))
    counter_ids = set(heuristic.get("counter_episodes", []))
    episode_ids = list(support_ids) + [eid for eid in counter_ids if eid not in support_ids]

    episode_packets = []
    source_packets = {}
    for eid in episode_ids:
        ep = episodes.get(eid)
        if not ep:
            continue
        role = "support" if eid in support_ids else "counter"
        episode_packets.append({
            "episode_id": eid,
            "role": role,
            "title": ep.get("title"),
            "episode_type": ep.get("episode_type"),
            "decision_action": ep.get("decision_action"),
            "evidence_strength": ep.get("evidence_strength"),
            "source_refs": ep.get("source_refs", []),
        })
        for sid in ep.get("source_refs", []):
            src = sources.get(sid)
            if src:
                source_packets[sid] = {
                    "source_id": sid,
                    "title": src.get("title"),
                    "source_class": src.get("source_class"),
                    "inspection_status": src.get("inspection_status"),
                    "stable_locator": src.get("stable_locator") or src.get("url"),
                }

    return {
        "scholar": slug,
        "heuristic_id": heuristic_id,
        "rule": heuristic.get("rule"),
        "lens_family": heuristic.get("lens_family"),
        "scholar_added_delta": (heuristic.get("specificity") or {}).get("scholar_added_delta", ""),
        "supporting_and_counter_episodes": episode_packets,
        "source_locators": list(source_packets.values()),
        "composition_audit": heuristic.get("composition_audit"),
    }


def validate_active_lens_provenance(packet: dict, policy: dict | None = None, root: Path = ROOT) -> list[str]:
    policy = policy or load_policy(root)
    cfg = policy["active_lens_provenance"]
    errors: list[str] = []
    episodes = packet.get("supporting_and_counter_episodes", [])
    supporting_count = sum(1 for ep in episodes if ep.get("role") == "support")
    if supporting_count < int(cfg["minimum_supporting_episodes"]):
        errors.append("insufficient supporting Episode count for strong scholar lens")
    sources = packet.get("source_locators", [])
    if cfg.get("require_source_locators") and not any(s.get("stable_locator") for s in sources):
        errors.append("active lens has no stable source locator")
    if cfg.get("require_inspected_source") and not any(
        s.get("inspection_status") == "inspected" and s.get("stable_locator") for s in sources
    ):
        errors.append("active lens has no inspected source with stable locator")
    if cfg.get("require_scholar_added_delta") and not packet.get("scholar_added_delta"):
        errors.append("active lens has no scholar-added delta")
    if cfg.get("require_composition_audit") and not packet.get("composition_audit"):
        errors.append("active lens has no composition audit")
    return errors


def swap_scholar_summary(results: list[dict]) -> dict:
    """Summarize same-task outputs across Generic ResearchMind and multiple Scholar Advisors."""
    if not results:
        return {"results": [], "warning": "no results"}
    active_counts = [int(r.get("active_lens_count", 0)) for r in results]
    added = [str(r.get("scholar_added_delta", "")).strip() for r in results if r.get("scholar") != "generic"]
    suspicious_uniformity = len(set(active_counts)) == 1 and active_counts[0] > 0
    duplicate_delta = len(added) > 1 and len(set(added)) == 1
    return {
        "results": results,
        "suspicious_uniformity": suspicious_uniformity,
        "duplicate_scholar_added_delta": duplicate_delta,
        "interpretation": (
            "possible forced-lens activation: multiple scholars contribute the same lens density or delta"
            if suspicious_uniformity or duplicate_delta
            else "no obvious uniformity signal"
        ),
    }
