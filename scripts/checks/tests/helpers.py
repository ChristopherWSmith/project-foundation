"""Helpers for the foundation self-tests. Run: python3 -m unittest discover -s scripts/checks/tests -v

Every test works on a throwaway copy of the repo these tests live in: the foundation folder (initialised on the
fly) or a product repo. Tests write their own config and fixtures, so they don't depend on a product's docs."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.com",
    "PYTHONWARNINGS": "ignore",
}
IMPLEMENTER, REVIEWER, CHRIS = "implementer-app[bot]", "astra-reviewer[bot]", "chris"


def sh(cmd, cwd, check=True, env=None) -> subprocess.CompletedProcess:
    res = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True, env={**ENV, **(env or {})})
    if check and res.returncode != 0:
        raise AssertionError(f"command failed ({res.returncode}): {cmd}\n--- stdout\n{res.stdout}\n--- stderr\n{res.stderr}")
    return res


def git(cwd, *args, check=True) -> str:
    return sh(["git", *args], cwd, check=check).stdout.strip()


def commit_all(cwd, msg="change") -> str:
    git(cwd, "add", "-A")
    git(cwd, "commit", "-qm", msg, "--allow-empty")
    return git(cwd, "rev-parse", "HEAD")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def set_json(path: Path, mutate) -> None:
    data = json.loads(path.read_text())
    mutate(data)
    path.write_text(json.dumps(data, indent=2) + "\n")


def project_json(repo: Path, stage="bootstrap", gates=None, test_globs=("selftest/**/*.test.mjs",)) -> None:
    """Write a complete, known .foundation/project.json (tests never depend on the product's own gates)."""
    names = ["install", "lint", "typecheck", "test", "build", "deadcode", "audit"]
    g = {n: {"run": None, "required": n != "deadcode"} for n in names}
    for n, cmd in (gates or {}).items():
        g[n]["run"] = cmd
    write(repo / ".foundation/project.json", json.dumps({"stage": stage, "gates": g, "tests": {"globs": list(test_globs), "min_files": 1}}, indent=2))


def fresh_repo(tmp: Path) -> Path:
    """A clean, initialised, committed copy with branches main == staging, staging checked out."""
    dest = tmp / "repo"
    shutil.copytree(REPO, dest, ignore=shutil.ignore_patterns("node_modules", ".venv", "__pycache__", ".next", "dist"))
    if (dest / ".foundation/IS_TEMPLATE").exists():
        shutil.rmtree(dest / ".git", ignore_errors=True)
        sh(["python3", "scripts/init.py", "Selftest App", "--github-owner", CHRIS, "--reviewer", REVIEWER], dest)
    elif not (dest / ".git").exists():
        git(dest, "init", "-q", "-b", "staging")
    for f in ["pnpm-lock.yaml", "package-lock.json", "package.json"]:
        (dest / f).unlink(missing_ok=True)
    set_json(dest / ".foundation/review.json", lambda c: c.update(reviewers=[REVIEWER], human_approvers=[CHRIS], implementers=[]))
    git(dest, "checkout", "-q", "-B", "staging")
    commit_all(dest, "selftest snapshot")
    git(dest, "branch", "-f", "main", "HEAD")
    return dest


def tmpdir() -> Path:
    return Path(tempfile.mkdtemp(prefix="foundation-selftest-"))
