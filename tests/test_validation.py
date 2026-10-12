"""Mutate disposable copies to verify the validator catches real failures."""

from pathlib import Path
import importlib.util
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "scripts/validate_repository.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RepositoryValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        shutil.copytree(ROOT, self.root, symlinks=True, ignore=shutil.ignore_patterns(".git", "__pycache__"))

    def append(self, name, text):
        with (self.root / name).open("a", encoding="utf-8") as output:
            output.write(text)

    def rejects(self, message):
        self.assertTrue(any(message in error for error in MODULE.validate(self.root)), message)

    def test_current_repository_passes(self):
        self.assertEqual(MODULE.validate(self.root), [])

    def test_missing_skill_reference_is_rejected(self):
        (self.root / "references/training.md").unlink()
        self.rejects("Missing file: references/training.md")

    def test_broken_documentation_link_is_rejected(self):
        self.append("README.md", "\n[missing](docs/absent.md)\n")
        self.rejects("Broken local link")

    def test_undefined_citation_is_rejected(self):
        self.append("references/training.md", "\n[T99]\n")
        self.rejects("Undefined evidence ID")

    def test_duplicate_evidence_id_is_rejected(self):
        self.append("references/evidence.md", "\n**T01｜duplicate**\n")
        self.rejects("Duplicate evidence ID")

    def test_default_prompt_must_invoke_correct_skill(self):
        path = self.root / "agents/openai.yaml"
        path.write_text(path.read_text(encoding="utf-8").replace("$evidence-based-cycling-coach", "$other-skill"), encoding="utf-8")
        self.rejects("Invalid UI metadata")

    def test_independent_rules_copy_is_rejected(self):
        path = self.root / "AGENTS.md"
        path.unlink()
        path.write_text("Independent rules", encoding="utf-8")
        self.rejects("AGENTS.md must be a relative symlink")

    def test_absolute_user_path_is_rejected(self):
        self.append("README.md", "\n/home/example/private-project\n")
        self.rejects("Local path or credential")

    def test_ci_write_permissions_are_rejected(self):
        path = self.root / ".github/workflows/validate.yml"
        path.write_text(path.read_text(encoding="utf-8").replace("contents: read", "contents: write"), encoding="utf-8")
        self.rejects("Invalid CI configuration")


if __name__ == "__main__":
    unittest.main()
