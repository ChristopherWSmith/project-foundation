#!/usr/bin/env bash
# Run every foundation check locally, the same as CI's drift job. Part of the project foundation.
# Usage: ./scripts/check-all.sh [--base <ref>] [--with-db]
set -uo pipefail
cd "$(dirname "$0")/.."

status=0
run() { "$@" || status=1; }

run python3 scripts/checks/check_docs.py
run python3 scripts/checks/check_agents_md.py
run python3 scripts/checks/check_env.py
run python3 scripts/checks/check_hygiene.py
run python3 scripts/brand/build_tokens.py --check

base_args=()
with_db=0
while [ $# -gt 0 ]; do
  case "$1" in
    --base) base_args=(--base "$2"); shift 2 ;;
    --with-db) with_db=1; shift ;;
    *) shift ;;
  esac
done
run python3 scripts/checks/doc_triggers.py ${base_args[@]+"${base_args[@]}"}
if [ "$with_db" = 1 ]; then run ./scripts/checks/supabase_drift.sh; fi

echo
if [ $status -eq 0 ]; then echo "All foundation checks passed."; else echo "Some foundation checks failed (see FAIL lines above)."; fi
exit $status
