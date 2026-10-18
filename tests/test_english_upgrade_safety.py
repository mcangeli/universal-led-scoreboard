"""v0.6.0 upgrade safety: legacy v0.5 settings must remain usable."""
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from universal_led.sport_settings import DEFAULT_SETTINGS, load_settings, save_settings


class EnglishUpgradeSafetyTests(unittest.TestCase):
    def legacy(self):
        value = deepcopy(DEFAULT_SETTINGS)
        value["sports"].pop("english")
        value.pop("english")
        value["sports"]["mls"]["enabled"] = True
        value["sports"]["nwsl"]["enabled"] = True
        value["sports"]["mls"]["news_enabled"] = True
        value["mls"]["favorite_teams"] = ["ATL"]
        value["nwsl"]["favorite_teams"] = ["GFC"]
        value["news"]["headline_seconds"] = 15
        return value

    def test_load_legacy_settings_adds_disabled_english(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root, "settings.json").write_text(json.dumps(self.legacy()), encoding="utf-8")
            upgraded = load_settings(root)
            self.assertFalse(upgraded["sports"]["english"]["enabled"])
            self.assertFalse(upgraded["sports"]["english"]["news_enabled"])
            self.assertEqual(upgraded["english"]["favorite_teams"], [])
            self.assertEqual(upgraded["mls"]["favorite_teams"], ["ATL"])
            self.assertEqual(upgraded["nwsl"]["favorite_teams"], ["GFC"])
            self.assertTrue(upgraded["sports"]["mls"]["enabled"])
            self.assertTrue(upgraded["sports"]["nwsl"]["enabled"])
            self.assertEqual(upgraded["news"]["headline_seconds"], 15)

    def test_load_does_not_rewrite_existing_settings(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root, "settings.json")
            original = json.dumps(self.legacy(), indent=2)
            path.write_text(original, encoding="utf-8")
            load_settings(root)
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_save_and_reload_preserves_existing_sports(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root, "settings.json")
            path.write_text(json.dumps(self.legacy()), encoding="utf-8")
            updated = load_settings(root)
            updated["sports"]["english"]["enabled"] = True
            updated["english"]["favorite_teams"] = ["espn:381"]
            updated["english"]["enabled_leagues"] = ["EPL"]
            save_settings(root, updated)
            reloaded = load_settings(root)
            self.assertTrue(reloaded["sports"]["english"]["enabled"])
            self.assertEqual(reloaded["english"]["favorite_teams"], ["espn:381"])
            self.assertEqual(reloaded["mls"]["favorite_teams"], ["ATL"])
            self.assertEqual(reloaded["nwsl"]["favorite_teams"], ["GFC"])
            self.assertEqual(reloaded["news"]["headline_seconds"], 15)


if __name__ == "__main__":
    unittest.main()
