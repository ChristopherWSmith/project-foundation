#!/usr/bin/env python3
"""Run the project's quality gates from .foundation/project.json. Part of the project foundation.

  quality_gates.py                       all gates
  quality_gates.py --gates lint,test     a subset (CI: checks job = install..deadcode, security job = audit)
  quality_gates.py --stage               print the stage and exit

Stage "bootstrap": an unset gate is reported, not enforced. A gate that IS set must pass.
Stage "development": every required gate must be set to a real command and pass, and test files must exist.
In both stages, placeholder commands (TODO, echo, true, `|| true`, --if-present, --passWithNoTests) are rejected
for required gates, because they make a gate pass without checking anything.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import ROOT, Report, path_matches, repo_files  # noqa: E402

CONFIG = ROOT / ".foundation" / "project.json"
STAGES = {"bootstrap", "development"}
FAKE = re.compile(
    r"(?i)\bTODO\b|^\s*(true|:|exit\s+0)\s*$|^\s*echo\b|\|\|\s*(true|:|exit\s+0)\s*$|--if-present|--passWithNoTests|--pass-with-no-tests"
)


def load() -> dict:
    if not CONFIG.exists():
        sys.exit("FAIL  [gates] .foundation/project.json is missing")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    if cfg.get("stage") not in STAGES:
        sys.exit(f"FAIL  [gates] stage must be one of {sorted(STAGES)}, got {cfg.get('stage')!r}")
    return cfg


def count_tests(cfg: dict) -> int:
    globs = cfg.get("tests", {}).get("globs", [])
    return sum(1 for f in repo_files() if any(path_matches(f, g) for g in globs))


def summary(lines: list[str]) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")


def main() -> int:
    args = sys.argv[1:]
    cfg = load()
    stage = cfg["stage"]
    if "--stage" in args:
        print(stage)
        return 0

    r = Report("gates")
    gates = cfg.get("gates", {})
    wanted = args[args.index("--gates") + 1].split(",") if "--gates" in args else list(gates)
    rows = [f"### Quality gates (stage: **{stage}**)", "", "| Gate | Command | Result |", "|---|---|---|"]

    if stage == "bootstrap":
        print("NOTE  [gates] stage=bootstrap: unset gates are not enforced, and promotion to main is blocked.")

    for name in wanted:
        gate = gates.get(name)
        if gate is None:
            r.fail(f"unknown gate '{name}' (not in .foundation/project.json)")
            continue
        cmd = (gate.get("run") or "").strip()
        required = bool(gate.get("required"))

        if not cmd:
            if stage == "development" and required:
                r.fail(f"{name}: required gate has no command (hint: {gate.get('hint', '—')})")
                rows.append(f"| {name} | — | ❌ not set |")
            else:
                print(f"skip  [gates] {name}: not set{' (bootstrap)' if required else ' (optional)'}")
                rows.append(f"| {name} | — | not set |")
            continue

        if FAKE.search(cmd) and required:
            r.fail(f"{name}: `{cmd}` can pass without checking anything; use the real command")
            rows.append(f"| {name} | `{cmd}` | ❌ placeholder |")
            continue

        print(f"run   [gates] {name}: {cmd}", flush=True)
        result = subprocess.run(cmd, shell=True, cwd=ROOT)
        if result.returncode != 0:
            r.fail(f"{name}: `{cmd}` exited {result.returncode}")
            rows.append(f"| {name} | `{cmd}` | ❌ exit {result.returncode} |")
        else:
            rows.append(f"| {name} | `{cmd}` | ✅ |")

    if stage == "development" and "test" in wanted:
        n = count_tests(cfg)
        minimum = cfg.get("tests", {}).get("min_files", 1)
        if n < minimum:
            r.fail(f"found {n} test file(s), need at least {minimum} (tests.globs in project.json). Mandatory tests are missing")
        rows.append(f"| test files | {cfg.get('tests', {}).get('globs')} | {'✅' if n >= minimum else '❌'} {n} found |")

    summary(rows)
    return r.finish()


if __name__ == "__main__":
    sys.exit(main())
