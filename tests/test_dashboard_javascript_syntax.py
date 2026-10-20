"""Catch broken inline dashboard scripts before the updater installs them."""
import re
import shutil
import subprocess
import unittest

from universal_led import configurator


def dashboard_script():
    scripts = re.findall(r"<script(?:\\s[^>]*)?>(.*?)</script>", configurator.HTML, re.S | re.I)
    if not scripts:
        raise AssertionError("Dashboard has no inline JavaScript")
    return "\n".join(scripts).replace("__TOKEN__", "'test-token'")


class DashboardJavascriptSyntaxTests(unittest.TestCase):
    def test_news_loaders_have_separate_statements(self):
        script = dashboard_script()
        self.assertNotRegex(script, r"textContent\\s*=\\s*['\\\"]{2}\\s+newsGroupLoaded\\(")

    def test_branch_selection_regex_is_not_double_escaped(self):
        script = dashboard_script()
        self.assertIn("const releaseMatch=", script)
        line = next(line for line in script.splitlines() if "const releaseMatch=" in line)
        self.assertNotIn(r"\\\\/", line)
        self.assertNotIn(r"\\\\d", line)

    @unittest.skipUnless(shutil.which("node"), "Node.js unavailable: JavaScript parser check skipped")
    def test_dashboard_script_parses_with_node(self):
        result = subprocess.run(
            ["node", "--check", "-"],
            input=dashboard_script(), text=True, capture_output=True, timeout=15,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
