"""Guard against accidental nested sport configuration panels."""
import re
import unittest
from html.parser import HTMLParser

from universal_led.configurator import HTML
from universal_led.sport_settings import SPORTS

# EFL is a reserved legacy setting, not a selectable dashboard sport.
DASHBOARD_SPORTS = tuple(sport for sport in SPORTS if sport != 'efl')


class PanelTree(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.panels = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div" and "sport-config-panel" in attrs.get("class", "").split():
            name = attrs.get("data-sport-panel")
            if any(panel in self.stack for panel in self.panels):
                self.errors.append("Nested panel: " + str(name))
            self.panels.append(name)
            self.stack.append(name)
        else:
            self.stack.append(None)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        # HTMLParser doesn't manage HTML void elements. Only div nesting matters.
        if tag == "div":
            if self.stack:
                self.stack.pop()


class DivPanelParser(HTMLParser):
    """Track only div elements to avoid void-element stack errors."""
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.open_panels = []
        self.panels = []
        self.nested = []

    def handle_starttag(self, tag, attrs):
        if tag != "div":
            return
        self.depth += 1
        values = dict(attrs)
        if "sport-config-panel" in values.get("class", "").split():
            name = values.get("data-sport-panel")
            if self.open_panels:
                self.nested.append(name)
            self.open_panels.append((name, self.depth))
            self.panels.append(name)

    def handle_endtag(self, tag):
        if tag != "div":
            return
        if self.open_panels and self.open_panels[-1][1] == self.depth:
            self.open_panels.pop()
        self.depth -= 1


class SportPanelStructureTests(unittest.TestCase):
    def test_all_sport_panels_are_independent(self):
        parser = DivPanelParser()
        parser.feed(HTML)
        self.assertEqual(parser.panels, list(DASHBOARD_SPORTS))
        self.assertEqual(parser.nested, [])
        self.assertEqual(parser.open_panels, [])

    def test_dropdown_selects_only_requested_panel(self):
        self.assertIn("panel.hidden=panel.dataset.sportPanel!==name", HTML)
        for sport in DASHBOARD_SPORTS:
            self.assertIn('<option value="'+sport+'">', HTML)
            self.assertIn('data-sport-panel="'+sport+'" hidden', HTML)


if __name__ == '__main__':
    unittest.main()
