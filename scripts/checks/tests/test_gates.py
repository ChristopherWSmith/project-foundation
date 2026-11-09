"""The gates fail when they should. Each test gets a fresh copy of the repo and writes its own config and fixtures."""
from __future__ import annotations

import json
import re
import shutil
import sys
import unittest
from pathlib import Path

from helpers import CHRIS, IMPLEMENTER, REVIEWER, commit_all, fresh_repo, git, project_json, set_json, sh, tmpdir, write

SHA1, SHA2 = "a" * 40, "b" * 40


def review(sha, verdict="approve", findings=(), state="COMMENTED", who=REVIEWER, extra=None, at="2026-11-07T10:00:00Z", body=None):
    contract = {"schema": "foundation-review/v1", "head_sha": sha, "verdict": verdict, "findings": list(findings), **(extra or {})}
    return {"user": {"login": who}, "state": state, "commit_id": sha, "submitted_at": at,
            "body": body if body is not None else f"Review.\n\n```foundation-review\n{json.dumps(contract, indent=2)}\n```"}


def finding(fid="F1", sev="P1", status="open"):
    return {"id": fid, "severity": sev, "status": status, "summary": "Tenant filter missing", "file": "src/a.ts", "line": 3}


def pr(sha=SHA1, author=IMPLEMENTER, base="staging", head="feat/CU-1-x", labels=()):
    return {"number": 7, "head": {"sha": sha, "ref": head}, "base": {"ref": base}, "user": {"login": author},
            "labels": [{"name": l} for l in labels]}


HANDOFF_OK = {
    "schema": "foundation-handoff/v1", "task": "CU-1", "plan": None, "implementer": IMPLEMENTER,
    "summary": "Adds sum() with a test.", "next_action": "independent review",
    "commands": [{"cmd": "./scripts/check-all.sh", "result": "pass"}, {"cmd": "node --test", "result": "pass"}],
}


def body_with(handoff) -> str:
    return f"Adds sum.\n\n```foundation-handoff\n{json.dumps(handoff, indent=2)}\n```\n"


PASSING_TEST = "import test from 'node:test'; import assert from 'node:assert'; test('x', () => assert.equal(1 + 1, 2));\n"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tmpdir()
        self.repo = fresh_repo(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def py(self, *args, env=None):
        return sh(["python3", *args], self.repo, check=False, env=env)

    def assertFails(self, res, text=None):
        self.assertNotEqual(res.returncode, 0, res.stdout)
        if text:
            self.assertIn(text, res.stdout + res.stderr)

    def assertPasses(self, res):
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)


class QualityGates(Base):
    REAL = {"install": "node -e 0", "lint": "node -e 0", "typecheck": "node -e 0", "test": "node --test selftest/sum.test.mjs",
            "build": "node -e 0", "audit": "node -e 0"}

    def gates(self, *args):
        return self.py("scripts/checks/quality_gates.py", *args)

    def test_bootstrap_passes_but_says_so(self):
        project_json(self.repo, "bootstrap")
        res = self.gates()
        self.assertPasses(res)
        self.assertIn("stage=bootstrap", res.stdout)

    def test_development_with_unset_gates_fails(self):
        project_json(self.repo, "development")
        self.assertFails(self.gates(), "required gate has no command")

    def test_missing_mandatory_tests_fail(self):
        project_json(self.repo, "development", dict(self.REAL, test="node -e 0"))  # a runner that "passes" with zero tests
        self.assertFails(self.gates(), "Mandatory tests are missing")

    def test_missing_package_script_fails(self):
        project_json(self.repo, "development", dict(self.REAL, test="npm test --silent"))
        write(self.repo / "package.json", json.dumps({"name": "selftest", "private": True, "scripts": {}}))
        write(self.repo / "selftest/sum.test.mjs", PASSING_TEST)
        self.assertFails(self.gates("--gates", "test"), "test: `npm test --silent` exited")

    def test_placeholder_commands_rejected(self):
        for cmd in ["pnpm run --if-present test", "echo TODO", "true", "npm test || true", "vitest --passWithNoTests"]:
            with self.subTest(cmd):
                project_json(self.repo, "bootstrap", {"test": cmd})
                self.assertFails(self.gates("--gates", "test"), "can pass without checking anything")

    def test_failing_test_fails(self):
        project_json(self.repo, "development", self.REAL)
        write(self.repo / "selftest/sum.test.mjs", "import test from 'node:test'; import assert from 'node:assert'; test('x', () => assert.equal(1, 2));\n")
        self.assertFails(self.gates("--gates", "test"), "exited")

    def test_real_gates_with_tests_pass(self):
        project_json(self.repo, "development", self.REAL)
        write(self.repo / "selftest/sum.test.mjs", PASSING_TEST)
        self.assertPasses(self.gates())


