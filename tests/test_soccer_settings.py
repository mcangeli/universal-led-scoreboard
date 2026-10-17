import copy
import unittest

from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings


class SoccerSettingsTests(unittest.TestCase):
    def settings(self):
        return copy.deepcopy(DEFAULT_SETTINGS)

    def test_mls_and_nwsl_disabled_by_default(self):
        settings = validate_settings(self.settings())
        self.assertFalse(settings["sports"]["mls"]["enabled"])
        self.assertFalse(settings["sports"]["nwsl"]["enabled"])

    def test_mls_can_be_enabled_and_selected(self):
        settings = self.settings()
        settings["sports"]["mls"]["enabled"] = True
        settings["active_sport"] = "mls"
        self.assertEqual(validate_settings(settings)["active_sport"], "mls")

    def test_nwsl_can_be_enabled_and_selected(self):
        settings = self.settings()
        settings["sports"]["nwsl"]["enabled"] = True
        settings["active_sport"] = "nwsl"
        self.assertEqual(validate_settings(settings)["active_sport"], "nwsl")

    def test_old_settings_migrate_missing_soccer_sections(self):
        settings = self.settings()
        settings.pop("mls")
        settings.pop("nwsl")
        settings["sports"].pop("nwsl")
        settings["sports"].pop("mls")
        result = validate_settings(settings)
        self.assertIn("mls", result)
        self.assertIn("nwsl", result["sports"])

    def test_provider_selection_persists(self):
        settings = self.settings()
        settings["mls"]["provider"] = "espn_only"
        settings["nwsl"]["provider"] = "league_only"
        result = validate_settings(settings)
        self.assertEqual(result["mls"]["provider"], "espn_only")
        self.assertEqual(result["nwsl"]["provider"], "league_only")

    def test_invalid_provider_rejected(self):
        settings = self.settings()
        settings["mls"]["provider"] = "magic"
        with self.assertRaises(ValueError):
            validate_settings(settings)

    def test_favorites_can_be_saved(self):
        settings = self.settings()
        settings["mls"]["favorite_teams"] = ["ATL", "LAFC"]
        self.assertEqual(validate_settings(settings)["mls"]["favorite_teams"], ["ATL", "LAFC"])

    def test_disabled_sport_cannot_be_selected(self):
        settings = self.settings()
        settings["active_sport"] = "mls"
        with self.assertRaises(ValueError):
            validate_settings(settings)


if __name__ == "__main__":
    unittest.main()
