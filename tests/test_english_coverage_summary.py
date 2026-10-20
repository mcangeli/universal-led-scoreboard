"""English Football game and standings coverage summaries."""
import unittest
from universal_led import configurator


class EnglishCoverageSummaryTests(unittest.TestCase):
    def test_separate_live_coverage_summaries_exist(self):
        html=configurator.HTML
        self.assertIn('id="english-game-coverage-summary"',html)
        self.assertIn('id="english-standings-coverage-summary"',html)
        self.assertIn('function refreshEnglishCoverageSummary()',html)

    def test_summaries_track_distinct_checkbox_groups(self):
        html=configurator.HTML
        self.assertIn("document.querySelectorAll('#english-leagues input:checked').length",html)
        self.assertIn("document.querySelectorAll('#english-standings-leagues input:checked').length",html)
        self.assertIn("event.target.closest('#english-leagues,#english-standings-leagues')",html)

    def test_standings_require_global_enablement(self):
        self.assertIn('Standings pages also require Standings Pages to be enabled under Content/News.',configurator.HTML)


if __name__=='__main__':
    unittest.main()
