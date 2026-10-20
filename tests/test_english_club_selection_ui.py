"""English club selection search and favorites UX contracts."""
import unittest
from universal_led import configurator


class EnglishClubSelectionTests(unittest.TestCase):
    def test_search_is_not_treated_as_unsaved_configuration(self):
        self.assertIn("event.target.id==='english-team-search'",configurator.HTML)

    def test_favorite_and_search_counts_are_visible(self):
        html=configurator.HTML
        self.assertIn('id="english-team-filter-summary"',html)
        self.assertIn("selected+' favorite clubs selected'",html)
        self.assertIn("visible+' matching clubs'",html)
        self.assertIn("getElementById('english-teams').addEventListener('change',filterEnglishClubs)",html)

    def test_directory_failure_still_refreshes_favorite_count(self):
        html=configurator.HTML
        self.assertIn("(saved favorite)'));return label;\n  }));\n  filterEnglishClubs();",html)


if __name__=='__main__':
    unittest.main()
