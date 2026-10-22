"""End-to-end regression for live-game rotation after a favorite finishes."""
import unittest
from types import SimpleNamespace

from universal_led.multisport_runtime import MultiSportRenderer
from universal_led.nhl_engine import ConfiguredNHLRenderer
from universal_led.nba_engine import ConfiguredNBARenderer


class Feed:
    def __init__(self, games):
        self.current = games

    def games(self):
        return self.current


def game(home, away, status):
    return SimpleNamespace(home=home, away=away, status=status)


class LiveTransitionTests(unittest.TestCase):
    def test_finished_nhl_favorite_does_not_remove_nhl_from_global_rotation(self):
        now = [0]
        clock = lambda: now[0]
        nhl_feed = Feed([game("BOS", "NYR", "live"), game("TOR", "MTL", "live")])
        nba_feed = Feed([game("BOS", "NYK", "live"), game("CHI", "DET", "live")])
        nhl = ConfiguredNHLRenderer(nhl_feed, favorite_teams=["BOS"], mode="fallback", clock=clock)
        nba = ConfiguredNBARenderer(nba_feed, favorite_teams=["BOS"], mode="fallback", clock=clock)
        router = MultiSportRenderer(None, nhl, nba_renderer=nba, clock=clock)
        router.configure_rotation(("nhl", "nba"), interval=5)
        self.assertEqual(router._live_sports(), ("nhl", "nba"))
        nhl_feed.current[0].status = "final"
        self.assertEqual(router._live_sports(), ("nhl", "nba"))
        self.assertEqual(nhl.game(), nhl_feed.current[1])
        now[0] = 5
        self.assertEqual(router._selected(), "nba")
        nba_feed.current[0].status = "final"
        self.assertEqual(router._live_sports(), ("nhl", "nba"))
        self.assertEqual(nba.game(), nba_feed.current[1])
        now[0] = 10
        self.assertEqual(router._selected(), "nhl")
        nhl_feed.current[1].status = "final"
        self.assertEqual(router._live_sports(), ("nba",))
        self.assertEqual(router._selected(), "nba")

    def test_only_last_live_game_finishing_clears_global_priority(self):
        now = [0]
        clock = lambda: now[0]
        nhl_feed = Feed([game("BOS", "NYR", "final")])
        nba_feed = Feed([game("BOS", "NYK", "final"), game("CHI", "DET", "live")])
        nhl = ConfiguredNHLRenderer(nhl_feed, favorite_teams=["BOS"], mode="fallback", clock=clock)
        nba = ConfiguredNBARenderer(nba_feed, favorite_teams=["BOS"], mode="fallback", clock=clock)
        router = MultiSportRenderer(None, nhl, nba_renderer=nba, clock=clock)
        router.configure_rotation(("nhl", "nba"), interval=5)
        self.assertEqual(router._live_sports(), ("nba",))
        nba_feed.current[1].status = "final"
        self.assertEqual(router._live_sports(), ())
        self.assertEqual(router._available(), ("nhl", "nba"))


if __name__ == "__main__":
    unittest.main()
