"""Regression tests for installing bundled Hermes skills."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"


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

    def test_replaces_file_occupying_skill_slot(self) -> None:
        """A regular file at the destination path must be removed cleanly."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package_dir = root / "package"
            source_skill = package_dir / "skills" / "my-skill"
            source_skill.mkdir(parents=True)
            (source_skill / "SKILL.md").write_text("skill content\n", encoding="utf-8")

            hermes_dir = root / "hermes"
            skills_root = hermes_dir / "skills"
            skills_root.mkdir(parents=True)
            # Occupy the slot with a regular file, not a directory.
            (skills_root / "my-skill").write_text("I am a file, not a dir\n", encoding="utf-8")

            with mock.patch.object(installer, "PACKAGE_DIR", package_dir):
                installed = installer.install_bundled_skills(hermes_dir)

            self.assertEqual(installed, ["my-skill"])
            self.assertTrue((skills_root / "my-skill" / "SKILL.md").is_file())

    def test_replaces_symlink_occupying_skill_slot(self) -> None:
        """A symlink at the destination path must be unlinked cleanly."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package_dir = root / "package"
            source_skill = package_dir / "skills" / "my-skill"
            source_skill.mkdir(parents=True)
            (source_skill / "SKILL.md").write_text("skill content\n", encoding="utf-8")

            hermes_dir = root / "hermes"
            skills_root = hermes_dir / "skills"
            skills_root.mkdir(parents=True)
            link_target = root / "elsewhere"
            link_target.mkdir()
            try:
                (skills_root / "my-skill").symlink_to(link_target)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks not supported on this platform")

            with mock.patch.object(installer, "PACKAGE_DIR", package_dir):
                installed = installer.install_bundled_skills(hermes_dir)

            self.assertEqual(installed, ["my-skill"])
            self.assertTrue((skills_root / "my-skill" / "SKILL.md").is_file())

    def test_real_package_bundle_contains_expected_skills(self) -> None:
        """The packaged skills directory must contain exactly 16 valid skill folders."""
        if not SKILLS_DIR.is_dir():
            self.skipTest("skills/ directory not found next to install.py")
        bundled = [
            d for d in SKILLS_DIR.iterdir()
            if d.is_dir() and (d / "SKILL.md").is_file()
        ]
        names = sorted(d.name for d in bundled)
        self.assertEqual(len(bundled), 16, f"Expected 16 skill folders, found: {names}")
        for d in bundled:
            text = (d / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), f"{d.name}/SKILL.md missing YAML frontmatter")

    def test_pipeline_design_frontmatter_name_is_pipeline_design(self) -> None:
        """pipeline-design/SKILL.md must declare name: pipeline-design, not solution-design."""
        skill_file = SKILLS_DIR / "pipeline-design" / "SKILL.md"
        if not skill_file.is_file():
            self.skipTest("pipeline-design/SKILL.md not found")
        import re
        content = skill_file.read_text(encoding="utf-8")
        match = re.search(r"^name:\s*(\S+)", content, re.MULTILINE)
        self.assertIsNotNone(match, "No 'name:' field found in pipeline-design/SKILL.md frontmatter")
        self.assertEqual(match.group(1), "pipeline-design")


if __name__ == "__main__":
    unittest.main()
