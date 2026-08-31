"""Regression tests for installing bundled Hermes skills."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_installer():
    spec = importlib.util.spec_from_file_location(
        "for_hermes_bundled_skills_installer", ROOT / "install.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load_installer()


class BundledSkillsInstallTests(unittest.TestCase):
    def test_installs_bundle_updates_matching_skill_and_preserves_user_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package_dir = root / "package"
            source_skill = package_dir / "skills" / "architecture-patterns"
            source_skill.mkdir(parents=True)
            (source_skill / "SKILL.md").write_text("new bundled skill\n", encoding="utf-8")
            (source_skill / "references").mkdir()
            (source_skill / "references" / "guide.md").write_text("reference\n", encoding="utf-8")

            hermes_dir = root / "hermes"
            prior_bundle = hermes_dir / "skills" / "architecture-patterns"
            prior_bundle.mkdir(parents=True)
            (prior_bundle / "obsolete.md").write_text("obsolete\n", encoding="utf-8")
            user_skill = hermes_dir / "skills" / "my-private-skill"
            user_skill.mkdir(parents=True)
            (user_skill / "SKILL.md").write_text("preserve me\n", encoding="utf-8")

            with mock.patch.object(installer, "PACKAGE_DIR", package_dir):
                installed = installer.install_bundled_skills(hermes_dir)

            self.assertEqual(installed, ["architecture-patterns"])
            self.assertEqual(
                (hermes_dir / "skills" / "architecture-patterns" / "SKILL.md").read_text(encoding="utf-8"),
                "new bundled skill\n",
            )
            self.assertTrue(
                (hermes_dir / "skills" / "architecture-patterns" / "references" / "guide.md").is_file()
            )
            self.assertFalse((hermes_dir / "skills" / "architecture-patterns" / "obsolete.md").exists())
            self.assertEqual((user_skill / "SKILL.md").read_text(encoding="utf-8"), "preserve me\n")


if __name__ == "__main__":
    unittest.main()
