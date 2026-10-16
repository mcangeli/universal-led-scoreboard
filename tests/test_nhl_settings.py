import copy
import unittest
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings


class NHLSettingsTests(unittest.TestCase):
    def test_default_remains_mlb(self):
        result = validate_settings(copy.deepcopy(DEFAULT_SETTINGS))
        self.assertEqual(result["active_sport"], "mlb")

    def test_enable_and_select_nhl(self):
        value = copy.deepcopy(DEFAULT_SETTINGS)
        value["sports"]["nhl"]["enabled"] = True
        value["active_sport"] = "nhl"
        value["nhl"]["favorite_teams"] = ["BOS", "NYR"]
        self.assertEqual(validate_settings(value)["active_sport"], "nhl")

    def test_disabled_nhl_cannot_be_active(self):
        value = copy.deepcopy(DEFAULT_SETTINGS)
        value["active_sport"] = "nhl"
        with self.assertRaises(ValueError):
            validate_settings(value)

    def test_bad_nhl_preferences(self):
        for key, invalid in (("favorite_teams", ["BAD TEAM"]),
                             ("mode", "broken"), ("refresh_seconds", 0),
                             ("rotation_seconds", 0)):
            with self.subTest(key=key):
                value = copy.deepcopy(DEFAULT_SETTINGS)
                value["nhl"][key] = invalid
                with self.assertRaises(ValueError):
                    validate_settings(value)

    def test_legacy_settings_gain_nhl_defaults(self):
        value = copy.deepcopy(DEFAULT_SETTINGS)
        del value["nhl"]
        self.assertEqual(validate_settings(value)["nhl"], DEFAULT_SETTINGS["nhl"])


if __name__ == "__main__":
    unittest.main()
