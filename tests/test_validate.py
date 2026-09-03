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
    def test_repository_validates(self):
        self.assertEqual(mod.validate(ROOT), [])
        self.assertEqual(mod.validate(ROOT, epistemic=True), [])

    def test_pauling_has_contrastive_pair(self):
        h = mod.load_json(ROOT / "data/pauling/heuristics/LP-H01-HARD-CONSTRAINT-FIRST.json")
        self.assertTrue(h["supporting_episodes"])
        self.assertTrue(h["counter_episodes"])

    def test_universal_scaffold_from_name_has_grade_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = mod.init_scholar("Geoffrey Hinton", depth="standard", root=root)
            self.assertEqual(base.name, "geoffrey-hinton")
            profile = mod.load_json(base / "scholar_profile.json")
            self.assertEqual(profile["distillation_grade"], "unknown")
            self.assertIn("evidence_profile", profile)
            self.assertEqual(mod.validate_scholar("geoffrey-hinton", root), [])

    def test_non_ascii_name_gets_stable_slug(self):
        a = mod.slugify("屠呦呦")
        b = mod.slugify("屠呦呦")
        self.assertEqual(a, b)
        self.assertRegex(a, r"^[a-z0-9][a-z0-9-]*$")

    def test_validated_heuristic_requires_specificity_pass(self):
        h = {
            "heuristic_id": "H1",
            "name": "x",
            "status": "validated",
            "decision_structure": "x",
            "rule": "x",
            "supporting_episodes": ["E1"],
            "counter_episodes": ["E2"],
            "boundary_conditions": ["x"],
            "failure_signals": ["x"]
        }
        errors = []
        mod.validate_specificity("H1", h, errors, "test")
        self.assertTrue(any("specificity gate" in e for e in errors))

    def test_specificity_pass_rejects_high_generic_overlap(self):
        h = {
            "heuristic_id": "H1",
            "status": "provisional",
            "specificity": {
                "status": "pass",
                "generic_baseline_overlap": "high",
                "scholar_specificity": "high",
                "framework_contamination": "low",
                "scholar_added_delta": "distinct operation",
                "specificity_evidence": ["E1", "E2"]
            }
        }
        errors = []
        mod.validate_specificity("H1", h, errors, "test")
        self.assertTrue(any("generic baseline overlap" in e for e in errors))

    def test_transactional_stage_and_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job_id, staged = mod.stage_scholar("Geoffrey Hinton", job_id="job-test", root=root)
            self.assertEqual(job_id, "job-test")
            self.assertTrue(staged.exists())
            dest = mod.commit_staged(job_id, "geoffrey-hinton", root=root)
            self.assertTrue(dest.exists())
            checkpoint = json.loads((root / ".researchmind/staging/job-test/checkpoint.json").read_text(encoding="utf-8"))
            self.assertEqual(checkpoint["phase"], "committed")

    def test_pauling_builds_three_layer_advisor(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "pauling-advisor"
            result = mod.build_skill("pauling", ROOT, out)
            self.assertEqual(result, out)
            skill = (out / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("DOMAIN_BASELINE", skill)
            self.assertIn("SCHOLAR_LENS", skill)
            self.assertIn("TRANSFER_INFERENCE", skill)
            self.assertTrue((out / "episodes").is_dir())
            self.assertTrue((out / "heuristics").is_dir())


if __name__ == "__main__":
    unittest.main()