class ReviewGate(Base):
    def gate(self, pr_obj, reviews=(), commits=()):
        fx = self.tmp / "fixture.json"
        fx.write_text(json.dumps({"pr": pr_obj, "reviews": list(reviews), "commits": list(commits)}))
        return self.py("scripts/checks/review_gate.py", "--fixture", str(fx))

    def test_no_review_blocks(self):
        self.assertFails(self.gate(pr()), "no independent review")

    def test_open_p1_blocks(self):
        self.assertFails(self.gate(pr(), [review(SHA1, "request_changes", [finding()])]), "open blocking finding")

    def test_open_p0_blocks_even_with_approve_verdict(self):
        self.assertFails(self.gate(pr(), [review(SHA1, "approve", [finding(sev="P0")])]), "open blocking finding")

    def test_review_of_older_commit_doesnt_count(self):
        self.assertFails(self.gate(pr(SHA2), [review(SHA1)]), "this one hasn't been")

    def test_contract_sha_must_match(self):
        r = review(SHA1)
        r["body"] = r["body"].replace(SHA1, SHA2)
        self.assertFails(self.gate(pr(SHA1), [r]), "review contract is for")

    def test_blocking_risk_cant_be_waived_by_reviewer(self):
        self.assertFails(self.gate(pr(), [review(SHA1, findings=[finding(status="accepted_risk")])]), "only a human override")

    def test_p2_open_does_not_block(self):
        self.assertPasses(self.gate(pr(), [review(SHA1, findings=[finding(sev="P2")])]))

    def test_clean_approval_passes(self):
        self.assertPasses(self.gate(pr(), [review(SHA1, findings=[finding(status="resolved")])]))

    def test_missing_or_invalid_contract_blocks(self):
        self.assertFails(self.gate(pr(), [review(SHA1, body="LGTM")]), "no ```foundation-review block")
        self.assertFails(self.gate(pr(), [review(SHA1, findings=[{"id": "F1", "severity": "critical", "status": "open", "summary": "x"}])]), "invalid")

    def test_changes_requested_state_blocks(self):
        self.assertFails(self.gate(pr(), [review(SHA1, state="CHANGES_REQUESTED")]), "requested changes")

    def test_unknown_reviewer_doesnt_count(self):
        self.assertFails(self.gate(pr(), [review(SHA1, who="random-bot[bot]")]), "no independent review")

    def test_reviewer_who_pushed_code_is_not_independent(self):
        commits = [{"sha": SHA1, "author": {"login": REVIEWER}, "committer": {"login": REVIEWER}}]
        self.assertFails(self.gate(pr(), [review(SHA1)], commits), "must not change the code it reviews")

    def test_reviewer_cannot_review_own_pr(self):
        self.assertFails(self.gate(pr(author=REVIEWER), [review(SHA1)]), "isn't independent")

    def test_docs_exception_needs_reviewer_acceptance(self):
        p = pr(labels=["docs-not-needed"])
        self.assertFails(self.gate(p, [review(SHA1)]), "didn't accept the exception")
        self.assertPasses(self.gate(p, [review(SHA1, extra={"docs_exception": "accepted"})]))

    def test_human_override_needs_reason(self):
        bad = {"user": {"login": CHRIS}, "state": "APPROVED", "commit_id": SHA1, "submitted_at": "2026-11-07T11:00:00Z", "body": "foundation-override: ok"}
        self.assertFails(self.gate(pr(), [review(SHA1, "request_changes", [finding()]), bad]), "needs a reason")
        good = dict(bad, body="foundation-override: known limitation, fixing in CU-2 before release")
        self.assertPasses(self.gate(pr(), [review(SHA1, "request_changes", [finding()]), good]))

    def test_back_merge_from_main_passes(self):
        self.assertPasses(self.gate(pr(head="main", author=CHRIS)))

    def test_unconfigured_gate_fails_closed(self):
        set_json(self.repo / ".foundation/review.json", lambda c: c.update(reviewers=["REPLACE-WITH-REVIEWER-LOGIN"]))
        self.assertFails(self.gate(pr(), [review(SHA1)]), "not configured")


