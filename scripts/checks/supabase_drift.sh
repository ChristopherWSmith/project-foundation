#!/usr/bin/env bash
# Part of the project foundation.
# Generated DB types match the migrations, and every public table has row-level security.
# Needs a running local Supabase (`supabase start`). Pin the CLI version: different versions format types differently.
# Don't run a formatter over the generated types file; add it to your formatter's ignore list.
set -euo pipefail

TYPES_FILE="${TYPES_FILE:-src/types/database.ts}"
DB_URL="${DB_URL:-postgresql://postgres:postgres@127.0.0.1:54322/postgres}"
fail=0

tmp="$(mktemp)"
supabase gen types typescript --local > "$tmp"
if [ ! -f "$TYPES_FILE" ]; then
  echo "FAIL  [supabase] $TYPES_FILE is missing. Run: supabase gen types typescript --local > $TYPES_FILE"
  fail=1
elif ! diff -q "$TYPES_FILE" "$tmp" >/dev/null; then
  echo "FAIL  [supabase] $TYPES_FILE is out of date with the migrations. Regenerate it:"
  diff -u "$TYPES_FILE" "$tmp" | head -40 || true
  fail=1
else
  echo "ok    [supabase] generated types match the migrations"
fi

no_rls="$(psql "$DB_URL" -At -c "select tablename from pg_tables where schemaname = 'public' and not rowsecurity order by 1")"
if [ -n "$no_rls" ]; then
  echo "FAIL  [supabase] RLS is off on: $(echo "$no_rls" | paste -sd, -)"
  fail=1
else
  echo "ok    [supabase] RLS is on for every public table"
fi

no_policy="$(psql "$DB_URL" -At -c "select c.relname from pg_class c join pg_namespace n on n.oid = c.relnamespace where n.nspname = 'public' and c.relkind = 'r' and c.relrowsecurity and not exists (select 1 from pg_policy p where p.polrelid = c.oid) order by 1")"
if [ -n "$no_policy" ]; then
  echo "WARN  [supabase] RLS on but no policies (nothing can read them; intended?): $(echo "$no_policy" | paste -sd, -)"
fi

exit $fail
