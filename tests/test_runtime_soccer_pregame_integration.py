"""Shared runtime must reuse standings snapshots and configured kickoff timezone."""
import unittest
from types import SimpleNamespace
from universal_led.multisport_runtime import MultiSportRenderer


class Adapter:
    def __init__(self):
        self.display = SimpleNamespace(timezone="America/New_York")
        self.caches = None
        self.cache = None

    def set_standings_caches(self, caches):
        self.caches = caches

    def set_standings_cache(self, cache):
        self.cache = cache

    def frame(self):
        return None


class RuntimeSoccerIntegrationTests(unittest.TestCase):
    def test_existing_standings_caches_are_shared(self):
        english, mls, nwsl = Adapter(), Adapter(), Adapter()
        caches = {"EPL": object(), "MLS": object(), "NWSL": object()}
        runtime = MultiSportRenderer(Adapter(), Adapter(), english_renderer=english,
            mls_renderer=mls, nwsl_renderer=nwsl,
            standings_rotation=SimpleNamespace(caches=caches))
        self.assertIs(english.caches["EPL"], caches["EPL"])
        self.assertIs(mls.cache, caches["MLS"])
        self.assertIs(nwsl.cache, caches["NWSL"])

    def test_timezone_getter_updates_all_soccer_adapters(self):
        english, mls, nwsl = Adapter(), Adapter(), Adapter()
        timezone = ["America/Chicago"]
        runtime = MultiSportRenderer(Adapter(), Adapter(), english_renderer=english,
            mls_renderer=mls, nwsl_renderer=nwsl,
            timezone_getter=lambda: timezone[0])
        runtime._sync_soccer_timezone()
        self.assertEqual(english.display.timezone, "America/Chicago")
        timezone[0] = "America/Los_Angeles"
        runtime._sync_soccer_timezone()
        self.assertEqual(mls.display.timezone, "America/Los_Angeles")
        self.assertEqual(nwsl.display.timezone, "America/Los_Angeles")


if __name__ == "__main__":
    unittest.main()