class Handoff(Base):
    def handoff(self, body, author=IMPLEMENTER):
        f = self.tmp / "body.md"
        f.write_text(body)
        return self.py("scripts/checks/check_handoff.py", "--body-file", str(f), "--author", author)

    def test_valid_handoff_passes(self):
        self.assertPasses(self.handoff(body_with(HANDOFF_OK)))

    def test_agent_pr_without_handoff_fails(self):
        self.assertFails(self.handoff("did stuff"), "without a handoff")

    def test_human_pr_without_handoff_only_warns(self):
        self.assertPasses(self.handoff("did stuff", author=CHRIS))

    def test_failing_command_cant_be_handed_off(self):
        h = json.loads(json.dumps(HANDOFF_OK))
        h["commands"][1]["result"] = "fail"
        self.assertFails(self.handoff(body_with(h)), "failing command")

    def test_not_run_needs_reason_and_check_all_required(self):
        h = dict(HANDOFF_OK, commands=[{"cmd": "node --test", "result": "not_run"}])
        res = self.handoff(body_with(h))
        self.assertFails(res, "without a reason")
        self.assertIn("check-all", res.stdout)

    def test_schema_violations_fail(self):
        self.assertFails(self.handoff(body_with(dict(HANDOFF_OK, extra_field=1))), "unexpected property")


class Promotion(Base):
    def promote(self, head):
        return self.py("scripts/checks/promotion_gate.py", "--head-ref", head, "--main-ref", "main")

    def to_development(self):
        project_json(self.repo, "development")
        commit_all(self.repo, "development stage")

    def test_bootstrap_cannot_ship(self):
        project_json(self.repo, "bootstrap")
        commit_all(self.repo)
        self.assertFails(self.promote("staging"), "before shipping")

    def test_feature_branch_cannot_ship(self):
        self.to_development()
        self.assertFails(self.promote("feat/CU-1-x"), "can't merge into main")

    def test_release_and_hotfix_paths(self):
        self.to_development()
        self.assertPasses(self.promote("staging"))
        self.assertPasses(self.promote("hotfix/CU-9-fix"))

    def test_unmerged_hotfix_blocks_next_release(self):
        self.to_development()
        git(self.repo, "checkout", "-q", "main")
        git(self.repo, "merge", "-q", "--no-ff", "staging", "-m", "release 1")
        write(self.repo / "selftest/HOTFIX.txt", "fix\n")
        commit_all(self.repo, "hotfix on main")
        git(self.repo, "checkout", "-q", "staging")
        self.assertFails(self.promote("staging"), "Merge main into staging first")
        git(self.repo, "merge", "-q", "--no-ff", "main", "-m", "back-merge")
        self.assertPasses(self.promote("staging"))


SCHEMA_DOC = "---\nstatus: draft\nlifecycle: living\nlast_reviewed: 2026-11-01\n---\n\n# Schema\n\nTables.\n"


class DocTriggers(Base):
    def setUp(self):
        super().setUp()
        write(self.repo / ".foundation/doc-triggers.txt", "selftest/migrations/** -> selftest/SCHEMA.md\n")
        write(self.repo / "selftest/SCHEMA.md", SCHEMA_DOC)
        commit_all(self.repo, "selftest trigger setup")
        git(self.repo, "checkout", "-q", "-b", "feat/CU-1-x")
        write(self.repo / "selftest/migrations/001_t.sql", "create table t (id uuid primary key);\n")

    def triggers(self, env=None):
        return self.py("scripts/checks/doc_triggers.py", "--base", "staging", env=env)

    def test_missing_doc_update_fails(self):
        commit_all(self.repo)
        self.assertFails(self.triggers(), "selftest/SCHEMA.md must change too")

    def test_date_bump_is_not_a_doc_update(self):
        write(self.repo / "selftest/SCHEMA.md", SCHEMA_DOC.replace("2026-11-01", "2026-11-07"))
        commit_all(self.repo)
        self.assertFails(self.triggers(), "only a date bump")

    def test_meaningful_update_passes(self):
        write(self.repo / "selftest/SCHEMA.md", SCHEMA_DOC + "\n### `t`\n\nPurpose: test table.\n")
        commit_all(self.repo)
        self.assertPasses(self.triggers())

    def test_exception_needs_label_and_reason(self):
        commit_all(self.repo)
        self.assertFails(self.triggers({"PR_LABELS": "docs-not-needed", "PR_BODY": "trust me"}), "without a reason")
        ok = self.triggers({"PR_LABELS": "docs-not-needed", "PR_BODY": "Docs-Not-Needed: migration only adds an internal index, no schema change"})
        self.assertPasses(ok)
        self.assertIn("exception claimed", ok.stdout)


