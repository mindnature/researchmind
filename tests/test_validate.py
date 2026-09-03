import importlib.util
from pathlib import Path
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

    def test_mvp_has_contrastive_pair(self):
        h = mod.load_json(ROOT / "data/pauling/heuristics/LP-H01-HARD-CONSTRAINT-FIRST.json")
        self.assertTrue(h["supporting_episodes"])
        self.assertTrue(h["counter_episodes"])

    def test_no_heuristic_claimed_validated_yet(self):
        s = mod.stats(ROOT)
        self.assertEqual(s["validated_heuristics"], 0)


if __name__ == "__main__":
    unittest.main()
