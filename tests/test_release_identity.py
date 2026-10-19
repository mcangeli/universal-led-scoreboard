"""Dashboard version reflects the actual installed build and release channel."""
import unittest
from unittest.mock import patch

from universal_led import release


class ReleaseIdentityTests(unittest.TestCase):
    def test_development_branch_and_commit(self):
        def git(*args):
            if args[0] == 'rev-parse':
                return 'abc12345'
            if args[0] == 'symbolic-ref':
                return 'feature/0.7.0-scoring-standings'
            return None
        with patch.object(release, '_git', side_effect=git):
            self.assertEqual(release.display_version(),
                             'v0.7.0 · feature/0.7.0-scoring-standings · abc12345')

    def test_exact_release_tag_takes_priority(self):
        with patch.object(release, '_git', side_effect=lambda *args:
                          'v0.7.0' if args[0] == 'describe' else None):
            self.assertEqual(release.installed_release(), 'v0.7.0')

    def test_detached_checkout_without_release_metadata(self):
        with patch.object(release, '_git', return_value=None):
            self.assertEqual(release.display_version(), 'v0.7.0 · development')


if __name__ == '__main__':
    unittest.main()
