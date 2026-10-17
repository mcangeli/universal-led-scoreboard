"""Sport extensibility contract.

Keep sport registration and dashboard structure synchronized without freezing
constructor formatting or the number/order of supported sports.
"""
import unittest
from html.parser import HTMLParser

from universal_led.configurator import HTML
from universal_led.sport_settings import SPORTS, DEFAULT_SETTINGS, validate_settings
from universal_led.multisport_runtime import MultiSportRenderer


# Legacy EFL is reserved for a future integration and intentionally has no UI.
UI_SPORTS = set(SPORTS) - {"efl"}


class SportMarkup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.panels = []
        self.picker = []
        self.states = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div" and "sport-config-panel" in attrs.get("class", "").split():
            self.panels.append(attrs.get("data-sport-panel"))
        if tag == "option" and attrs.get("value") in UI_SPORTS:
            self.picker.append(attrs["value"])
        if tag == "span" and attrs.get("id", "").startswith("sport-state-"):
            self.states.append(attrs["id"].removeprefix("sport-state-"))


class SportExtensibilityTests(unittest.TestCase):
    def test_every_configurable_sport_has_one_panel_and_overview_card(self):
        parser = SportMarkup()
        parser.feed(HTML)
        self.assertEqual(set(parser.panels), UI_SPORTS)
        self.assertEqual(len(parser.panels), len(UI_SPORTS))
        self.assertEqual(set(parser.states), UI_SPORTS)
        self.assertEqual(len(parser.states), len(UI_SPORTS))

    def test_new_sports_start_disabled_and_existing_defaults_survive(self):
        settings = validate_settings(DEFAULT_SETTINGS)
        self.assertEqual(set(settings["sports"]), set(SPORTS))
        self.assertEqual(settings["active_sport"], "mlb")
        self.assertTrue(settings["sports"]["mlb"]["enabled"])
        self.assertFalse(settings["sports"]["english"]["enabled"])

    def test_english_renderer_is_registered_via_public_constructor(self):
        class Fake:
            def frame(self):
                return "frame"
            def game(self):
                return None
            def has_games(self):
                return True
            def has_live_games(self):
                return False
        english = Fake()
        board = MultiSportRenderer(Fake(), Fake(), english_renderer=english)
        self.assertIs(board._renderer("english"), english)
        board.configure_rotation(["english"], preferred="english")
        self.assertEqual(board.frame(), "frame")


if __name__ == "__main__":
    unittest.main()
