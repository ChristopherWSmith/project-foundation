"""init.py turns the foundation into a clean product repo. Only runs in the foundation folder itself."""
from __future__ import annotations

import json
import shutil
import unittest

from helpers import CHRIS, REPO, REVIEWER, git, sh, tmpdir

TEMPLATE = (REPO / ".foundation/IS_TEMPLATE").exists()


@unittest.skipUnless(TEMPLATE, "init tests run in the foundation folder, not in product repos")
class Init(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tmpdir()
        cls.repo = cls.tmp / "app"
        shutil.copytree(REPO, cls.repo, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        cls.out = sh(["python3", "scripts/init.py", "Acme & Co Budget", "--github-owner", CHRIS, "--reviewer", REVIEWER,
                      "--description", "Budgets for families"], cls.repo)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_placeholders_filled_and_marker_gone(self):
        self.assertFalse((self.repo / ".foundation/IS_TEMPLATE").exists())
        res = sh("python3 scripts/checks/check_hygiene.py", self.repo, check=False)
        self.assertNotIn("placeholder", res.stdout)
        self.assertIn("# Acme & Co Budget", (self.repo / "README.md").read_text())
        self.assertNotIn("template-note", (self.repo / "README.md").read_text())
        self.assertIn("@chris", (self.repo / ".github/CODEOWNERS").read_text())
        cfg = json.loads((self.repo / ".foundation/review.json").read_text())
        self.assertEqual((cfg["reviewers"], cfg["human_approvers"]), ([REVIEWER], [CHRIS]))

    def test_git_branches(self):
        self.assertEqual(git(self.repo, "branch", "--show-current"), "staging")
        self.assertTrue(git(self.repo, "rev-parse", "--verify", "main"))
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    def test_fresh_repo_passes_every_check(self):
        res = sh("./scripts/check-all.sh --base main", self.repo, check=False)
        self.assertEqual(res.returncode, 0, res.stdout)
        gates = sh("python3 scripts/checks/quality_gates.py", self.repo, check=False)
        self.assertEqual(gates.returncode, 0, gates.stdout)
        self.assertIn("stage=bootstrap", gates.stdout)
        self.assertTrue((self.repo / "brand/dist/tokens.css").exists())

    def test_workflows_lint_clean(self):
        actionlint = shutil.which("actionlint")
        if not actionlint:
            self.skipTest("actionlint not installed")
        res = sh([actionlint, *map(str, (self.repo / ".github/workflows").glob("*.yml"))], self.repo, check=False)
        self.assertEqual(res.returncode, 0, res.stdout)

    def test_runs_only_once(self):
        res = sh(["python3", "scripts/init.py", "Again", "--github-owner", CHRIS], self.repo, check=False)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Already initialised", res.stderr)

    def test_leftover_placeholder_is_caught(self):
        p = self.repo / "docs/product/VISION.md"
        original = p.read_text()
        p.write_text(original + "\nOwner: __OWNER__\n")
        try:
            res = sh("python3 scripts/checks/check_hygiene.py", self.repo, check=False)
            self.assertIn("placeholder __OWNER__ left in", res.stdout)
        finally:
            p.write_text(original)

    def test_without_reviewer_the_gate_stays_closed(self):
        repo = self.tmp / "noreviewer"
        shutil.copytree(REPO, repo, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        out = sh(["python3", "scripts/init.py", "X", "--github-owner", CHRIS], repo).stdout
        self.assertIn("PRs into staging stay blocked", out)
        self.assertIn("REPLACE-WITH", (repo / ".foundation/review.json").read_text())


if __name__ == "__main__":
    unittest.main()
