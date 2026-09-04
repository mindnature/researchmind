import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "researchmind.py"
spec = importlib.util.spec_from_file_location("researchmind_cli", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class ResearchMindValidationTest(unittest.TestCase):
    def test_repository_has_no_blocking_errors(self):
        self.assertEqual(mod.validate(ROOT), [])
        self.assertEqual(mod.validate(ROOT, epistemic=True), [])
        self.assertEqual(mod.quality_report(ROOT)["errors"], [])

    def test_policy_is_single_machine_source(self):
        policy = mod.load_policy(ROOT)
        self.assertEqual(policy["version"], "0.6")
        self.assertIn("scholar_task_fit", policy)
        self.assertIn("transfer_policy", policy)
        self.assertIn("scientific_judgment", policy["lens_families"])

    def test_universal_scaffold_from_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = mod.init_scholar("Geoffrey Hinton", depth="standard", root=root)
            self.assertEqual(base.name, "geoffrey-hinton")
            profile = mod.load_json(base / "scholar_profile.json")
            self.assertEqual(profile["distillation_grade"], "unknown")
            self.assertEqual(mod.validate_scholar("geoffrey-hinton", root), [])

    def test_non_ascii_name_gets_stable_slug(self):
        a = mod.slugify("屠呦呦")
        b = mod.slugify("屠呦呦")
        self.assertEqual(a, b)
        self.assertRegex(a, r"^[a-z0-9][a-z0-9-]*$")

    def test_low_specificity_is_soft_routed_not_blocked(self):
        heuristic = {
            "heuristic_id": "H1",
            "name": "Be rigorous",
            "status": "validated",
            "decision_structure": "generic",
            "rule": "Be rigorous about assumptions.",
            "supporting_episodes": [],
            "counter_episodes": [],
            "boundary_conditions": [],
            "failure_signals": [],
            "specificity": {
                "status": "reject",
                "generic_baseline_overlap": "high",
                "scholar_specificity": "low",
                "framework_contamination": "low",
                "scholar_added_delta": "",
                "specificity_evidence": []
            }
        }
        errors = []
        mod.validate_specificity("H1", heuristic, errors, "test")
        self.assertEqual(errors, [])
        route = mod.derive_routing(heuristic, policy=mod.load_policy(ROOT))
        self.assertEqual(route["lens_eligibility"], "generic_absorbed")

    def test_specificity_pass_needs_composition_audit_for_active_lens(self):
        heuristic = {
            "heuristic_id": "H2",
            "name": "Distinct rule",
            "status": "provisional",
            "decision_structure": "distinct",
            "rule": "Do X under Y.",
            "supporting_episodes": [],
            "counter_episodes": [],
            "boundary_conditions": [],
            "failure_signals": [],
            "specificity": {
                "status": "pass",
                "generic_baseline_overlap": "low",
                "scholar_specificity": "high",
                "framework_contamination": "low",
                "scholar_added_delta": "A distinctive operational representation.",
                "specificity_evidence": ["E1", "E2"]
            }
        }
        route = mod.derive_routing(heuristic, policy=mod.load_policy(ROOT))
        self.assertEqual(route["lens_eligibility"], "experimental_lens")
        heuristic["composition_audit"] = {
            "components": ["X", "Y"],
            "combined_operation_evidence": ["E1", "E2"],
            "fabrication_risk": "low"
        }
        route = mod.derive_routing(heuristic, policy=mod.load_policy(ROOT))
        self.assertEqual(route["lens_eligibility"], "active_lens")

    def test_methodological_stance_is_allowed_for_stance_lens(self):
        policy = mod.load_policy(ROOT)
        self.assertTrue(mod.episode_type_allowed_for_lens("methodological_stance", "methodological_stance", policy))
        self.assertTrue(mod.episode_type_allowed_for_lens("paradigm_shift_advocacy", "research_strategy", policy))
        self.assertFalse(mod.episode_type_allowed_for_lens("institution_building", "research_strategy", policy))

    def test_task_fit_can_abstain_even_when_scholar_has_lenses(self):
        assessment = {
            "scholar": "Zheng Bingwen",
            "task": "review a low-altitude logistics project",
            "target_domain": "operations management",
            "domain_fit": 25,
            "decision_structure_fit": 50,
            "evidence_fit": 40,
            "added_value_fit": 35,
            "rationale": "cross-domain analogy only"
        }
        result = mod.evaluate_task_fit(assessment, root=ROOT)
        self.assertEqual(result["activation_level"], "abstain")
        self.assertLess(result["overall_fit"], 50)

    def test_cross_domain_fit_caps_active_to_experimental(self):
        assessment = {
            "scholar": "Scholar X",
            "task": "far-domain task",
            "target_domain": "unrelated",
            "domain_fit": 20,
            "decision_structure_fit": 70,
            "evidence_fit": 100,
            "added_value_fit": 100,
            "rationale": "strong lens but weak domain and structure fit"
        }
        result = mod.evaluate_task_fit(assessment, root=ROOT)
        self.assertEqual(result["activation_level"], "experimental")

    def test_medium_transfer_is_diagnostic_only(self):
        self.assertEqual(mod.transfer_action("high", root=ROOT), "recommendation_allowed")
        self.assertEqual(mod.transfer_action("medium", root=ROOT), "diagnostic_only")
        self.assertEqual(mod.transfer_action("low", root=ROOT), "question_generation_only")
        self.assertEqual(mod.transfer_action("reject", root=ROOT), "abstain")

    def test_composite_heuristic_without_combined_evidence_is_downgraded(self):
        heuristic = {
            "composition_audit": {
                "components": ["participation", "centralization"],
                "combined_operation_evidence": [],
                "fabrication_risk": "high"
            }
        }
        result = mod.composition_audit_result(heuristic, root=ROOT)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["action"], "experimental_lens")

    def test_swap_scholar_flags_uniform_outputs(self):
        results = [
            {"scholar": "generic", "active_lens_count": 2, "scholar_added_delta": ""},
            {"scholar": "A", "active_lens_count": 2, "scholar_added_delta": "same framework"},
            {"scholar": "B", "active_lens_count": 2, "scholar_added_delta": "same framework"}
        ]
        summary = mod.swap_scholar_summary(results)
        self.assertTrue(summary["suspicious_uniformity"])
        self.assertTrue(summary["duplicate_scholar_added_delta"])

    def test_auto_distill_creates_recoverable_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pipeline = mod.auto_distill("Geoffrey Hinton", mode="fast-auto", root=root)
            self.assertTrue(pipeline["agent_required"])
            self.assertEqual(pipeline["depth"], "quick")
            self.assertEqual(pipeline["status"], "awaiting_agent")
            self.assertEqual(pipeline["pipeline_version"], "0.6")
            path = mod.staging_root(root, pipeline["job_id"]) / "pipeline.json"
            self.assertTrue(path.exists())

    def test_transactional_commit_allows_quality_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job_id, staged = mod.stage_scholar("Geoffrey Hinton", job_id="job-test", root=root)
            heuristic = {
                "heuristic_id": "GH-GENERIC",
                "name": "Generic advice",
                "status": "validated",
                "decision_structure": "generic",
                "rule": "Be careful.",
                "supporting_episodes": [],
                "counter_episodes": [],
                "boundary_conditions": [],
                "failure_signals": [],
                "specificity": {
                    "status": "reject",
                    "generic_baseline_overlap": "high",
                    "scholar_specificity": "low",
                    "framework_contamination": "low",
                    "scholar_added_delta": "",
                    "specificity_evidence": []
                }
            }
            mod.write_json(staged / "heuristics" / "GH-GENERIC.json", heuristic)
            dest = mod.commit_staged(job_id, "geoffrey-hinton", root=root)
            self.assertTrue(dest.exists())
            committed = mod.load_json(dest / "heuristics" / "GH-GENERIC.json")
            self.assertEqual(committed["routing"]["lens_eligibility"], "generic_absorbed")
            report = mod.load_json(root / ".researchmind" / "staging" / job_id / "quality_report.json")
            self.assertEqual(report["errors"], [])
            self.assertTrue(report["warnings"])

    def test_pauling_builds_task_fit_aware_three_layer_advisor(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "pauling-advisor"
            result = mod.build_skill("pauling", ROOT, out)
            self.assertEqual(result, out)
            skill = (out / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("Scholar–Task Fit", skill)
            self.assertIn("Forced Lens Activation", skill)
            self.assertIn("Composite Heuristic Fabrication", skill)
            self.assertIn("DOMAIN_BASELINE", skill)
            self.assertIn("SCHOLAR_LENS", skill)
            self.assertIn("TRANSFER_INFERENCE", skill)
            self.assertTrue((out / "build_report.json").exists())


if __name__ == "__main__":
    unittest.main()
