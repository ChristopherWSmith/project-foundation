#!/usr/bin/env python3
"""The PR description carries a valid ```foundation-handoff block (.foundation/schemas/handoff.schema.json),
and the handoff is honest: no failing commands handed off, every "not_run" explained, the foundation checks listed.
Part of the project foundation.

Required for PRs opened by bots / configured implementers (review.json → require_handoff_from_bots, implementers).
Reads PR_BODY and PR_AUTHOR from the environment (set by the workflow), or --body-file / --author for local use.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import ROOT, Report  # noqa: E402
from _schema import extract_block, load_schema, validate  # noqa: E402


def main() -> int:
    r = Report("handoff")
    args = sys.argv[1:]
    body = Path(args[args.index("--body-file") + 1]).read_text() if "--body-file" in args else os.environ.get("PR_BODY", "")
    author = args[args.index("--author") + 1] if "--author" in args else os.environ.get("PR_AUTHOR", "")

    cfg_path = ROOT / ".foundation" / "review.json"
    cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    is_agent = author in cfg.get("implementers", []) or (cfg.get("require_handoff_from_bots", True) and author.endswith("[bot]"))

    data, err = extract_block(body, "foundation-handoff")
    if err:
        if is_agent:
            r.fail(f"agent PR ({author}) without a handoff: {err}. Use the PR template")
        else:
            r.warn(f"no handoff block ({author or 'unknown author'}); required only for agent PRs")
        return r.finish()

    for e in validate(data, load_schema(ROOT, "handoff")):
        r.fail(f"handoff invalid: {e}")
    if r.fails:
        return r.finish()

    for c in data["commands"]:
        if c["result"] == "fail":
            r.fail(f"handed off with a failing command: `{c['cmd']}`. Fix it, or don't hand off yet")
        if c["result"] == "not_run" and len(c.get("note", "").strip()) < 5:
            r.fail(f"`{c['cmd']}` marked not_run without a reason in `note`")
    if not any("check-all" in c["cmd"] for c in data["commands"]):
        r.fail("handoff doesn't list ./scripts/check-all.sh")

    return r.finish()


if __name__ == "__main__":
    sys.exit(main())
