#!/usr/bin/env python3
"""Review gate: a PR into staging can't merge without an independent review of its current head commit that has
no open P0/P1 findings. Part of the project foundation.

Runs in .github/workflows/review-gate.yml with the BASE branch checked out (so the PR can't change this script or
its config) and posts the `review-gate` commit status, which the staging ruleset requires.

  review_gate.py [--event $GITHUB_EVENT_PATH] [--post-status]      in CI (reads reviews/commits via `gh api`)
  review_gate.py --fixture case.json                                tests: {"pr": {...}, "reviews": [...], "commits": [...]}

Rules, in order:
  1. Back-merge PRs (main → staging) pass: main only changes through admin-approved promotion.
  2. Reviewers must be configured (.foundation/review.json); placeholders fail closed.
  3. Independence: the PR author can't be a reviewer, and no reviewer may have authored or committed to the PR.
  4. A human approver can override with an APPROVED review on the head commit containing `foundation-override: <reason>`.
  5. Otherwise the newest review by a configured reviewer *on the head commit* must contain a valid
     ```foundation-review block (.foundation/schemas/review.schema.json) with verdict "approve", head_sha matching,
     no open blocking findings, and no blocking finding marked accepted_risk.
  6. If the PR carries the `docs-not-needed` label, the review must say docs_exception: "accepted".
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import ROOT  # noqa: E402
from _schema import extract_block, load_schema, validate  # noqa: E402

PLACEHOLDER = "REPLACE-WITH"


def gh_json(path: str, paginate: bool = True):
    cmd = ["gh", "api", path] + (["--paginate", "--slurp"] if paginate else [])
    data = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
    return [item for page in data for item in page] if paginate else data


def evaluate(pr: dict, reviews: list, commits: list, cfg: dict, schema: dict) -> tuple[bool, str]:
    head_sha = pr["head"]["sha"]
    short = head_sha[:7]
    base, head_ref = pr["base"]["ref"], pr["head"]["ref"]
    author = (pr.get("user") or {}).get("login", "")
    labels = {l["name"] for l in pr.get("labels", [])}

    if base == "staging" and head_ref == "main":
        return True, "back-merge from main (already promoted and admin-approved)"

    reviewers = [r for r in cfg.get("reviewers", []) if r and PLACEHOLDER not in r]
    if not reviewers:
        return False, "review gate not configured: set reviewers in .foundation/review.json"
    blocking = set(cfg.get("blocking_severities", ["P0", "P1"]))

    if author in reviewers:
        return False, f"{author} opened this PR and is a configured reviewer: review isn't independent"
    for c in commits:
        for who in ("author", "committer"):
            login = (c.get(who) or {}).get("login")
            if login in reviewers:
                return False, f"reviewer {login} {who[:-2]}ed commit {c.get('sha', '')[:7]}: reviewer must not change the code it reviews"

    on_head = [r for r in reviews if r.get("commit_id") == head_sha and r.get("state") not in ("DISMISSED", "PENDING")]
    on_head.sort(key=lambda r: r.get("submitted_at") or "")

    for r in reversed(on_head):
        login = (r.get("user") or {}).get("login")
        if login in cfg.get("human_approvers", []) and login != author and r.get("state") == "APPROVED":
            body = r.get("body") or ""
            if "foundation-override:" in body:
                rest = body.split("foundation-override:", 1)[1].strip()
                reason = rest.splitlines()[0].strip() if rest else ""
                if len(reason) >= 10:
                    return True, f"human override by {login}: {reason[:80]}"
                return False, f"override by {login} needs a reason (foundation-override: <why>, 10+ chars)"

    mine = [r for r in on_head if (r.get("user") or {}).get("login") in reviewers]
    if not mine:
        older = [r for r in reviews if (r.get("user") or {}).get("login") in reviewers]
        why = "earlier commits were reviewed; this one hasn't been" if older else "no review yet"
        return False, f"no independent review of {short} ({why})"

    latest = mine[-1]
    who = latest["user"]["login"]
    if latest.get("state") == "CHANGES_REQUESTED":
        return False, f"{who} requested changes on {short}"

    data, err = extract_block(latest.get("body") or "", "foundation-review")
    if err:
        return False, f"{who}'s review of {short}: {err}"
    errors = validate(data, schema)
    if errors:
        return False, f"{who}'s review contract is invalid: {errors[0]}"
    if not head_sha.startswith(data["head_sha"]):
        return False, f"review contract is for {data['head_sha'][:7]}, but the PR head is {short}"

    open_blocking = [f for f in data["findings"] if f["severity"] in blocking and f["status"] == "open"]
    if open_blocking:
        ids = ", ".join(f"{f['severity']} {f['id']}" for f in open_blocking[:3])
        return False, f"{len(open_blocking)} open blocking finding(s): {ids}"
    waived = [f for f in data["findings"] if f["severity"] in blocking and f["status"] == "accepted_risk"]
    if waived:
        return False, f"{waived[0]['severity']} {waived[0]['id']} marked accepted_risk: only a human override can accept a blocking risk"
    if data["verdict"] != "approve":
        return False, f"{who}'s verdict on {short} is {data['verdict']}"
    if "docs-not-needed" in labels and data.get("docs_exception") != "accepted":
        return False, "PR claims docs-not-needed but the reviewer didn't accept the exception (docs_exception: accepted)"

    return True, f"approved by {who} at {short}"


def main() -> int:
    args = sys.argv[1:]
    cfg = json.loads((ROOT / ".foundation" / "review.json").read_text(encoding="utf-8"))
    schema = load_schema(ROOT, "review")

    if "--fixture" in args:
        fx = json.loads(Path(args[args.index("--fixture") + 1]).read_text())
        pr, reviews, commits = fx["pr"], fx.get("reviews", []), fx.get("commits", [])
    else:
        event_path = args[args.index("--event") + 1] if "--event" in args else os.environ["GITHUB_EVENT_PATH"]
        pr_event = json.loads(Path(event_path).read_text())["pull_request"]
        repo = os.environ["GITHUB_REPOSITORY"]
        n = pr_event["number"]
        pr = gh_json(f"repos/{repo}/pulls/{n}", paginate=False)
        reviews = gh_json(f"repos/{repo}/pulls/{n}/reviews")
        commits = gh_json(f"repos/{repo}/pulls/{n}/commits")

    ok, message = evaluate(pr, reviews, commits, cfg, schema)
    print(f"{'PASS' if ok else 'FAIL'}  [review-gate] {message}")

    if "--post-status" in args:
        repo = os.environ["GITHUB_REPOSITORY"]
        run_url = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
        subprocess.run(
            ["gh", "api", "-X", "POST", f"repos/{repo}/statuses/{pr['head']['sha']}",
             "-f", f"state={'success' if ok else 'failure'}", "-f", "context=review-gate",
             "-f", f"description={message[:139]}", "-f", f"target_url={run_url}"],
            check=True, capture_output=True,
        )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
