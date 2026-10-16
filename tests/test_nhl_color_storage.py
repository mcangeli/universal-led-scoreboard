import json
import tempfile
import unittest
from pathlib import Path

from universal_led.config_store import read_config, read_nhl_colors, save_config
from universal_led.nhl_colors import NHL_TEAM_COLORS


class NHLColorStorageTests(unittest.TestCase):
    def test_defaults_are_separate_from_mlb(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(read_nhl_colors(directory), NHL_TEAM_COLORS)
            self.assertNotIn('nhl_teams', read_config(directory))

    def test_nhl_override_persists_without_touching_mlb(self):
        with tempfile.TemporaryDirectory() as directory:
            before = read_config(directory)
            save_config(directory, 'nhl_teams', {'BOS': [1, 2, 3]})
            self.assertEqual(read_nhl_colors(directory)['BOS'], (1, 2, 3))
            self.assertEqual(read_config(directory), before)
            self.assertFalse((Path(directory) / 'teams.json').exists())

    def test_rejects_unknown_team_and_invalid_rgb(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                save_config(directory, 'nhl_teams', {'XYZ': [1, 2, 3]})
            with self.assertRaises(ValueError):
                save_config(directory, 'nhl_teams', {'BOS': [256, 2, 3]})

    def test_repeated_saves_make_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            save_config(directory, 'nhl_teams', {'BOS': [1, 2, 3]})
            save_config(directory, 'nhl_teams', {'BOS': [4, 5, 6]})
            backups=list((Path(directory) / 'backups').glob('nhl_teams-*.json'))
            self.assertEqual(len(backups), 1)
            self.assertEqual(json.loads(backups[0].read_text())['BOS'], [1, 2, 3])


if __name__ == '__main__':
    unittest.main()
