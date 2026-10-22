"""Regression coverage for discarding custom news source edits."""
import unittest

from universal_led import configurator


class NewsDiscardNavigationTests(unittest.TestCase):
    def test_discard_restores_custom_news_editor(self):
        html = configurator.HTML
        start = html.index("function discardNewsEdits(){")
        end = html.index("\n}", start)
        discard = html[start:end]
        self.assertIn("newsSources=clone(newsSourcesSaved)", discard)
        self.assertIn("newsSourcesDirty=false", discard)
        self.assertIn("renderNewsSources();", discard)
        self.assertIn("document.getElementById('news-status').textContent=''", discard)
        self.assertIn("delete newsSettingsSaved[group]", discard)

    def test_navigation_cancel_preserves_unsaved_news_edits(self):
        html = configurator.HTML
        self.assertIn("if(!confirm('You have unsaved Content & News changes. Leave this page without saving?'))return;discardNewsEdits();", html)


if __name__ == "__main__":
    unittest.main()
