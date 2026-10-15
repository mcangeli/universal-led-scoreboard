"""Game-day regression fixtures for pregame, live and final transitions."""
import copy
import unittest

from universal_led.mlb_data import parse_schedule
from universal_led.mlb_palette_v11 import MLBPaletteScreen


def fixture(abstract, detailed, inning=None, top=True, outs=0, bases=()):
    game = {
        'gameDate': '2026-10-15T17:00:00Z',
        'teams': {
            'away': {'team': {'id': 139}, 'score': 0, 'leagueRecord': {'wins': 90, 'losses': 72},
                     'probablePitcher': {'fullName': 'Shane McClanahan'}},
            'home': {'team': {'id': 114}, 'score': 0, 'leagueRecord': {'wins': 92, 'losses': 70},
                     'probablePitcher': {'fullName': 'Tanner Bibee'}},
        },
        'status': {'abstractGameState': abstract, 'detailedState': detailed},
    }
    if inning is not None:
        game['linescore'] = {
            'currentInning': inning, 'isTopInning': top, 'outs': outs,
            'offense': {base: {'id': n} for n, base in enumerate(bases, 1)},
            'teams': {'away': {'hits': 3, 'errors': 0}, 'home': {'hits': 5, 'errors': 1}},
        }
    return {'dates': [{'games': [game]}]}


class GameTransitionTests(unittest.TestCase):
    def test_pregame_to_live_to_final_uses_same_teams(self):
        cases = [
            ('Preview', 'Scheduled', None, 'pregame'),
            ('Live', 'In Progress', 1, 'live'),
            ('Live', 'In Progress', 10, 'live'),
            ('Final', 'Final', 10, 'final'),
        ]
        for abstract, detailed, inning, expected in cases:
            with self.subTest(status=expected, inning=inning):
                game = parse_schedule(fixture(abstract, detailed, inning))[0]
                self.assertEqual((game.away, game.home), ('TBR', 'CLE'))
                self.assertEqual(game.status, expected)
                self.assertEqual((game.away_probable, game.home_probable),
                                 ('Shane McClanahan', 'Tanner Bibee'))
                frame = MLBPaletteScreen(game).render()
                self.assertEqual((frame.width, frame.height), (64, 32))

    def test_live_occupancy_outs_and_inning_half(self):
        game = parse_schedule(fixture('Live', 'In Progress', 7, False, 2,
                                      ('first', 'second', 'third')))[0]
        self.assertEqual(game.inning_half, 'bottom')
        self.assertEqual(game.outs, 2)
        self.assertEqual(game.bases, (True, True, True))
        self.assertEqual((game.away_hits, game.home_hits, game.home_errors), (3, 5, 1))

    def test_delay_and_postponement_are_not_live(self):
        for detailed, expected in [('Delayed', 'delayed'), ('Postponed', 'postponed')]:
            with self.subTest(detailed=detailed):
                game = parse_schedule(fixture('Live', detailed, 4))[0]
                self.assertEqual(game.status, expected)
                self.assertEqual(MLBPaletteScreen(game).render().width, 64)


if __name__ == '__main__':
    unittest.main()
