#!/usr/bin/env python3
"""Generate brand/dist/tokens.css from brand/tokens.json. Part of the project foundation.

  build_tokens.py              write :root { --color-primary: … }
  build_tokens.py --tailwind   write a Tailwind v4 @theme block instead (utilities like bg-primary come for free)
  build_tokens.py --check      fail if the committed CSS doesn't match tokens.json (used in CI)

Format choice is remembered in the file's first line, so --check compares like with like.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "brand" / "tokens.json"
OUT = ROOT / "brand" / "dist" / "tokens.css"


def flatten(node: dict, prefix: str = "") -> list[tuple[str, str]]:
    items = []
    for key, value in node.items():
        if key.startswith("$"):
            continue
        name = f"{prefix}-{key}" if prefix else key
        if isinstance(value, dict):
            items += flatten(value, name)
        else:
            items.append((name, str(value)))
    return items


def render(tailwind: bool) -> str:
    tokens = flatten(json.loads(SRC.read_text(encoding="utf-8")))
    head = f"/* generated from brand/tokens.json by scripts/brand/build_tokens.py{' --tailwind' if tailwind else ''}; don't edit */"
    body = "\n".join(f"  --{name}: {value};" for name, value in tokens)
    return f"{head}\n{'@theme' if tailwind else ':root'} {{\n{body}\n}}\n"


def main() -> int:
    args = sys.argv[1:]
    if "--check" in args:
        if not OUT.exists():
            print("FAIL  [brand] brand/dist/tokens.css is missing. Run: python3 scripts/brand/build_tokens.py")
            return 1
        tailwind = "--tailwind" in OUT.read_text(encoding="utf-8").splitlines()[0]
        if OUT.read_text(encoding="utf-8") != render(tailwind):
            print("FAIL  [brand] brand/dist/tokens.css is out of date with tokens.json. Rebuild it")
            return 1
        print("ok    [brand]")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render("--tailwind" in args), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
