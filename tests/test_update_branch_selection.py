"""Software update page should discover the installed branch without manual search."""
import unittest

from universal_led.configurator import HTML


class UpdateBranchSelectionTests(unittest.TestCase):
    def test_opening_system_page_automatically_checks_git(self):
        self.assertIn("if(name==='system'){refreshSystem();checkSoftwareUpdate();}", HTML)

    def test_server_branch_is_default_after_page_refresh(self):
        self.assertIn("const selected=updateBranchUserSelected?picker.value:data.branch;", HTML)
        self.assertIn("let updateBranchUserSelected=false;", HTML)
        self.assertIn("updateBranchData=data;renderUpdateBranches();", HTML)

    def test_explicit_selection_survives_in_page_recheck(self):
        self.assertIn("function updateBranchChanged(){\n updateBranchUserSelected=true;", HTML)
        self.assertIn("picker.value=visible.includes(selected)?selected:", HTML)

    def test_installed_branch_in_default_filtered_list(self):
        self.assertIn("name===data.branch||name==='main'", HTML)


if __name__ == "__main__":
    unittest.main()
