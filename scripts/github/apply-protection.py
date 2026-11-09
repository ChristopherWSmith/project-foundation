#!/usr/bin/env python3
"""Apply the portfolio's branch, merge and environment protection to a repo. Idempotent: run it again any time.

  apply-protection.py <owner/repo> [--with <check>]... [--dry-run]
  e.g. apply-protection.py chris/aventiel --with supabase_drift

Does:
  1. Repo settings: default branch = staging, auto-merge allowed, merged branches deleted, squash + merge commits
     allowed (rebase off).
  2. The five rulesets in .github/rulesets/ (created or updated by name). --with adds required checks to the baseline.
  3. Environments: `staging` (deployable only from staging) and `production` (only from main). Put deploy
     secrets in these, never in repo-level secrets.

Run from the repo root. Needs: gh authenticated as an admin of the repo (your account, never an agent's), python3.
Then run scripts/github/verify-protection.py to confirm the live state.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gh import GhError, gh  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RULESETS = ROOT / ".github" / "rulesets"
ENVIRONMENTS = {"staging": "staging", "production": "main"}
REPO_SETTINGS = {
    "default_branch": "staging",
    "allow_auto_merge": True,
    "delete_branch_on_merge": True,
    "allow_squash_merge": True,
    "allow_merge_commit": True,
    "allow_rebase_merge": False,
}


def load_rulesets(extra: list[str]) -> list[dict]:
    out = []
    for path in sorted(RULESETS.glob("*.json")):
        rs = json.loads(path.read_text())
        rs.pop("$comment", None)
        if path.name.startswith("10-") and extra:
            for rule in rs["rules"]:
                if rule["type"] == "required_status_checks":
                    have = {c["context"] for c in rule["parameters"]["required_status_checks"]}
                    rule["parameters"]["required_status_checks"] += [
                        {"context": c, "integration_id": 15368} for c in extra if c not in have
                    ]
        out.append(rs)
    return out


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        print(__doc__)
        return 2
    repo, dry = args[0], "--dry-run" in args
    extra = [args[i + 1] for i, a in enumerate(args) if a == "--with"]
    rulesets = load_rulesets(extra)

    if dry:
        print(f"Would PATCH repos/{repo}: {json.dumps(REPO_SETTINGS)}")
        for rs in rulesets:
            print(f"Would upsert ruleset '{rs['name']}':\n{json.dumps(rs, indent=2)}")
        for env, branch in ENVIRONMENTS.items():
            print(f"Would create environment '{env}' deployable only from '{branch}'")
        return 0

    try:
        gh(f"repos/{repo}/branches/staging")
    except GhError:
        print(f"{repo} has no staging branch. Push it first: git push origin staging", file=sys.stderr)
        return 1

    gh("-X", "PATCH", f"repos/{repo}", body=REPO_SETTINGS)
    print("✓ repo settings: default branch staging, auto-merge on, squash + merge commits, delete merged branches")

    existing = {r["name"]: r["id"] for r in (gh(f"repos/{repo}/rulesets", paginate=True) or [])}
    for rs in rulesets:
        if rs["name"] in existing:
            gh("-X", "PUT", f"repos/{repo}/rulesets/{existing[rs['name']]}", body=rs)
            print(f"✓ updated ruleset '{rs['name']}'")
        else:
            gh("-X", "POST", f"repos/{repo}/rulesets", body=rs)
            print(f"✓ created ruleset '{rs['name']}'")

    for env, branch in ENVIRONMENTS.items():
        gh("-X", "PUT", f"repos/{repo}/environments/{env}",
           body={"deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": True}})
        policies = gh(f"repos/{repo}/environments/{env}/deployment-branch-policies") or {}
        names = {p["name"] for p in policies.get("branch_policies", [])}
        for stray in names - {branch}:
            pid = next(p["id"] for p in policies["branch_policies"] if p["name"] == stray)
            gh("-X", "DELETE", f"repos/{repo}/environments/{env}/deployment-branch-policies/{pid}")
        if branch not in names:
            gh("-X", "POST", f"repos/{repo}/environments/{env}/deployment-branch-policies",
               body={"name": branch, "type": "branch"})
        print(f"✓ environment '{env}': deployable only from {branch}")

    print(f"\nDone. Confirm with: scripts/github/verify-protection.py {repo}{''.join(f' --with {c}' for c in extra)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
