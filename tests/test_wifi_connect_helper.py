import importlib.util
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

HELPER=Path(__file__).resolve().parents[1]/'scripts'/'universal-led-wifi-connect'
spec=importlib.util.spec_from_file_location('wifi_connect_helper',HELPER)
# Extensionless executable: explicitly load source.
from importlib.machinery import SourceFileLoader
loader=SourceFileLoader('wifi_connect_helper',str(HELPER))
spec=importlib.util.spec_from_loader(loader.name,loader)
module=importlib.util.module_from_spec(spec)
loader.exec_module(module)

class WifiConnectHelperTests(unittest.TestCase):
    def test_preflight_only(self):
        self.assertEqual(module.parse_request(b'{"operation":"preflight"}'),
                         {'operation':'preflight'})
        for data in (b'{"operation":"connect"}',
                     b'{"operation":"preflight","command":"sh"}',
                     b'{"operation":"rollback"}',
                     b'{"operation":"preflight","password":"secret"}',
                     b'[]',b'not json'):
            with self.subTest(data=data),self.assertRaises(ValueError):
                module.parse_request(data)

    def test_size_limit(self):
        with self.assertRaises(ValueError):
            module.parse_request(b'x'*(module.MAX_REQUEST_BYTES+1))

    def test_no_mutating_nmcli_commands(self):
        runner=Mock(return_value=SimpleNamespace(returncode=0,stdout='wlan0:wifi:connected:Home'))
        response=module.preflight(run=runner)
        self.assertFalse(response['switching_enabled'])
        self.assertFalse(response['rollback_armed'])
        self.assertEqual(runner.call_args.args[0],
                         ['nmcli','-t','-f','DEVICE,TYPE,STATE,CONNECTION','device','status'])

    def test_nmcli_failure(self):
        runner=Mock(return_value=SimpleNamespace(returncode=1,stdout=''))
        with self.assertRaises(RuntimeError):
            module.preflight(run=runner)

if __name__=='__main__':
    unittest.main()
