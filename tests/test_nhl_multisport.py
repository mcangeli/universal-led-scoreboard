import unittest
from universal_led.multisport_runtime import MultiSportRenderer


class FakeRenderer:
    def __init__(self, label):
        self.label = label
        self.calls = []

    def frame(self):
        self.calls.append("frame")
        return self.label

    def game(self):
        self.calls.append("game")
        return self.label + "-game"


class MultiSportTests(unittest.TestCase):
    def setUp(self):
        self.mlb = FakeRenderer("MLB")
        self.nhl = FakeRenderer("NHL")
        self.router = MultiSportRenderer(self.mlb, self.nhl)

    def test_default_is_mlb(self):
        self.assertEqual(self.router.active_sport, "mlb")
        self.assertEqual(self.router.frame(), "MLB")

    def test_switch_to_nhl(self):
        self.router.set_active_sport("nhl")
        self.assertEqual(self.router.frame(), "NHL")
        self.assertEqual(self.router.game(), "NHL-game")

    def test_switch_back_to_mlb(self):
        self.router.set_active_sport("nhl")
        self.router.set_active_sport("mlb")
        self.assertEqual(self.router.frame(), "MLB")

    def test_invalid_sport_does_not_change_selection(self):
        with self.assertRaises(ValueError):
            self.router.set_active_sport("nfl")
        self.assertEqual(self.router.active_sport, "mlb")

    def test_no_cross_sport_render(self):
        self.router.set_active_sport("nhl")
        self.router.frame()
        self.assertEqual(self.mlb.calls, [])
        self.assertEqual(self.nhl.calls, ["frame"])


    def test_live_game_in_other_sport_suppresses_news(self):
        from types import SimpleNamespace

        class FakeNews:
            def items(self):
                return [SimpleNamespace(source="Test", text="Headline")]

        self.router.news = FakeNews()
        self.router.settings_getter = lambda: {"news": {
            "rotation_interval": 1, "scroll_chars_per_second": 1}}
        self.router.configure_rotation(("mlb", "nhl"), interval=12)
        self.nhl.game = lambda: SimpleNamespace(status="live")
        self.mlb.game = lambda: SimpleNamespace(status="scheduled")
        self.assertEqual(self.router.frame(), "NHL")

    def test_no_news_does_not_probe_other_sport_game(self):
        class EmptyNews:
            def items(self):
                return []

        self.router.news = EmptyNews()
        self.router.settings_getter = lambda: {"news": {}}
        self.router.set_active_sport("nhl")
        self.assertEqual(self.router.frame(), "NHL")
        self.assertEqual(self.mlb.calls, [])
        self.assertEqual(self.nhl.calls, ["frame"])



    def test_live_sport_preempts_scheduled_sport(self):
        from types import SimpleNamespace
        self.router.configure_rotation(("mlb", "nhl"), interval=12)
        self.mlb.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.game = lambda: SimpleNamespace(status="live")
        self.assertEqual(self.router.frame(), "NHL")

    def test_rotation_recovers_when_live_game_finishes(self):
        from types import SimpleNamespace
        state = {"status": "live"}
        self.router.configure_rotation(("mlb", "nhl"), interval=12)
        self.mlb.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.game = lambda: SimpleNamespace(status=state["status"])
        self.assertEqual(self.router.frame(), "NHL")
        state["status"] = "final"
        self.assertEqual(self.router.frame(), "MLB")

    def test_multiple_live_sports_remain_eligible(self):
        from types import SimpleNamespace
        now = [0]
        self.router.clock = lambda: now[0]
        self.router.configure_rotation(("mlb", "nhl"), interval=12)
        self.mlb.game = lambda: SimpleNamespace(status="live")
        self.nhl.game = lambda: SimpleNamespace(status="live")
        self.assertEqual(self.router.frame(), "MLB")
        now[0] = 12
        self.assertEqual(self.router.frame(), "NHL")



    def test_all_games_live_contract_overrides_selected_scheduled_game(self):
        from types import SimpleNamespace
        self.router.configure_rotation(("mlb", "nhl"), interval=12)
        self.mlb.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.has_live_games = lambda: True
        self.assertEqual(self.router.frame(), "NHL")

    def test_all_games_contract_recovers_after_live_games_end(self):
        from types import SimpleNamespace
        state = {"live": True}
        self.router.configure_rotation(("mlb", "nhl"), interval=12)
        self.mlb.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.has_live_games = lambda: state["live"]
        self.assertEqual(self.router.frame(), "NHL")
        state["live"] = False
        self.assertEqual(self.router.frame(), "MLB")



if __name__ == "__main__":
    unittest.main()
