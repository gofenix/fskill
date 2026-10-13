#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

CHECKER="$ROOT/skills/health/scripts/check-verifier-output.sh"

tmpdir=$(make_tmpdir)
project="$tmpdir/project"
mkdir -p "$project/src"

# Stale golangci-lint path triggers WARN + targeted cache-clean suggestion.
printf '%s\n' \
  'golangci-lint run ./cmd/...' \
  '/private/tmp/deleted-worktree/foo.go:12: errcheck failed' \
  > "$tmpdir/stale.log"
bash "$CHECKER" "$project" "$tmpdir/stale.log" >"$tmpdir/stale.out"
grep -q '^verifier_output_status: WARN$' "$tmpdir/stale.out"
grep -q '/private/tmp/deleted-worktree/foo.go' "$tmpdir/stale.out"
grep -q 'golangci-lint cache clean' "$tmpdir/stale.out"

# Existing /tmp path should NOT be flagged as stale.
existing_file="/tmp/fskill-verifier-existing-$$.go"
touch "$existing_file"
printf '%s\n' "go test $existing_file:1" > "$tmpdir/existing.log"
bash "$CHECKER" "$project" "$tmpdir/existing.log" >"$tmpdir/existing.out"
rm -f "$existing_file"
grep -q '^verifier_output_status: PASS$' "$tmpdir/existing.out"
if grep -q 'stale external verifier paths detected' "$tmpdir/existing.out"; then
  echo "verifier output should not flag existing tmp paths"; exit 1
fi

# Unknown verifier with stale /private/tmp path -> WARN + generic suggestion.
printf '%s\n' 'unknown verifier failed at /private/tmp/ghost/tool.out' > "$tmpdir/unknown.log"
bash "$CHECKER" "$project" "$tmpdir/unknown.log" >"$tmpdir/unknown.out"
grep -q '^verifier_output_status: WARN$' "$tmpdir/unknown.out"
grep -q 'rerun the verifier after removing stale temporary worktrees' "$tmpdir/unknown.out"

echo "verifier output smoke: ok"
