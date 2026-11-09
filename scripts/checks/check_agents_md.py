#!/usr/bin/env python3
"""AGENTS.md stays short, and the paths and commands it names actually exist. Part of the project foundation."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import ROOT, Report, config, read, repo_files  # noqa: E402

PATH_EXT = re.compile(r"\.(md|json|ya?ml|toml|txt|ts|tsx|js|mjs|cjs|py|sh|sql|css)$")
PNPM_BUILTINS = {
    "install", "i", "add", "remove", "rm", "update", "up", "dlx", "exec", "create", "audit", "outdated",
    "list", "ls", "why", "store", "init", "publish", "link", "unlink", "prune", "rebuild", "import",
    "fetch", "patch", "env", "setup", "config",
}


def looks_like_path(token: str) -> bool:
    if any(c in token for c in " <>*{}|…$") or "YYYY" in token or "NNNN" in token or "://" in token:
        return False
    if token.startswith(("/", "~", "-", "@")):
        return False
    return "/" in token or bool(PATH_EXT.search(token))


def section(text: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    return m.group(1) if m else ""


def check_command(cmd: str, scripts: dict | None, r: Report, where: str) -> None:
    cmd = cmd.strip()
    first = cmd.split()[0]
    if first.startswith("./") or first.startswith("scripts/"):
        if not (ROOT / first).exists():
            r.fail(f"{where}: command `{cmd}` → {first} doesn't exist")
        return
    m = re.match(r"^(?:pnpm|yarn|bun)(?:\s+run)?\s+([\w:.-]+)|^npm\s+(?:run\s+)?([\w:.-]+)", cmd)
    if not m:
        return
    name = m.group(1) or m.group(2)
    if cmd.startswith("pnpm") and not cmd.startswith("pnpm run") and name in PNPM_BUILTINS:
        return
    if cmd.startswith("npm") and name in {"install", "i", "ci", "audit", "exec"}:
        return
    if scripts is None:
        r.warn(f"{where}: can't verify `{cmd}`, there's no package.json yet")
    elif name not in scripts:
        r.fail(f"{where}: `{cmd}` but package.json has no `{name}` script")


def main() -> int:
    r = Report("agents")
    cfg = config()
    files = [f for f in repo_files() if f.rsplit("/", 1)[-1] == "AGENTS.md"]
    if "AGENTS.md" not in files:
        r.fail("AGENTS.md is missing at the repo root")
        return r.finish()

    pkg = ROOT / "package.json"
    scripts = json.loads(pkg.read_text()).get("scripts", {}) if pkg.exists() else None

    for path in files:
        text = read(path)
        base = (ROOT / path).parent
        lines = text.count("\n") + 1
        if lines > cfg["agents_md_max_lines"]:
            r.warn(f"{path}: {lines} lines (budget {cfg['agents_md_max_lines']}). Move detail into docs/ and link to it")

        visible = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        for token in sorted(set(re.findall(r"`([^`\n]+)`", visible))):
            t = token.removeprefix("./")
            if looks_like_path(t) and not (base / t).exists() and not (ROOT / t).exists():
                r.fail(f"{path}: refers to `{token}`, which doesn't exist (stale reference?)")

        empty = 0
        for row in section(text, "Commands").splitlines():
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) < 2 or set(cells[0]) <= {"-", " "} or cells[0] == "Task":
                continue
            cmds = re.findall(r"`([^`]+)`", cells[1])
            if not cmds:
                empty += 1
            for c in cmds:
                check_command(c, scripts, r, path)
        if empty:
            r.warn(f"{path}: {empty} command row(s) still empty; agents will guess")

    return r.finish()


if __name__ == "__main__":
    sys.exit(main())
