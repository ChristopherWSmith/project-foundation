#!/usr/bin/env python3
"""A stateful stand-in for `gh api`, for tests only. State lives in $MOCK_GH_STATE (JSON); calls are appended to
$MOCK_GH_LOG. Models just the endpoints apply-protection.py and verify-protection.py use."""
import base64
import json
import os
import re
import sys

state_path, log_path = os.environ["MOCK_GH_STATE"], os.environ["MOCK_GH_LOG"]
state = json.load(open(state_path))
args = sys.argv[1:]
assert args[0] == "api", args
args = args[1:]
method, body, paginate = "GET", None, "--paginate" in args
if "-X" in args:
    method = args[args.index("-X") + 1]
if "--input" in args:
    body = json.load(open(args[args.index("--input") + 1]))
path = next(a for a in args if a not in ("-X", method, "--input", "--paginate", "--slurp") and not a.endswith(".json") and not a.startswith("-"))
with open(log_path, "a") as fh:
    fh.write(json.dumps({"method": method, "path": path, "body": body}) + "\n")


def out(data, code=0):
    if paginate:
        data = [data]
    print(json.dumps(data))
    json.dump(state, open(state_path, "w"))
    sys.exit(code)


def fail(msg="Not Found"):
    print(json.dumps({"message": msg}), file=sys.stderr)
    sys.exit(1)


path = path.split("?")[0] if not path.startswith("repos/") or "/contents/" not in path else path
m = re.match(r"repos/[^/]+/[^/]+(.*)$", path)
rest = m.group(1) if m else None

if path.startswith("user/installations"):
    out({"total_count": len(state["installations"]), "installations": state["installations"]})
if rest is None:
    fail()
if rest == "":
    if method == "PATCH":
        state["repo"].update(body)
    out(state["repo"])
if rest == "/branches/staging":
    out({"name": "staging"}) if "staging" in state["branches"] else fail()
if rest == "/rulesets":
    if method == "POST":
        body = dict(body, id=state["next_id"])
        state["next_id"] += 1
        state["rulesets"].append(body)
        out(body)
    out([{"id": r["id"], "name": r["name"]} for r in state["rulesets"]])
m = re.match(r"/rulesets/(\d+)$", rest)
if m:
    rid = int(m.group(1))
    idx = next((i for i, r in enumerate(state["rulesets"]) if r["id"] == rid), None)
    if idx is None:
        fail()
    if method == "PUT":
        state["rulesets"][idx] = dict(body, id=rid)
    out(state["rulesets"][idx])
m = re.match(r"/environments/([^/]+)$", rest)
if m and method == "PUT":
    state["environments"].setdefault(m.group(1), [])
    out({"name": m.group(1)})
m = re.match(r"/environments/([^/]+)/deployment-branch-policies(?:/(\d+))?$", rest)
if m:
    env, pid = m.group(1), m.group(2)
    if env not in state["environments"]:
        fail()
    pols = state["environments"][env]
    if method == "POST":
        pols.append({"id": state["next_id"], "name": body["name"]})
        state["next_id"] += 1
        out(pols[-1])
    if method == "DELETE":
        state["environments"][env] = [p for p in pols if p["id"] != int(pid)]
        out({})
    out({"total_count": len(pols), "branch_policies": pols})
m = re.match(r"/contents/([^?]+)", rest)
if m:
    f = state["files"].get(m.group(1))
    out({"content": base64.b64encode(f.encode()).decode()}) if f is not None else fail()
fail(f"mock: unhandled {method} {path}")
