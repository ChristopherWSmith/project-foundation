#!/usr/bin/env python3
"""If a PR changes X, it must also change the doc that describes X (rules in .foundation/doc-triggers.txt).
Also: an edited prompt in prompts/ must bump its `version:`. Part of the project foundation.

The required change must be meaningful: bumping `last_reviewed`, whitespace or blank lines alone doesn't count.

Exception: label the PR `docs-not-needed` AND put a line `Docs-Not-Needed: <reason, 20+ chars>` in the PR
description (env PR_LABELS / PR_BODY in CI). The failures then become warnings, and the review gate requires
the reviewer to accept the exception (docs_exception: "accepted").

Usage: doc_triggers.py [--base <git ref>]   (default: $GITHUB_BASE_REF, then staging, then main)
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import ROOT, Report, path_matches, run_git  # noqa: E402

CONFIG = ROOT / ".foundation" / "doc-triggers.txt"
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", re.M)


def slug(heading: str) -> str:
    s = re.sub(r"[^\w\s-]", "", heading.strip().lower())
    return re.sub(r"\s+", "-", s)


def find_base(arg: str | None) -> str | None:
    candidates = [arg] if arg else []
    if os.environ.get("GITHUB_BASE_REF"):
        candidates.append(f"origin/{os.environ['GITHUB_BASE_REF']}")
    candidates += ["origin/staging", "staging", "origin/main", "main"]
    for ref in candidates:
        if ref and run_git("rev-parse", "--verify", "--quiet", ref) is not None:
            return ref
    return None


def sections_at(text: str, line_numbers: set[int]) -> set[str]:
    found, current = set(), ""
    for n, line in enumerate(text.splitlines(), 1):
        m = re.match(r"^#{1,6}\s+(.*)", line)
        if m:
            current = slug(m.group(1))
        if n in line_numbers:
            found.add(current)
    return found


def touched_sections(base: str, path: str) -> set[str]:
    diff = run_git("diff", "-U0", f"{base}...HEAD", "--", path) or ""
    old_lines, new_lines = set(), set()
    for a, b, c, d in HUNK.findall(diff):
        a, c = int(a), int(c)
        b = 1 if b == "" else int(b)
        d = 1 if d == "" else int(d)
        old_lines.update(range(a, a + max(b, 1)))
        new_lines.update(range(c, c + max(d, 1)))
    result = set()
    if (ROOT / path).exists():
        result |= sections_at((ROOT / path).read_text(encoding="utf-8", errors="replace"), new_lines)
    old = run_git("show", f"{base}:{path}")
    if old:
        result |= sections_at(old, old_lines)
    return result


TRIVIAL = re.compile(r"^\s*$|^\s*(last_reviewed|date|status|review_every_days)\s*:|^\s*---\s*$")


def meaningful_change(base: str, path: str) -> bool:
    diff = run_git("diff", "-U0", f"{base}...HEAD", "--", path)
    if diff is None:
        return False
    for line in diff.splitlines():
        if line.startswith(("+++", "---", "@@", "diff ", "index ", "new file", "deleted file")):
            continue
        if line[:1] in "+-" and not TRIVIAL.match(line[1:]):
            return True
    return False


def exception_reason() -> tuple[bool, str | None]:
    labels = {l.strip() for l in os.environ.get("PR_LABELS", "").split(",") if l.strip()}
    if "docs-not-needed" not in labels:
        return False, None
    m = re.search(r"^\s*Docs-Not-Needed:\s*(.+)$", os.environ.get("PR_BODY", ""), flags=re.M | re.I)
    return True, (m.group(1).strip() if m and len(m.group(1).strip()) >= 20 else None)


def load_rules() -> list[tuple[str, str | None, str]]:
    rules = []
    if not CONFIG.exists():
        return rules
    for raw in CONFIG.read_text().splitlines():
        line = raw.split("  #", 1)[0].strip()
        if not line or line.startswith("#") or "->" not in line:
            continue
        left, right = (s.strip() for s in line.split("->", 1))
        pattern, _, sect = left.partition("#")
        rules.append((pattern, sect or None, right))
    return rules


def main() -> int:
    r = Report("doc-triggers")
    args = sys.argv[1:]
    base = find_base(args[args.index("--base") + 1] if "--base" in args else None)
    if not base:
        r.warn("no base branch found (staging/main); skipping")
        return r.finish()

    out = run_git("diff", "--name-status", f"{base}...HEAD")
    if out is None:
        r.warn(f"couldn't diff against {base}; skipping")
        return r.finish()
    status = {}
    for line in out.splitlines():
        parts = line.split("\t")
        status[parts[-1]] = parts[0][0]
    changed = set(status)
    if not changed:
        return r.finish()

    problems = []
    for pattern, sect, required in load_rules():
        hits = [f for f in changed if path_matches(f, pattern) and not path_matches(f, required)]
        if sect:
            hits = [f for f in hits if f.endswith(".md") and sect in touched_sections(base, f)]
        if not hits:
            continue
        what = f"{hits[0]} (section #{sect})" if sect else hits[0]
        more = f" and {len(hits) - 1} more" if len(hits) > 1 else ""
        touched = [f for f in changed if path_matches(f, required)]
        if not touched:
            problems.append(f"{what}{more} changed, so {required} must change too")
        elif not any(status[f] == "D" or meaningful_change(base, f) for f in touched):
            problems.append(f"{what}{more} changed, but the change to {required} is only a date bump or whitespace")

    if problems:
        claimed, reason = exception_reason()
        if claimed and reason:
            for p in problems:
                r.warn(f"{p} — exception claimed: \"{reason[:100]}\" (the reviewer must accept it)")
        else:
            for p in problems:
                r.fail(p)
            if claimed:
                r.fail("docs-not-needed label without a reason: add `Docs-Not-Needed: <why, 20+ chars>` to the PR description")
            else:
                r.warn("if no doc change is genuinely needed: label the PR docs-not-needed and add `Docs-Not-Needed: <why>` to the description")

    for f in sorted(changed):
        if f.startswith("prompts/") and f.endswith(".md") and not f.endswith("README.md") and status[f] == "M":
            diff = run_git("diff", "-U0", f"{base}...HEAD", "--", f) or ""
            if not re.search(r"^\+version:", diff, flags=re.M):
                r.fail(f"{f} changed but its `version:` wasn't bumped (and the evals should be re-run)")

    return r.finish()


if __name__ == "__main__":
    sys.exit(main())
