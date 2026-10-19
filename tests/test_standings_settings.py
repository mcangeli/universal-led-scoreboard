"""Standings preferences remain safe for existing installations."""
import copy
import unittest

from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings


class StandingsSettingsTests(unittest.TestCase):
    def test_default_is_opt_in(self):
        self.assertFalse(validate_settings(copy.deepcopy(DEFAULT_SETTINGS))["standings"]["enabled"])

    def test_legacy_settings_without_standings_are_accepted(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings.pop("standings")
        self.assertEqual(validate_settings(settings)["standings"],
                         {"enabled": False, "page_seconds": 12, "refresh_seconds": 900})

    def test_valid_custom_preferences(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings["standings"] = {"enabled": True, "page_seconds": 8, "refresh_seconds": 600}
        self.assertEqual(validate_settings(settings)["standings"]["page_seconds"], 8)

    def test_invalid_enabled_type_rejected(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings["standings"]["enabled"] = "yes"
        with self.assertRaises(ValueError):
            validate_settings(settings)

    def test_invalid_intervals_rejected(self):
        for field, value in (("page_seconds", 0), ("refresh_seconds", 10),
                             ("page_seconds", True), ("refresh_seconds", 90000)):
            with self.subTest(field=field, value=value):
                settings = copy.deepcopy(DEFAULT_SETTINGS)
                settings["standings"][field] = value
                with self.assertRaises(ValueError):
                    validate_settings(settings)


if __name__ == "__main__":
    unittest.main()
