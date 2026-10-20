"""Dashboard version reflects the actual installed build and release channel."""
import unittest
from unittest.mock import patch
from tempfile import TemporaryDirectory
from pathlib import Path

from universal_led import release


class ReleaseIdentityTests(unittest.TestCase):
    def test_development_branch_and_commit(self):
        def git(*args):
            if args[0] == 'rev-parse':
                return 'abc12345'
            if args[0] == 'symbolic-ref':
                return 'feature/0.7.0-scoring-standings'
            return None
        with patch.object(release, 'checkout_branch', return_value=None), patch.object(release, '_git', side_effect=git):
            self.assertEqual(release.display_version(),
                             'v0.7.0 · feature/0.7.0-scoring-standings · abc12345')

    def test_exact_release_tag_takes_priority(self):
        with patch.object(release, '_git', side_effect=lambda *args:
                          'v0.7.0' if args[0] == 'describe' else None):
            self.assertEqual(release.installed_release(), 'v0.7.0')

    def test_detached_checkout_at_main_head(self):
        def git(*args):
            if args[0] == 'branch':
                return 'origin/main\norigin/feature/0.7.0-scoring-standings'
            return None
        with patch.object(release, 'checkout_branch', return_value=None), patch.object(release, '_git', side_effect=git):
            self.assertEqual(release.installed_release(), 'main')

    def test_installed_main_branch_works_without_git_subprocess(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / '.git').mkdir()
            (root / '.git' / 'HEAD').write_text('ref: refs/heads/main' + chr(10), encoding='utf-8')
            with patch.object(release, '__file__', str(root / 'universal_led' / 'release.py')):
                with patch.object(release, '_git', return_value=None):
                    self.assertEqual(release.checkout_branch(), 'main')
                    self.assertEqual(release.installed_release(), 'main')

    def test_detached_checkout_without_release_metadata(self):
        with patch.object(release, 'checkout_branch', return_value=None), patch.object(release, '_git', return_value=None):
            self.assertEqual(release.display_version(), 'v0.7.0 · development')


if __name__ == '__main__':
    unittest.main()
