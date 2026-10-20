import subprocess
import unittest
from unittest.mock import patch

from universal_led import __version__
from universal_led.release import display_version, installed_commit


class ReleaseVersionTests(unittest.TestCase):
    def test_git_commit_is_shown(self):
        result=subprocess.CompletedProcess([],0,'abc12345\n','')
        with patch('universal_led.release.subprocess.run',return_value=result), \
             patch('universal_led.release.installed_release',return_value='development'):
            self.assertEqual(display_version(),f'v{__version__} · development · abc12345')

    def test_no_git_checkout_falls_back_to_package_version(self):
        with patch('universal_led.release.checkout_branch', return_value=None), \
             patch('universal_led.release.subprocess.run',side_effect=OSError('missing git')):
            self.assertIsNone(installed_commit())
            self.assertEqual(display_version(),f'v{__version__} · development')

    def test_git_failure_falls_back(self):
        result=subprocess.CompletedProcess([],128,'','not a repository')
        with patch('universal_led.release.checkout_branch', return_value=None), \
             patch('universal_led.release.subprocess.run',return_value=result):
            self.assertEqual(display_version(),f'v{__version__} · development')


if __name__=='__main__':
    unittest.main()
