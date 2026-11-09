"""The full loop at the contract level: implementer → handoff → review with a P1 → fix → stale review rejected →
re-review → gate green → squash into staging → release blocked in bootstrap → development stage → release allowed."""
from __future__ import annotations

import json
import shutil
import unittest

from helpers import IMPLEMENTER, commit_all, fresh_repo, git, project_json, sh, tmpdir, write
from test_gates import HANDOFF_OK, body_with, finding, review


class ClaudeCodexLoop(unittest.TestCase):
    def setUp(self):
        self.tmp = tmpdir()
        self.repo = fresh_repo(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def py(self, *args):
        return sh(["python3", *args], self.repo, check=False)

    def gate(self, sha, reviews):
        fx = self.tmp / "fx.json"
        fx.write_text(json.dumps({"pr": {"number": 1, "head": {"sha": sha, "ref": "feat/CU-1-sum"}, "base": {"ref": "staging"},
                                         "user": {"login": IMPLEMENTER}, "labels": []}, "reviews": reviews,
                                  "commits": [{"sha": sha, "author": {"login": IMPLEMENTER}, "committer": {"login": IMPLEMENTER}}]}))
        return self.py("scripts/checks/review_gate.py", "--fixture", str(fx))

    def test_full_loop(self):
        r = self.repo
        project_json(r, "bootstrap")
        commit_all(r, "selftest config")

        # 1. Implementer: branch, code with a bug, test, handoff
        git(r, "checkout", "-q", "-b", "feat/CU-1-sum")
        write(r / "selftest/sum.mjs", "export const sum = (a, b) => a - b;\n")
        write(r / "selftest/sum.test.mjs", "import test from 'node:test';\nimport assert from 'node:assert';\nimport { sum } from './sum.mjs';\ntest('sum', () => assert.equal(sum(2, 2), 4));\n")
        sha1 = commit_all(r, "feat: sum (CU-1)")
        body = self.tmp / "pr.md"
        body.write_text(body_with(HANDOFF_OK))
        self.assertEqual(self.py("scripts/checks/check_handoff.py", "--body-file", str(body), "--author", IMPLEMENTER).returncode, 0)

        # 2. No review yet: gate closed
        self.assertIn("no review yet", self.gate(sha1, []).stdout)

        # 3. Reviewer finds a P1 on sha1
        r1 = review(sha1, "request_changes", [finding("F1", "P1", "open")], at="2026-11-07T10:00:00Z")
        res = self.gate(sha1, [r1])
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("open blocking finding(s): P1 F1", res.stdout)

        # 4. Fix → new head; the old review no longer counts
        write(r / "selftest/sum.mjs", "export const sum = (a, b) => a + b;\n")
        sha2 = commit_all(r, "fix: sum adds (CU-1)")
        res = self.gate(sha2, [r1])
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("this one hasn't been", res.stdout)

        # 5. Re-review on sha2: resolved, approve → green
        r2 = review(sha2, "approve", [finding("F1", "P1", "resolved")], at="2026-11-07T11:00:00Z")
        res = self.gate(sha2, [r1, r2])
        self.assertEqual(res.returncode, 0, res.stdout)

        # 6. Auto-merge squashes into staging
        git(r, "checkout", "-q", "staging")
        git(r, "merge", "-q", "--squash", "feat/CU-1-sum")
        commit_all(r, "feat: sum (#1)")

        # 7. Release while in bootstrap → blocked
        res = self.py("scripts/checks/promotion_gate.py", "--head-ref", "staging", "--main-ref", "main")
        self.assertIn("before shipping", res.stdout)

        # 8. Development stage with real gates: the real test runs and passes
        project_json(r, "development", {"install": "node -e 0", "lint": "node -e 0", "typecheck": "node -e 0",
                                        "test": "node --test selftest/sum.test.mjs", "build": "node -e 0", "audit": "node -e 0"})
        commit_all(r, "chore: development stage")
        self.assertEqual(self.py("scripts/checks/quality_gates.py").returncode, 0)

        # 9. Release from staging allowed; from a feature branch never
        self.assertEqual(self.py("scripts/checks/promotion_gate.py", "--head-ref", "staging", "--main-ref", "main").returncode, 0)
        self.assertNotEqual(self.py("scripts/checks/promotion_gate.py", "--head-ref", "feat/CU-2", "--main-ref", "main").returncode, 0)


if __name__ == "__main__":
    unittest.main()
