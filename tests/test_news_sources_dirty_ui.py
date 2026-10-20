"""Content & News source edits remain visible until saved or explicitly abandoned."""
import unittest
from universal_led import configurator


class NewsSourcesDirtyUITests(unittest.TestCase):
    def test_news_sources_track_saved_snapshot(self):
        html=configurator.HTML
        self.assertIn('newsSourcesSaved=clone(newsSources);newsSourcesDirty=false;',html)
        self.assertIn('newsSourcesDirty=JSON.stringify(newsSources)!==JSON.stringify(newsSourcesSaved)',html)

    def test_navigation_warns_before_leaving_unsaved_sources(self):
        html=configurator.HTML
        self.assertIn("if(name!=='news'&&(newsSourcesDirty||newsSettingsDirty())&&!confirm('You have unsaved Content & News changes.",html)
        self.assertIn("if(name==='news'){if(!newsSourcesDirty)loadNewsSources();",html)

    def test_other_news_controls_track_unsaved_changes(self):
        html=configurator.HTML
        for group in ('automatic','scoring','timing','interruptions','standings'):
            with self.subTest(group=group):
                self.assertIn("newsGroupCanLoad('"+group+"')",html)
                self.assertIn("newsGroupLoaded('"+group+"')",html)
                self.assertIn("newsGroupSaved('"+group+"')",html)
        self.assertIn('newsSettingsDirty()',html)

    def test_edit_add_remove_and_save_update_dirty_state(self):
        html=configurator.HTML
        self.assertIn('source[key]=type===\'number\'?Number(input.value):input.value;markNewsSourcesDirty()',html)
        self.assertIn('source.enabled=checkbox.checked;markNewsSourcesDirty()',html)
        self.assertIn('newsSources.splice(index,1);renderNewsSources();markNewsSourcesDirty()',html)
        self.assertIn('newsSourcesSaved=clone(newsSources);newsSourcesDirty=false;renderNewsSources();status.textContent=\'News sources saved.\'',html)


if __name__=='__main__':
    unittest.main()
