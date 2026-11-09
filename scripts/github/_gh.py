"""Tiny wrapper around the `gh` CLI shared by the protection scripts. Stdlib only."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile


class GhError(RuntimeError):
    def __init__(self, args, stderr):
        super().__init__(f"gh {' '.join(args)}: {stderr.strip()[:300]}")
        self.stderr = stderr


def gh(*args: str, body: dict | None = None, paginate: bool = False):
    """Run `gh api ...` and return parsed JSON (None for empty output)."""
    cmd = ["gh", "api", *args]
    tmp = None
    if body is not None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(body, tmp)
        tmp.close()
        cmd += ["--input", tmp.name]
    if paginate:
        cmd += ["--paginate", "--slurp"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit("gh CLI not found. Install it and run `gh auth login`.")
    if out.returncode != 0:
        raise GhError(args, out.stderr or out.stdout)
    if not out.stdout.strip():
        return None
    data = json.loads(out.stdout)
    if paginate:
        return [item for page in data for item in (page if isinstance(page, list) else [page])]
    return data
