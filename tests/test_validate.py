import importlib.util
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

    def test_pauling_has_contrastive_pair(self):
        h = mod.load_json(ROOT / "data/pauling/heuristics/LP-H01-HARD-CONSTRAINT-FIRST.json")
        self.assertTrue(h["supporting_episodes"])
        self.assertTrue(h["counter_episodes"])

    def test_universal_scaffold_from_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = mod.init_scholar("Geoffrey Hinton", depth="standard", root=root)
            self.assertEqual(base.name, "geoffrey-hinton")
            self.assertTrue((base / "scholar_profile.json").exists())
            self.assertTrue((base / "distillation_manifest.json").exists())
            self.assertTrue((base / "source_registry.json").exists())
            self.assertTrue((base / "episodes").is_dir())
            self.assertTrue((base / "heuristics").is_dir())
            self.assertEqual(mod.validate_scholar("geoffrey-hinton", root), [])

    def test_non_ascii_name_gets_stable_slug(self):
        a = mod.slugify("屠呦呦")
        b = mod.slugify("屠呦呦")
        self.assertEqual(a, b)
        self.assertRegex(a, r"^[a-z0-9][a-z0-9-]*$")

    def test_pauling_builds_portable_advisor(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "pauling-advisor"
            result = mod.build_skill("pauling", ROOT, out)
            self.assertEqual(result, out)
            self.assertTrue((out / "SKILL.md").exists())
            self.assertTrue((out / "scholar_profile.json").exists())
            self.assertTrue((out / "episodes").is_dir())
            self.assertTrue((out / "heuristics").is_dir())


if __name__ == "__main__":
    unittest.main()
