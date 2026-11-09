#!/usr/bin/env python3
"""Docs declare a lifecycle, living docs don't go silently stale, and internal links resolve.
Part of the project foundation.

Frontmatter on every doc under docs/ (READMEs, `_templates`, foundation docs and docs/archive/ excepted):
  status:     draft | current | superseded            (ADRs/plans use their own statuses)
  lifecycle:  living | reference | record
                living     describes the system as it is now; reviewed every 90 days (or review_every_days)
                reference  changes rarely (vision, glossary, policies); reviewed every 365 days
                record     a point-in-time record (ADRs, plans, drill logs); never goes stale
  last_reviewed: YYYY-MM-DD   (living and reference)     date: YYYY-MM-DD   (records)
ADRs (docs/decisions/) and plans (docs/plans/) are records by default.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).parent))
from _lib import ROOT, Report, config, frontmatter, read, repo_files, strip_code  # noqa: E402

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
EXEMPT_NAMES = {"README.md", "0000-template.md"}
LIFECYCLES = {"living": None, "reference": 365, "record": 0}
DONE_STATUSES = {"superseded", "done", "rejected"}


def needs_frontmatter(path: str, text: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return (
        path.startswith("docs/")
        and not path.startswith("docs/archive/")
        and name not in EXEMPT_NAMES
        and not name.startswith("_")
        and "Part of the project foundation" not in text[:400]
    )


def check_frontmatter(path: str, text: str, r: Report, cfg: dict, today: date) -> None:
    fm = frontmatter(text)
    if not fm or "status" not in fm:
        r.fail(f"{path}: missing frontmatter with `status:` and `lifecycle:` (see docs/README.md → Conventions)")
        return
    is_record_dir = path.startswith(("docs/decisions/", "docs/plans/"))
    lifecycle = fm.get("lifecycle") or ("record" if is_record_dir else None)
    if lifecycle not in LIFECYCLES:
        r.fail(f"{path}: `lifecycle:` must be living, reference or record (got {lifecycle!r})")
        return
    if fm["status"].split()[0] in DONE_STATUSES or lifecycle == "record":
        if lifecycle == "record" and not (fm.get("date") or fm.get("last_reviewed")):
            r.fail(f"{path}: records need a `date:`")
        return

    stamp = fm.get("last_reviewed")
    if not stamp:
        r.fail(f"{path}: {lifecycle} docs need `last_reviewed:`")
        return
    try:
        age = (today - date.fromisoformat(stamp)).days
    except ValueError:
        r.fail(f"{path}: last_reviewed `{stamp}` isn't a YYYY-MM-DD date")
        return
    limit = int(fm.get("review_every_days") or (LIFECYCLES[lifecycle] or cfg["stale_doc_days"]))
    if age > limit:
        r.warn(f"{path}: {lifecycle} doc last reviewed {age} days ago (limit {limit}); check it against reality and bump last_reviewed")


def main() -> int:
    r = Report("docs")
    cfg = config()
    today = date.today()

    for path in [f for f in repo_files() if f.endswith(".md")]:
        text = read(path)
        if needs_frontmatter(path, text):
            check_frontmatter(path, text, r, cfg, today)

        for target in LINK.findall(strip_code(text)):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#") or "{{" in target or "<" in target:
                continue
            clean = unquote(target.split("#", 1)[0])
            if not clean:
                continue
            base = ROOT if clean.startswith("/") else (ROOT / path).parent
            if not (base / clean.lstrip("/")).exists():
                r.fail(f"{path}: broken link → {target}")

    return r.finish()


if __name__ == "__main__":
    sys.exit(main())
