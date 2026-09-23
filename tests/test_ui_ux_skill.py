"""Contract and installer guards for the generic Hermes UI/UX skill."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "ui-ux" / "SKILL.md"
CONTRACT = ROOT / "skills" / "ui-ux" / "references" / "decision-contract.json"
CHECKLIST = ROOT / "skills" / "ui-ux" / "references" / "review-checklist.md"


def load_installer_module():
    spec = importlib.util.spec_from_file_location("for_hermes_installer", ROOT / "install.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load_installer_module()


class UiUxSkillTests(unittest.TestCase):
    def test_skill_layout_and_frontmatter(self) -> None:
        self.assertTrue(SKILL.is_file())
        self.assertTrue(CONTRACT.is_file())
        self.assertTrue(CHECKLIST.is_file())
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("name: ui-ux", text)
        self.assertIn('skill_view("ui-ux", "references/decision-contract.json")', text)

    def test_decision_contract_has_closed_action_grammar(self) -> None:
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], 1)
        prefixes = set(data["actionPrefixes"])
        self.assertEqual(prefixes, {"constraint", "pattern", "mode", "review"})
        self.assertIn("must-have", data["rules"])

        for condition, rule in data["rules"].items():
            self.assertTrue(rule["signals"], condition)
            self.assertTrue(rule["actions"], condition)
            for action in rule["actions"]:
                prefix, sep, value = action.partition(":")
                self.assertEqual(sep, ":", action)
                self.assertIn(prefix, prefixes, action)
                self.assertTrue(value.strip(), action)
                lowered = action.lower()
                for forbidden in ("http://", "https://", "javascript:", "<script", " exec", " eval"):
                    self.assertNotIn(forbidden, lowered, action)

    def test_contract_is_not_a_second_design_token_source(self) -> None:
        raw = CONTRACT.read_text(encoding="utf-8").lower()
        self.assertNotIn("fontfamily", raw)
        self.assertNotRegex(raw, r"#[0-9a-f]{3,8}\b")
        self.assertNotRegex(raw, r"\b(?:rgb|oklch)\s*\(")

    def test_installer_copies_ui_ux_skill_to_hermes_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hermes_home = Path(tmp) / ".hermes"
            destination = installer.install_ui_ux_skill(hermes_home)

            self.assertEqual(destination, hermes_home / "skills" / "ui-ux")
            self.assertTrue((destination / "SKILL.md").is_file())
            self.assertTrue((destination / "references" / "decision-contract.json").is_file())
            self.assertTrue((destination / "references" / "review-checklist.md").is_file())

            installed_contract = json.loads(
                (destination / "references" / "decision-contract.json").read_text(encoding="utf-8")
            )
            self.assertEqual(installed_contract["version"], 1)


if __name__ == "__main__":
    unittest.main()
