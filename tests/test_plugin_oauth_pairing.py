import unittest

from universal_led.plugin_oauth_pairing import PairingError, PairingTickets


class PairingTests(unittest.TestCase):
    def test_single_use(self):
        tickets = PairingTickets()
        ticket = tickets.issue(plugin_id="daily-calendar", provider_id="google-calendar", session_id="admin")
        self.assertTrue(tickets.consume(ticket=ticket, plugin_id="daily-calendar",
                                        provider_id="google-calendar", session_id="admin"))
        with self.assertRaises(PairingError):
            tickets.consume(ticket=ticket, plugin_id="daily-calendar",
                            provider_id="google-calendar", session_id="admin")

    def test_wrong_session_consumes_ticket(self):
        tickets = PairingTickets()
        ticket = tickets.issue(plugin_id="daily-calendar", provider_id="google-calendar", session_id="admin")
        with self.assertRaises(PairingError):
            tickets.consume(ticket=ticket, plugin_id="daily-calendar",
                            provider_id="google-calendar", session_id="other")
        with self.assertRaises(PairingError):
            tickets.consume(ticket=ticket, plugin_id="daily-calendar",
                            provider_id="google-calendar", session_id="admin")

    def test_expiration(self):
        now = [1000]
        tickets = PairingTickets(clock=lambda: now[0])
        ticket = tickets.issue(plugin_id="daily-calendar", provider_id="google-calendar", session_id="admin")
        now[0] += 301
        with self.assertRaises(PairingError):
            tickets.consume(ticket=ticket, plugin_id="daily-calendar",
                            provider_id="google-calendar", session_id="admin")

    def test_other_plugin_not_authorized(self):
        tickets = PairingTickets()
        with self.assertRaises(ValueError):
            tickets.issue(plugin_id="swimming-fish", provider_id="google-calendar", session_id="admin")


if __name__ == "__main__":
    unittest.main()
