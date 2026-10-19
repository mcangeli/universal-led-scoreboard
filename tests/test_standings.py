"""Standings foundation regression tests."""
import unittest

from universal_led.standings import Standing, order_standings


def row(team, *, league="EPL", group="Premier League", points=10, gd=2, rank=None):
    return Standing(league, group, team, 5, 3, 1, 1, points, gd, rank)


class StandingsTests(unittest.TestCase):
    def test_official_order_uses_provider_rank(self):
        rows = [row("ARS", rank=2), row("MUN", rank=1)]
        self.assertEqual([r.team_id for r in order_standings(rows)], ["MUN", "ARS"])

    def test_official_order_requires_ranks(self):
        with self.assertRaises(ValueError):
            order_standings([row("ARS")])

    def test_provisional_football_order_by_points_then_goal_difference(self):
        rows = [row("A", points=7, gd=8), row("B", points=10, gd=0),
                row("C", points=7, gd=10)]
        self.assertEqual([r.team_id for r in order_standings(rows, policy="football")],
                         ["B", "C", "A"])

    def test_unresolved_football_tie_preserves_feed_order(self):
        rows = [row("A"), row("B")]
        self.assertEqual(order_standings(rows, policy="football"), tuple(rows))

    def test_rejects_cross_league_ranking(self):
        with self.assertRaises(ValueError):
            order_standings([row("A"), row("B", league="MLS")], policy="football")

    def test_rejects_invalid_records(self):
        with self.assertRaises(ValueError):
            Standing("EPL", "Premier League", "A", 2, 2, 1)
        with self.assertRaises(ValueError):
            Standing("EPL", "Premier League", "A", -1, 0, 0)
        with self.assertRaises(ValueError):
            row("A", rank=0)

    def test_rejects_unknown_policy(self):
        with self.assertRaises(ValueError):
            order_standings([row("A")], policy="baseball")


if __name__ == "__main__":
    unittest.main()