class DocsAndHygiene(Base):
    def test_lifecycle_rules(self):
        write(self.repo / "docs/selftest/STALE.md", "---\nstatus: current\nlifecycle: living\nlast_reviewed: 2020-01-01\n---\n# x\n")
        write(self.repo / "docs/selftest/OLD-RECORD.md", "---\nstatus: current\nlifecycle: record\ndate: 2020-01-01\n---\n# x\n")
        write(self.repo / "docs/selftest/NO-LIFECYCLE.md", "---\nstatus: draft\nlast_reviewed: 2026-11-01\n---\n# x\n")
        out = self.py("scripts/checks/check_docs.py").stdout
        self.assertRegex(out, r"WARN .*docs/selftest/STALE.md: living doc last reviewed")
        self.assertNotIn("OLD-RECORD", out)
        self.assertRegex(out, r"FAIL .*docs/selftest/NO-LIFECYCLE.md: `lifecycle:`")

    def test_broken_link_fails(self):
        write(self.repo / "docs/selftest/LINKS.md", "---\nstatus: current\nlifecycle: record\ndate: 2026-11-07\n---\n[x](nowhere.md)\n")
        self.assertRegex(self.py("scripts/checks/check_docs.py").stdout, r"FAIL .*LINKS.md: broken link")

    def test_conflict_markers_fail(self):
        write(self.repo / "selftest/NOTES.md", "a\n" + "<" * 7 + " ours\nx\n=======\ny\n" + ">" * 7 + " theirs\n")
        self.assertRegex(self.py("scripts/checks/check_hygiene.py").stdout, r"FAIL .*selftest/NOTES.md:2: unresolved merge conflict")
        write(self.repo / "selftest/AGENTS.md.rej", "hunk")
        self.assertIn("rejected update hunk", self.py("scripts/checks/check_hygiene.py").stdout)

    def test_code_drift_caught(self):
        cases = [
            ("src/selftest/pay.ts", "export const k = process.env.SELFTEST_SECRET;\n", "check_env.py", "SELFTEST_SECRET is read"),
            ("src/selftest/todo.ts", "// TODO fix later\n", "check_hygiene.py", "todo.ts:1: TODO without a ticket"),
            ("src/selftest/a.css", ".a { color: #ff0000; }\n", "check_hygiene.py", "raw colour #ff0000"),
            ("tests/selftest/a.test.ts", "it.only('x', () => {})\n", "check_hygiene.py", "focused test"),
        ]
        for path, text, check, msg in cases:
            with self.subTest(path):
                write(self.repo / path, text)
                self.assertIn(msg, self.py(f"scripts/checks/{check}").stdout)
                (self.repo / path).unlink()

    def test_agents_md_stale_reference(self):
        with open(self.repo / "AGENTS.md", "a") as f:
            f.write("\nSee `docs/selftest/GONE.md`.\n")
        self.assertIn("docs/selftest/GONE.md", self.py("scripts/checks/check_agents_md.py").stdout)


class SchemaValidator(unittest.TestCase):
    def test_subset_and_unsupported_keywords(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from _schema import validate
        schema = {"type": "object", "required": ["a"], "additionalProperties": False,
                  "properties": {"a": {"type": "integer", "minimum": 1}, "b": {"enum": ["x"]}}}
        self.assertEqual(validate({"a": 1}, schema), [])
        self.assertTrue(validate({"a": 0}, schema))
        self.assertTrue(validate({"a": True}, schema), "bool is not an integer")
        self.assertTrue(validate({"a": 1, "c": 2}, schema))
        self.assertTrue(validate({"a": 1, "b": "y"}, schema))
        self.assertIn("unsupported", validate({}, {"oneOf": []})[0])


if __name__ == "__main__":
    unittest.main()
