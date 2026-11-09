"""Shared helpers for the foundation checks. Part of the project foundation. Stdlib only."""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DEFAULTS = {
    "ticket_pattern": r"(?:[A-Z][A-Z0-9]+-\d+|CU-[A-Za-z0-9]+|#\d+)",
    "code_dirs": ["src", "app", "apps", "packages", "lib", "server", "tests", "test"],
    "exclude_dirs": ["node_modules", "dist", "build", ".next", "coverage", ".turbo", "brand/dist", "scripts/checks"],
    "agents_md_max_lines": 200,
    "stale_doc_days": 90,
    "raw_hex_check": True,
}

ALWAYS_SKIP_PARTS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".next", ".turbo"}
IGNORE_MARK = "foundation-ignore"


def config() -> dict:
    cfg = dict(DEFAULTS)
    path = ROOT / ".foundation" / "hygiene.json"
    if path.exists():
        cfg.update(json.loads(path.read_text(encoding="utf-8")))
    return cfg


class Report:
    def __init__(self, name: str):
        self.name, self.fails, self.warns = name, [], []

    def fail(self, msg: str) -> None:
        self.fails.append(msg)

    def warn(self, msg: str) -> None:
        self.warns.append(msg)

    def finish(self) -> int:
        for w in self.warns:
            print(f"WARN  [{self.name}] {w}")
        for f in self.fails:
            print(f"FAIL  [{self.name}] {f}")
        if not self.fails:
            extra = f" ({len(self.warns)} warning(s))" if self.warns else ""
            print(f"ok    [{self.name}]{extra}")
        return 1 if self.fails else 0


def run_git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True)
        return out.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def repo_files() -> list[str]:
    """Tracked + untracked-but-not-ignored files, as repo-relative posix paths."""
    out = run_git("ls-files", "--cached", "--others", "--exclude-standard")
    if out is not None:
        files = [line for line in out.splitlines() if line]
    else:
        files = []
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in ALWAYS_SKIP_PARTS]
            for fn in filenames:
                files.append((Path(dirpath) / fn).relative_to(ROOT).as_posix())
    return sorted(f for f in files if not (set(f.split("/")) & ALWAYS_SKIP_PARTS) and (ROOT / f).is_file())


def is_excluded(path: str, excludes: list[str]) -> bool:
    parts = path.split("/")
    for ex in excludes:
        if "/" in ex:
            if path == ex or path.startswith(ex.rstrip("/") + "/"):
                return True
        elif ex in parts:
            return True
    return False


def code_files(exts: set[str], cfg: dict | None = None, extra_dirs: tuple[str, ...] = ()) -> list[str]:
    cfg = cfg or config()
    dirs = tuple(cfg["code_dirs"]) + extra_dirs
    return [
        f for f in repo_files()
        if f.split("/")[0] in dirs
        and Path(f).suffix in exts
        and not is_excluded(f, cfg["exclude_dirs"])
    ]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    data = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition(":")
            data[key.strip()] = re.sub(r"\s+#.*$", "", value).strip()
    return data


def strip_code(md: str) -> str:
    """Remove fenced code blocks, inline code and HTML comments from markdown."""
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", md)


def glob_to_regex(pattern: str) -> re.Pattern:
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile(out + r"\Z")


def path_matches(path: str, pattern: str) -> bool:
    rx = glob_to_regex(pattern)
    if "/" not in pattern:  # like .gitignore: a bare name matches at any depth
        return bool(rx.match(path.rsplit("/", 1)[-1]))
    return bool(rx.match(path))
