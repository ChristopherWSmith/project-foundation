"""scripts/github against a stateful mock `gh`: apply → verify round-trip, tampering detected, dry-run writes
nothing, refuses without a staging branch."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parents[1] / "github"
REPO = "chris/workbench"
GOOD_FILES = {".github/CODEOWNERS": "/.github/ @chris\n", ".foundation/review.json": json.dumps({"reviewers": ["astra[bot]"]})}
AGENTS = {"agents": [
    {"role": "implementer", "app_slug": "chris-implementer", "must_not": ["administration", "workflows", "statuses:write"]},
    {"role": "reviewer", "app_slug": "chris-reviewer", "must_not": ["administration", "workflows"]},
]}
INSTALLS = [
    {"app_slug": "chris-implementer", "permissions": {"contents": "write", "pull_requests": "write", "metadata": "read"}},
    {"app_slug": "chris-reviewer", "permissions": {"contents": "read", "pull_requests": "write", "metadata": "read"}},
]


class Protection(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        (bin_dir / "gh").write_text(f"#!/bin/sh\nexec {sys.executable} {HERE / 'mock_gh.py'} \"$@\"\n")
        (bin_dir / "gh").chmod(0o755)
        self.state = self.tmp / "state.json"
        self.log = self.tmp / "log.jsonl"
        self.state.write_text(json.dumps({"repo": {"default_branch": "main"}, "branches": ["main", "staging"], "rulesets": [],
                                          "environments": {}, "files": GOOD_FILES, "installations": INSTALLS, "next_id": 100}))
        self.log.write_text("")
        self.agents = self.tmp / "agents.json"
        self.agents.write_text(json.dumps(AGENTS))
        self.env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "MOCK_GH_STATE": str(self.state), "MOCK_GH_LOG": str(self.log)}

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_script(self, name, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / name), *args], capture_output=True, text=True, env=self.env)

    def mutate(self, fn):
        s = json.loads(self.state.read_text())
        fn(s)
        self.state.write_text(json.dumps(s))

    def test_apply_then_verify_round_trip(self):
        res = self.run_script("apply-protection.py", REPO, "--with", "supabase_drift")
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        s = json.loads(self.state.read_text())
        self.assertEqual(len(s["rulesets"]), 5)
        self.assertFalse(any("$comment" in r for r in s["rulesets"]), "$comment must not be sent to GitHub")
        baseline = next(r for r in s["rulesets"] if "baseline" in r["name"])
        contexts = {c["context"]: c["integration_id"] for r in baseline["rules"] if r["type"] == "required_status_checks"
                    for c in r["parameters"]["required_status_checks"]}
        self.assertEqual(contexts, {"checks": 15368, "security_staging": 15368, "drift": 15368, "selftest": 15368, "supabase_drift": 15368})
        self.assertEqual(s["repo"]["default_branch"], "staging")
        self.assertEqual([p["name"] for p in s["environments"]["production"]], ["main"])

        again = self.run_script("apply-protection.py", REPO, "--with", "supabase_drift")
        self.assertEqual(again.returncode, 0)
        self.assertEqual(len(json.loads(self.state.read_text())["rulesets"]), 5, "re-running must update, not duplicate")

        ver = self.run_script("verify-protection.py", REPO, "--with", "supabase_drift", "--agents", str(self.agents))
        self.assertEqual(ver.returncode, 0, ver.stdout + ver.stderr)
        self.assertNotIn("FAIL", ver.stdout)

    def test_verify_catches_tampering(self):
        self.assertEqual(self.run_script("apply-protection.py", REPO).returncode, 0)
        cases = {
            "bypass added to baseline": (lambda s: s["rulesets"][0].update(bypass_actors=[{"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}]), "bypass"),
            "check no longer pinned to Actions": (lambda s: [c.pop("integration_id") for r in s["rulesets"] if "review gate" in r["name"]
                                                         for rule in r["rules"] for c in rule["parameters"]["required_status_checks"]], "review-gate"),
            "ruleset disabled": (lambda s: s["rulesets"][4].update(enforcement="disabled"), "is active"),
            "production deployable from staging": (lambda s: s["environments"]["production"].append({"id": 1, "name": "staging"}), "production"),
            "agent can edit workflows": (lambda s: s["installations"][0]["permissions"].update(workflows="write"), "no workflows permission"),
            "reviewer not configured": (lambda s: s["files"].update({".foundation/review.json": json.dumps({"reviewers": ["REPLACE-WITH-REVIEWER-LOGIN"]})}), "reviewers configured"),
            "CODEOWNERS only comments": (lambda s: s["files"].update({".github/CODEOWNERS": "# /.github/ @OWNER\n"}), "CODEOWNERS"),
        }
        snapshot = self.state.read_text()
        for name, (fn, expect) in cases.items():
            with self.subTest(name):
                self.state.write_text(snapshot)
                self.mutate(fn)
                res = self.run_script("verify-protection.py", REPO, "--agents", str(self.agents))
                self.assertEqual(res.returncode, 1, res.stdout)
                fails = [l for l in res.stdout.splitlines() if l.startswith("FAIL")]
                self.assertTrue(any(expect in l for l in fails), f"expected a FAIL mentioning {expect!r}, got {fails}")

    def test_dry_run_writes_nothing(self):
        res = self.run_script("apply-protection.py", REPO, "--dry-run")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(self.log.read_text(), "")

    def test_refuses_without_staging(self):
        self.mutate(lambda s: s.update(branches=["main"]))
        res = self.run_script("apply-protection.py", REPO)
        self.assertEqual(res.returncode, 1)
        self.assertIn("no staging branch", res.stderr)


if __name__ == "__main__":
    unittest.main()
