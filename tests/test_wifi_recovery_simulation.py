import unittest
from universal_led.wifi_recovery_simulation import simulate_recovery

class RecoverySimulationTests(unittest.TestCase):
    def test_successful_recovery_removes_state(self):
        result=simulate_recovery()
        self.assertTrue(result['recovered'])
        self.assertTrue(result['command_attempted'])
        self.assertFalse(result['state_remaining'])
        self.assertFalse(result['network_changed'])

    def test_confirmation_cancels_recovery(self):
        result=simulate_recovery(cancel=True)
        self.assertFalse(result['recovered'])
        self.assertFalse(result['command_attempted'])
        self.assertFalse(result['state_remaining'])

    def test_failed_command_preserves_state(self):
        result=simulate_recovery(command_succeeds=False)
        self.assertFalse(result['recovered'])
        self.assertTrue(result['command_attempted'])
        self.assertTrue(result['state_remaining'])

    def test_corrupt_state_does_not_run_command(self):
        result=simulate_recovery(corrupt=True)
        self.assertEqual(result['error'],'ValueError')
        self.assertFalse(result['command_attempted'])

    def test_simulation_has_no_real_network_calls(self):
        from pathlib import Path
        source=(Path(__file__).resolve().parents[1]/
                'universal_led'/'wifi_recovery_simulation.py').read_text()
        self.assertNotIn('subprocess.run(',source)
        self.assertNotIn('os.system(',source)

if __name__=='__main__':
    unittest.main()
