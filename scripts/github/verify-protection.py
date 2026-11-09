#!/usr/bin/env python3
"""Check a repo's LIVE protection against the portfolio standard. Read-only. Exit 1 on any failure.

  verify-protection.py <owner/repo> [--with <check>]... [--agents .foundation/agents.json]

Checks: repo settings; each ruleset in .github/rulesets/ exists, is active, and has the same rules, required checks
(pinned to GitHub Actions) and bypass actors; environments are branch-restricted; CODEOWNERS and the review gate
config are filled in on staging; agent apps have no permission that would let them bypass the gates.
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gh import GhError, gh  # noqa: E402

apply = __import__("apply-protection")


def file_on(repo: str, path: str, ref: str = "staging") -> str | None:
    try:
        data = gh(f"repos/{repo}/contents/{path}?ref={ref}")
        return base64.b64decode(data["content"]).decode("utf-8", "replace")
    except GhError:
        return None


def checks_of(rules: list[dict]) -> set[tuple]:
    found = set()
    for r in rules:
        if r["type"] == "required_status_checks":
            for c in r["parameters"]["required_status_checks"]:
                found.add((c["context"], c.get("integration_id")))
    return found


def bypass_of(rs: dict) -> set[tuple]:
    return {(b["actor_id"], b["actor_type"], b["bypass_mode"]) for b in rs.get("bypass_actors") or []}


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        print(__doc__)
        return 2
    repo = args[0]
    extra = [args[i + 1] for i, a in enumerate(args) if a == "--with"]
    agents_file = Path(args[args.index("--agents") + 1]) if "--agents" in args else apply.ROOT / ".foundation" / "agents.json"
    results: list[tuple[bool, str]] = []

    def check(ok: bool, what: str) -> None:
        results.append((ok, what))

    info = gh(f"repos/{repo}")
    for key, want in apply.REPO_SETTINGS.items():
        check(info.get(key) == want, f"repo setting {key} = {want!r} (is {info.get(key)!r})")

    live = {r["name"]: r for r in (gh(f"repos/{repo}/rulesets", paginate=True) or [])}
    for want in apply.load_rulesets(extra):
        name = want["name"]
        if name not in live:
            check(False, f"ruleset '{name}' exists")
            continue
        have = gh(f"repos/{repo}/rulesets/{live[name]['id']}")
        check(have.get("enforcement") == "active", f"ruleset '{name}' is active")
        check({r["type"] for r in have["rules"]} == {r["type"] for r in want["rules"]}, f"ruleset '{name}' has rules {sorted(r['type'] for r in want['rules'])}")
        missing = checks_of(want["rules"]) - checks_of(have["rules"])
        check(not missing, f"ruleset '{name}' requires checks {sorted(c for c, _ in checks_of(want['rules']))} from GitHub Actions" + (f" (missing {sorted(missing)})" if missing else ""))
        check(bypass_of(have) == bypass_of(want), f"ruleset '{name}' bypass = {sorted(bypass_of(want)) or 'nobody'} (is {sorted(bypass_of(have)) or 'nobody'})")
        for r in want["rules"]:
            if r["type"] == "pull_request":
                live_pr = next((x for x in have["rules"] if x["type"] == "pull_request"), {"parameters": {}})
                for k in ("require_code_owner_review", "allowed_merge_methods", "required_review_thread_resolution"):
                    w, h = r["parameters"].get(k), live_pr["parameters"].get(k)
                    check((sorted(w) == sorted(h or [])) if isinstance(w, list) else w == h, f"ruleset '{name}' pull_request.{k} = {w}")

    for env, branch in apply.ENVIRONMENTS.items():
        try:
            pol = gh(f"repos/{repo}/environments/{env}/deployment-branch-policies") or {}
            names = sorted(p["name"] for p in pol.get("branch_policies", []))
            check(names == [branch], f"environment '{env}' deployable only from {branch} (is {names})")
        except GhError:
            check(False, f"environment '{env}' exists")

    owners = file_on(repo, ".github/CODEOWNERS")
    check(bool(owners) and any(l.strip() and not l.lstrip().startswith("#") for l in owners.splitlines()) and "@OWNER" not in owners and "__GITHUB_OWNER__" not in owners,
          "CODEOWNERS on staging is filled in (not just comments)")
    review = file_on(repo, ".foundation/review.json")
    try:
        reviewers = json.loads(review or "{}").get("reviewers", [])
    except json.JSONDecodeError:
        reviewers = []
    check(bool(reviewers) and not any("REPLACE" in r for r in reviewers), f"review gate reviewers configured ({reviewers})")

    agents = json.loads(agents_file.read_text()).get("agents", []) if agents_file.exists() else []
    slugs = [a["app_slug"] for a in agents]
    if any("REPLACE" in s for s in slugs):
        check(False, f"agent app slugs filled in ({agents_file})")
    else:
        check(len(set(slugs)) == len(slugs), "implementer and reviewer are different apps")
        data = gh("user/installations?per_page=100") or {}
        installs = {i["app_slug"]: i for i in data.get("installations", [])}
        for a in agents:
            inst = installs.get(a["app_slug"])
            if not inst:
                check(False, f"{a['role']} app '{a['app_slug']}' is installed")
                continue
            perms = inst.get("permissions", {})
            for rule in a.get("must_not", []):
                perm, _, level = rule.partition(":")
                bad = perm in perms and (not level or perms[perm] == level)
                check(not bad, f"{a['role']} app '{a['app_slug']}' has no {rule} permission (has {perms.get(perm, 'none')})")

    failed = [w for ok, w in results if not ok]
    for ok, what in results:
        print(f"{'PASS' if ok else 'FAIL'}  {what}")
    print(f"\n{len(results) - len(failed)}/{len(results)} passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
