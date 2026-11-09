#!/usr/bin/env python3
"""Code hygiene: TODOs and skipped tests carry a ticket, no focused tests, no raw hex colours in UI code,
product name spelled right, no unresolved merge conflicts (e.g. from a merge).
Put `foundation-ignore` on a line to exempt it. Part of the project foundation."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import IGNORE_MARK, ROOT, Report, code_files, config, read, repo_files  # noqa: E402

CODE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".vue", ".svelte", ".astro", ".go", ".rs", ".sql"}
UI_EXTS = {".css", ".scss", ".sass", ".less", ".tsx", ".jsx", ".vue", ".svelte", ".astro", ".html"}
TODO = re.compile(r"\b(TODO|FIXME|HACK)\b(\([^)]*\))?")
FOCUS = re.compile(r"\b(?:it|test|describe)\.only\(|\bf(?:it|describe)\(")
SKIP = re.compile(r"\b(?:it|test|describe)\.skip\(|\bx(?:it|describe|test)\(|@pytest\.mark\.skip|\bt\.skip\(")
HEX = re.compile(r"(?<![\w&#/])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")
ANCHOR_ATTR = re.compile(r"(?:href|to|xlink:href)=\s*[\"']$|url\($")


def is_test(path: str) -> bool:
    return bool(re.search(r"(^|/)(tests?|__tests__|spec)/|\.(test|spec)\.\w+$|(^|/)test_\w+\.py$", path))


BINARY = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".woff", ".woff2", ".ttf", ".zip", ".gz", ".webp"}
CONFLICT = re.compile(r"^(<{7}|>{7})( |$)")


def check_conflicts(r: Report) -> None:
    for f in repo_files():
        if f.endswith(".rej"):
            r.fail(f"{f}: rejected update hunk left behind; apply it by hand and delete the file")
            continue
        if Path(f).suffix.lower() in BINARY:
            continue
        for n, line in enumerate(read(f).splitlines(), 1):
            if CONFLICT.match(line):
                r.fail(f"{f}:{n}: unresolved merge conflict marker")
                break


PLACEHOLDER = re.compile(r"__(PROJECT_NAME|PROJECT_SLUG|DESCRIPTION|OWNER|GITHUB_OWNER|DATE)__")


def check_placeholders(r: Report) -> None:
    if (ROOT / ".foundation" / "IS_TEMPLATE").exists():
        return
    for f in repo_files():
        if f.startswith("scripts/") or Path(f).suffix.lower() in BINARY:
            continue
        m = PLACEHOLDER.search(read(f))
        if m:
            r.fail(f"{f}: placeholder {m.group(0)} left in. Run scripts/init.py, or fill it in by hand")


def main() -> int:
    r = Report("hygiene")
    cfg = config()
    check_conflicts(r)
    check_placeholders(r)
    ticket = re.compile(cfg["ticket_pattern"])

    lint_path = ROOT / "brand" / "copy-lint.json"
    lint = json.loads(lint_path.read_text()) if lint_path.exists() else {}
    wrong = [w for w in lint.get("wrong_spellings", []) if w]
    banned = [b for b in lint.get("banned_phrases", []) if b]

    files = sorted(set(code_files(CODE_EXTS | UI_EXTS, cfg)))
    for f in files:
        suffix = Path(f).suffix
        lines = read(f).splitlines()
        for n, line in enumerate(lines, 1):
            if IGNORE_MARK in line:
                continue
            loc = f"{f}:{n}"

            if suffix in CODE_EXTS:
                for m in TODO.finditer(line):
                    if not m.group(2) or not ticket.search(m.group(2)):
                        r.fail(f"{loc}: {m.group(1)} without a ticket. Write {m.group(1)}(<ticket-id>): …")

            if is_test(f):
                if FOCUS.search(line):
                    r.fail(f"{loc}: focused test (.only) left in")
                if SKIP.search(line):
                    prev = lines[n - 2] if n > 1 else ""
                    if not ticket.search(line) and not ticket.search(prev):
                        r.fail(f"{loc}: skipped test without a ticket on this or the previous line")

            if cfg.get("raw_hex_check") and suffix in UI_EXTS:
                for m in HEX.finditer(line):
                    if ANCHOR_ATTR.search(line[: m.start()]):
                        continue
                    r.fail(f"{loc}: raw colour {m.group(0)}; use a token from brand/tokens.json")

            if suffix in UI_EXTS:
                for w in wrong:
                    if re.search(rf"\b{re.escape(w)}\b", line):
                        r.fail(f"{loc}: '{w}' — the product is written '{lint.get('product_name', '?')}'")
                for b in banned:
                    if re.search(rf"\b{re.escape(b)}\b", line, flags=re.I):
                        r.warn(f"{loc}: '{b}' is on the banned-phrases list (docs/product/VOICE.md)")

    return r.finish()


if __name__ == "__main__":
    sys.exit(main())
