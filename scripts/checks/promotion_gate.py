#!/usr/bin/env python3
"""Promotion gate for PRs into main (production). Part of the project foundation.

  1. Only `staging` (a release) or `hotfix/*` may be merged into main.
  2. The project must be in stage "development": a bootstrap project can't ship.
  3. A release from staging must contain everything already on main, so a hotfix can't be silently undone
     by the next release. (After a hotfix, merge main back into staging with a merge commit.)

Usage: promotion_gate.py --head-ref <ref> [--base-ref main] [--main-ref origin/main]
       (CI passes the PR's refs; needs a full clone: fetch-depth 0)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import ROOT, Report, run_git  # noqa: E402


def arg(args: list[str], name: str, default: str | None = None) -> str | None:
    return args[args.index(name) + 1] if name in args else default


def main() -> int:
    r = Report("promotion")
    args = sys.argv[1:]
    head = arg(args, "--head-ref")
    base = arg(args, "--base-ref", "main")
    main_ref = arg(args, "--main-ref", "origin/main")

    if base != "main":
        print(f"ok    [promotion] base is {base}, not main: nothing to check")
        return 0
    if not head:
        r.fail("--head-ref is required")
        return r.finish()

    if not (head == "staging" or head.startswith("hotfix/")):
        r.fail(f"'{head}' can't merge into main. Only staging (release) or hotfix/* can")

    stage = json.loads((ROOT / ".foundation" / "project.json").read_text()).get("stage")
    if stage != "development":
        r.fail(f"stage is '{stage}'. Set the real gate commands and stage 'development' in .foundation/project.json before shipping")

    if head == "staging":
        if run_git("rev-parse", "--verify", "--quiet", main_ref) is None:
            r.warn(f"{main_ref} not found; can't confirm staging contains main (first release?)")
        elif run_git("merge-base", "--is-ancestor", main_ref, "HEAD") is None:
            r.fail("main has commits staging doesn't (an un-merged hotfix?). Merge main into staging first, with a merge commit")

    return r.finish()


if __name__ == "__main__":
    sys.exit(main())
