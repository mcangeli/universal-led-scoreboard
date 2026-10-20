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

    def test_live_other_sport_sets_soccer_interruption_context(self):
        from types import SimpleNamespace
        soccer = FakeRenderer("MLS")
        soccer.external_live_games = False
        soccer.has_games = lambda: True
        soccer.has_live_games = lambda: False
        self.router.mls = soccer
        self.router.configure_rotation(("nhl", "mls"), interval=12, preferred="mls")
        self.nhl.game = lambda: SimpleNamespace(status="live")
        self.assertEqual(self.router.frame(), "NHL")
        self.assertTrue(soccer.external_live_games)

    def test_soccer_interruption_context_clears_after_final(self):
        from types import SimpleNamespace
        state = {"status": "live"}
        soccer = FakeRenderer("MLS")
        soccer.external_live_games = False
        soccer.has_games = lambda: True
        soccer.has_live_games = lambda: False
        self.router.mls = soccer
        self.router.configure_rotation(("nhl", "mls"), interval=12, preferred="mls")
        self.nhl.game = lambda: SimpleNamespace(status=state["status"])
        self.router.frame()
        state["status"] = "final"
        self.router.frame()
        self.assertFalse(soccer.external_live_games)

    def test_bullpen_suppressed_by_live_nhl(self):
        from types import SimpleNamespace

        class Slot:
            def __init__(self):
                self.calls = []

            def frame(self, **kwargs):
                self.calls.append(kwargs)
                return "BULLPEN"

        now = [12]
        self.router.clock = lambda: now[0]
        self.router.configure_rotation(("mlb", "nhl"), interval=12)
        self.mlb.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.game = lambda: SimpleNamespace(status="live")
        slot = Slot()
        self.router.set_bullpen_slots((slot,))
        self.assertEqual(self.router.frame(), "NHL")
        self.assertEqual(slot.calls, [])

    def test_bullpen_shares_idle_slots_and_yields_to_normal_frames(self):
        from types import SimpleNamespace

        class Slot:
            def __init__(self):
                self.calls = []

            def frame(self, **kwargs):
                self.calls.append(kwargs)
                return "BULLPEN"

        now = [0]
        self.router.clock = lambda: now[0]
        self.router.configure_rotation(("mlb", "nhl"), interval=12)
        self.mlb.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.game = lambda: SimpleNamespace(status="final")
        slot = Slot()
        self.router.set_bullpen_slots((slot,))
        self.assertEqual(self.router.frame(), "MLB")
        self.assertEqual(slot.calls, [])
        now[0] = 12
        self.assertEqual(self.router.frame(), "BULLPEN")
        self.assertEqual(len(slot.calls), 1)

    def test_unready_bullpen_falls_back_to_sport_frame(self):
        from types import SimpleNamespace

        class Slot:
            def frame(self, **kwargs):
                return None

        now = [12]
        self.router.clock = lambda: now[0]
        self.router.configure_rotation(("mlb", "nhl"), interval=12)
        self.mlb.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.game = lambda: SimpleNamespace(status="final")
        self.router.set_bullpen_slots((Slot(),))
        # The normal scheduler selects MLB at this slot; plugin fallback
        # must preserve that selection rather than choosing another sport.
        self.assertEqual(self.router.frame(), "MLB")

    def test_bullpen_suppressed_by_live_nba(self):
        from types import SimpleNamespace

        class Slot:
            def __init__(self):
                self.calls = 0

            def frame(self, **kwargs):
                self.calls += 1
                return "BULLPEN"

        now = [12]
        self.router.clock = lambda: now[0]
        nba = FakeRenderer("NBA")
        nba.has_live_games = lambda: True
        nba.game = lambda: SimpleNamespace(status="live")
        self.router.nba = nba
        self.router.configure_rotation(("mlb", "nhl", "nba"), interval=12)
        self.mlb.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.game = lambda: SimpleNamespace(status="final")
        slot = Slot()
        self.router.set_bullpen_slots((slot,))
        self.assertEqual(self.router.frame(), "NBA")
        self.assertEqual(slot.calls, 0)

    def test_bullpen_suppressed_by_live_english_football(self):
        from types import SimpleNamespace

        class Slot:
            def __init__(self):
                self.calls = 0

            def frame(self, **kwargs):
                self.calls += 1
                return "BULLPEN"

        now = [12]
        self.router.clock = lambda: now[0]
        english = FakeRenderer("ENGLISH")
        english.has_live_games = lambda: True
        english.game = lambda: SimpleNamespace(status="live")
        self.router.english = english
        self.router.configure_rotation(("mlb", "nhl", "english"), interval=12)
        self.mlb.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.game = lambda: SimpleNamespace(status="final")
        slot = Slot()
        self.router.set_bullpen_slots((slot,))
        self.assertEqual(self.router.frame(), "ENGLISH")
        self.assertEqual(slot.calls, 0)

    def test_crashing_bullpen_falls_back_to_normal_sport(self):
        from types import SimpleNamespace

        class CrashingSlot:
            def frame(self, **kwargs):
                raise RuntimeError("plugin render failed")

        now = [12]
        self.router.clock = lambda: now[0]
        self.router.configure_rotation(("mlb", "nhl"), interval=12)
        self.mlb.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.game = lambda: SimpleNamespace(status="final")
        self.router.set_bullpen_slots((CrashingSlot(),))
        self.assertEqual(self.router.frame(), "MLB")

    def test_repeated_bullpen_failures_quarantine_plugin(self):
        from types import SimpleNamespace

        class CrashingSlot:
            def __init__(self):
                self.calls = 0

            def frame(self, **kwargs):
                self.calls += 1
                raise RuntimeError("broken plugin")

        now = [12]
        self.router.clock = lambda: now[0]
        self.router.configure_rotation(("mlb", "nhl"), interval=12)
        self.mlb.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.game = lambda: SimpleNamespace(status="final")
        slot = CrashingSlot()
        self.router.set_bullpen_slots((slot,))
        now[0] += 12  # Enter the plugin slot after rotation starts.
        for _ in range(5):
            self.assertEqual(self.router.frame(), "NHL")
        self.assertEqual(slot.calls, 3)
        self.assertEqual(self.router._bullpen_failures[0], 3)
        # Reconfiguration explicitly clears the quarantine.
        self.router.set_bullpen_slots((slot,))
        self.router.frame()
        self.assertEqual(slot.calls, 4)

    def test_bullpen_health_reports_quarantine_and_reset(self):
        class Slot:
            def frame(self, **kwargs):
                return None

        slot = Slot()
        self.router.set_bullpen_slots((slot,))
        self.assertEqual(self.router.bullpen_health(),
                         ({"slot": 0, "failures": 0, "status": "healthy"},))
        self.router._bullpen_failures[0] = 1
        self.assertEqual(self.router.bullpen_health()[0]["status"], "degraded")
        self.router._bullpen_failures[0] = 3
        snapshot = self.router.bullpen_health()
        self.assertEqual(snapshot[0]["status"], "quarantined")
        self.assertEqual(snapshot[0]["failures"], 3)
        self.router.set_bullpen_slots((slot,))
        self.assertEqual(self.router.bullpen_health()[0]["status"], "healthy")

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



    def test_live_game_suppresses_news_until_final(self):
        from types import SimpleNamespace

        class FakeNews:
            def items(self):
                return [SimpleNamespace(source="Test", text="Headline")]

        state = {"live": True}
        now = [0]
        self.router.clock = lambda: now[0]
        self.router.configure_rotation(("mlb", "nhl"), interval=12)
        self.router.news = FakeNews()
        self.router.settings_getter = lambda: {"news": {
            "rotation_interval": 1, "scroll_chars_per_second": 1}}
        self.mlb.has_live_games = lambda: False
        self.nhl.has_live_games = lambda: state["live"]
        self.mlb.game = lambda: SimpleNamespace(status="scheduled")
        self.nhl.game = lambda: SimpleNamespace(status="live" if state["live"] else "final")
        self.assertEqual(self.router.frame(), "NHL")
        state["live"] = False
        self.assertNotEqual(self.router.frame(), "NHL")

    def test_no_news_avoids_live_probe_in_single_sport_mode(self):
        class EmptyNews:
            def items(self):
                return []

        self.router.news = EmptyNews()
        self.router.settings_getter = lambda: {"news": {}}
        self.router.set_active_sport("mlb")
        def unexpected_probe():
            raise AssertionError("No live status probe needed without headlines")
        self.mlb.has_live_games = unexpected_probe
        self.assertEqual(self.router.frame(), "MLB")


if __name__ == "__main__":
    unittest.main()
