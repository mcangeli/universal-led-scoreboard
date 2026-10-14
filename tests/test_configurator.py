import json
import tempfile
import unittest
from pathlib import Path
from universal_led.config_store import read_config,save_config
from universal_led.configurator import make_handler

class ConfiguratorTests(unittest.TestCase):
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as root:
            save_config(root,'teams',{'ATL':'#123456'})
            save_config(root,'scoreboard',{'accent':[1,2,3]})
            data=read_config(root)
            self.assertEqual(data['teams']['ATL'],(18,52,86))
            self.assertEqual(data['scoreboard']['accent'],(1,2,3))
    def test_backup(self):
        with tempfile.TemporaryDirectory() as root:
            save_config(root,'teams',{'ATL':[1,2,3]})
            save_config(root,'teams',{'ATL':[4,5,6]})
            backups=list((Path(root)/'backups').glob('teams-*.json'))
            self.assertEqual(len(backups),1)
            self.assertEqual(json.loads(backups[0].read_text())['ATL'],[1,2,3])
    def test_invalid_no_write(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                save_config(root,'scoreboard',{'accent':[999,0,0]})
            self.assertFalse((Path(root)/'scoreboard.json').exists())
    def test_unknown_section(self):
        with self.assertRaises(ValueError):
            save_config('/tmp','something',{})
    def test_handler_creation(self):
        self.assertTrue(make_handler('/tmp','test-token'))
if __name__=='__main__':
    unittest.main()
