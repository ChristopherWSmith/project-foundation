#!/usr/bin/env python3
"""Turn a copy of the project foundation into a named product repo. Runs once.

  python3 scripts/init.py "Product Name" --github-owner <username> [--reviewer <bot-login>[,<login>]]
                          [--description "One sentence"] [--owner Chris] [--slug product-name]

Fills every __PLACEHOLDER__, builds brand/dist/tokens.css, removes the template markers, and (only if there's no
git repo yet) creates git with `main` (production) and `staging` (integration, checked out).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = ROOT / ".foundation" / "IS_TEMPLATE"
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__"}
SKIP_FILES = {"scripts/init.py"}
BINARY = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".woff", ".woff2", ".ttf", ".zip", ".webp"}
NOTE = re.compile(r"<!-- foundation:template-note -->.*?<!-- /foundation:template-note -->\n", re.S)


def git(*args: str) -> None:
    subprocess.run(["git", *args], cwd=ROOT, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name")
    ap.add_argument("--github-owner", required=True, help="your GitHub username (CODEOWNERS, human approver)")
    ap.add_argument("--reviewer", default="", help="independent reviewer login(s), comma-separated")
    ap.add_argument("--description", default="TODO: one-sentence description")
    ap.add_argument("--owner", default="Chris")
    ap.add_argument("--slug")
    a = ap.parse_args()

    if not MARKER.exists():
        print("Already initialised (.foundation/IS_TEMPLATE is gone). Edit the files directly.", file=sys.stderr)
        return 1

    reviewers = [r.strip() for r in a.reviewer.split(",") if r.strip()] or ["REPLACE-WITH-REVIEWER-LOGIN"]
    values = {
        "__PROJECT_NAME__": a.name.strip(),
        "__PROJECT_SLUG__": a.slug or re.sub(r"[^a-z0-9]+", "-", a.name.strip().lower()).strip("-"),
        "__DESCRIPTION__": a.description,
        "__OWNER__": a.owner,
        "__GITHUB_OWNER__": a.github_owner.lstrip("@"),
        "__DATE__": date.today().isoformat(),
    }

    changed = 0
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT).as_posix()
        if not path.is_file() or set(path.parts) & SKIP_DIRS or rel in SKIP_FILES or path.suffix.lower() in BINARY:
            continue
        if rel.startswith("scripts/"):  # tooling: some scripts look for these tokens on purpose
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        new = NOTE.sub("", text)
        for token, value in values.items():
            new = new.replace(token, value)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1

    review = ROOT / ".foundation" / "review.json"
    cfg = json.loads(review.read_text())
    cfg["reviewers"] = reviewers
    cfg["human_approvers"] = [values["__GITHUB_OWNER__"]]
    review.write_text(json.dumps(cfg, indent=2) + "\n")

    subprocess.run([sys.executable, str(ROOT / "scripts" / "brand" / "build_tokens.py")], cwd=ROOT, check=True)
    MARKER.unlink()
    print(f"Filled placeholders in {changed} files.")

    if not (ROOT / ".git").exists():
        git("init", "-q", "-b", "main")
        git("add", "-A")
        git("commit", "-qm", f"chore: start {values['__PROJECT_NAME__']} from the project foundation")
        git("branch", "staging")
        git("checkout", "-q", "staging")
        print("Git: main (production) + staging (integration, checked out).")
    else:
        print("Existing git repo: nothing committed. Review with `git status` and `git diff`.")

    print(f"""
Next:
  1. Fill in AGENTS.md (stack, golden paths, approved libraries) and docs/product/VISION.md
  2. Delete what this product will never need (see .foundation/README.md)
  3. Push main and staging, then:
       python3 scripts/github/apply-protection.py <owner>/{values['__PROJECT_SLUG__']} --with supabase_drift
       python3 scripts/github/verify-protection.py <owner>/{values['__PROJECT_SLUG__']} --with supabase_drift
  4. When real code lands: set the gates in .foundation/project.json and switch stage to "development"
""" + ("" if a.reviewer else "  ! No --reviewer given: PRs into staging stay blocked until .foundation/review.json has the reviewer login.\n"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
