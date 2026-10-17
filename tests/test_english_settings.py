"""English football settings are opt-in and survive legacy upgrades."""
import unittest
from copy import deepcopy

from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings


class EnglishSettingsTests(unittest.TestCase):
    def test_disabled_by_default(self):
        settings = validate_settings(deepcopy(DEFAULT_SETTINGS))
        self.assertFalse(settings["sports"]["english"]["enabled"])

    def test_legacy_settings_gain_english_defaults(self):
        settings = deepcopy(DEFAULT_SETTINGS)
        settings["sports"].pop("english")
        settings.pop("english")
        result = validate_settings(settings)
        self.assertIn("english", result["sports"])
        self.assertIn("english", result)

    def test_valid_english_favorites_and_divisions(self):
        settings = deepcopy(DEFAULT_SETTINGS)
        settings["english"]["favorite_teams"] = ["espn:381"]
        settings["english"]["enabled_leagues"] = ["EPL", "CHAMPIONSHIP"]
        self.assertEqual(validate_settings(settings)["english"]["favorite_teams"], ["espn:381"])

    def test_rejects_unknown_division(self):
        settings = deepcopy(DEFAULT_SETTINGS)
        settings["english"]["enabled_leagues"] = ["FA_CUP"]
        with self.assertRaises(ValueError):
            validate_settings(settings)

    def test_rejects_abbreviation_as_persistent_favorite(self):
        settings = deepcopy(DEFAULT_SETTINGS)
        settings["english"]["favorite_teams"] = ["WRX"]
        with self.assertRaises(ValueError):
            validate_settings(settings)

    def test_rejects_duplicate_divisions(self):
        settings = deepcopy(DEFAULT_SETTINGS)
        settings["english"]["enabled_leagues"] = ["EPL", "EPL"]
        with self.assertRaises(ValueError):
            validate_settings(settings)


if __name__ == "__main__":
    unittest.main()
