#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

tmpdir=$(make_tmpdir)
home_dir="$tmpdir/home"
bin_dir="$tmpdir/bin"
mkdir -p "$home_dir/.codex"
prepare_codex_installer_bin "$bin_dir"
write_stub_curl "$bin_dir" "## Anti-Patterns\n\nanti-patterns rule\n"

PATH="$bin_dir" HOME="$home_dir" /bin/bash "$ROOT/scripts/setup-rule.sh" anti-patterns claude-code >"$tmpdir/claude.out"
grep -q 'anti-patterns rule' "$home_dir/.claude/rules/anti-patterns.md"

# Idempotent for Codex target: two runs leave exactly one marker.
PATH="$bin_dir" HOME="$home_dir" /bin/bash "$ROOT/scripts/setup-rule.sh" anti-patterns codex >"$tmpdir/codex1.out"
PATH="$bin_dir" HOME="$home_dir" /bin/bash "$ROOT/scripts/setup-rule.sh" anti-patterns codex >"$tmpdir/codex2.out"
test "$(grep -c '<!-- fskill Anti-Patterns: start -->' "$home_dir/.codex/AGENTS.md")" -eq 1
grep -q 'anti-patterns rule' "$home_dir/.codex/AGENTS.md"

if PATH="$bin_dir" HOME="$home_dir" /bin/bash "$ROOT/scripts/setup-rule.sh" ../CLAUDE claude-code >"$tmpdir/traversal.out" 2>"$tmpdir/traversal.err"; then
  echo "setup-rule should reject path traversal rule names"; exit 1
fi
grep -q 'rule-name must match' "$tmpdir/traversal.err"
test ! -f "$home_dir/.claude/CLAUDE.md"
if WAZA_REF='../main' PATH="$bin_dir" HOME="$home_dir" /bin/bash "$ROOT/scripts/setup-rule.sh" anti-patterns claude-code >"$tmpdir/ref.out" 2>"$tmpdir/ref.err"; then
  echo "setup-rule should reject unsafe WAZA_REF"; exit 1
fi
grep -q 'WAZA_REF must be main or a release tag' "$tmpdir/ref.err"

echo "Anti-Patterns installer smoke: ok"
