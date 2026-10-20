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
        self.assertIn("if(name!=='news'&&(newsSourcesDirty||newsSettingsDirty())){if(!confirm('You have unsaved Content & News changes.",html)
        self.assertIn('discardNewsEdits();',html)
        self.assertIn("if(name==='news'){if(!newsSourcesDirty)loadNewsSources();",html)

    def test_other_news_controls_track_unsaved_changes(self):
        html=configurator.HTML
        for group in ('automatic','scoring','timing','interruptions','standings'):
            with self.subTest(group=group):
                self.assertIn("newsGroupCanLoad('"+group+"')",html)
                self.assertIn("newsGroupLoaded('"+group+"')",html)
                self.assertIn("newsGroupSaved('"+group+"')",html)
        self.assertIn('newsSettingsDirty()',html)

    def test_confirmed_discard_clears_all_news_dirty_snapshots(self):
        html=configurator.HTML
        discard=html.split('function discardNewsEdits(){',1)[1].split('function showPage(name)',1)[0]
        self.assertIn('newsSources=clone(newsSourcesSaved);newsSourcesDirty=false;',discard)
        self.assertIn('delete newsSettingsSaved[group]',discard)
        self.assertIn("if(!confirm('You have unsaved Content & News changes.",html)
        self.assertIn('return;discardNewsEdits();',html)

    def test_failed_load_does_not_record_saved_baseline(self):
        html=configurator.HTML
        for name,group in (
            ('AutomaticNews','automatic'),('ScoringAlerts','scoring'),
            ('NewsTiming','timing'),('GameInterruptions','interruptions'),
            ('StandingsSettings','standings')
        ):
            with self.subTest(group=group):
                load=html.split('async function load'+name+'(){',1)[1].split('async function save'+name+'(){',1)[0]
                self.assertLess(load.index("newsGroupLoaded('"+group+"')"),load.index('catch('))

    def test_edit_add_remove_and_save_update_dirty_state(self):
        html=configurator.HTML
        self.assertIn('source[key]=type===\'number\'?Number(input.value):input.value;markNewsSourcesDirty()',html)
        self.assertIn('source.enabled=checkbox.checked;markNewsSourcesDirty()',html)
        self.assertIn('newsSources.splice(index,1);renderNewsSources();markNewsSourcesDirty()',html)
        self.assertIn('newsSourcesSaved=clone(newsSources);newsSourcesDirty=false;renderNewsSources();status.textContent=\'News sources saved.\'',html)


if __name__=='__main__':
    unittest.main()
