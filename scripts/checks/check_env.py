#!/usr/bin/env python3
"""Every env var the code reads is listed in .env.example (and the typed schema, if there is one). Part of the project foundation."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import ROOT, Report, code_files, config, read  # noqa: E402

SCHEMA_FILE = "src/config/env.ts"
CODE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".vue", ".svelte", ".astro"}
READS = [
    r"process\.env\.([A-Z][A-Z0-9_]*)",
    r"process\.env\[\s*[\"']([A-Z][A-Z0-9_]*)[\"']\s*\]",
    r"import\.meta\.env\.([A-Z][A-Z0-9_]*)",
    r"os\.environ\[\s*[\"']([A-Z][A-Z0-9_]*)[\"']\s*\]",
    r"os\.environ\.get\(\s*[\"']([A-Z][A-Z0-9_]*)[\"']",
    r"os\.getenv\(\s*[\"']([A-Z][A-Z0-9_]*)[\"']",
    r"Deno\.env\.get\(\s*[\"']([A-Z][A-Z0-9_]*)[\"']",
]
PLATFORM = {"CI", "HOME", "PATH", "PWD", "TZ", "PORT", "MODE", "DEV", "PROD", "SSR", "BASE_URL"}
PLATFORM_PREFIXES = ("GITHUB_", "RAILWAY_", "VERCEL_", "RUNNER_", "npm_")


def main() -> int:
    r = Report("env")
    example_path = ROOT / ".env.example"
    if not example_path.exists():
        r.fail(".env.example is missing")
        return r.finish()
    example = set(re.findall(r"^\s*([A-Z][A-Z0-9_]*)\s*=", example_path.read_text(), flags=re.M))

    schema: set[str] = set()
    if (ROOT / SCHEMA_FILE).exists():
        schema = set(re.findall(r"^\s+([A-Z][A-Z0-9_]*)\s*:", read(SCHEMA_FILE), flags=re.M))

    direct: dict[str, set[str]] = {}
    files = code_files(CODE_EXTS, config(), extra_dirs=("scripts",))
    for f in files:
        text = read(f)
        for rx in READS:
            for name in re.findall(rx, text):
                if name in PLATFORM or name.startswith(PLATFORM_PREFIXES):
                    continue
                direct.setdefault(name, set()).add(f)

    for name in sorted((schema | set(direct)) - example):
        where = SCHEMA_FILE if name in schema else ", ".join(sorted(direct[name])[:3])
        r.fail(f"{name} is read in {where} but missing from .env.example")

    if schema:
        for name in sorted(example - schema - PLATFORM):
            r.warn(f"{name} is in .env.example but not in {SCHEMA_FILE}")
        outside = sorted({f for fs in direct.values() for f in fs} - {SCHEMA_FILE})
        if outside:
            r.warn(f"process.env read directly in {', '.join(outside[:5])}; import `env` from {SCHEMA_FILE} instead")
    elif files and direct:
        for name in sorted(example - set(direct) - {"NODE_ENV"}):
            r.warn(f"{name} is in .env.example but nothing reads it")

    return r.finish()


if __name__ == "__main__":
    sys.exit(main())
