#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

tmpdir=$(make_tmpdir)
home_dir="$tmpdir/home"
bin_dir="$tmpdir/bin"
mkdir -p "$home_dir/.codex" "$home_dir/.claude/rules"
prepare_codex_installer_bin "$bin_dir"
ln -s "$(command -v cp)" "$bin_dir/cp"
cat >"$bin_dir/curl" <<'CURL'
#!/bin/bash
set -euo pipefail
outfile=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-o" ]; then outfile="$2"; shift 2; else shift; fi
done
cp "$ROOT/rules/clarity.md" "$outfile"
CURL
chmod +x "$bin_dir/curl"

printf 'Keep my project instructions.\n' >"$home_dir/.codex/AGENTS.md"
printf 'Keep my other rule.\n' >"$home_dir/.claude/rules/custom.md"
for target in claude-code codex antigravity-cli; do
  for run in 1 2; do
    PATH="$bin_dir" HOME="$home_dir" /bin/bash "$ROOT/scripts/setup-rule.sh" clarity "$target" >"$tmpdir/$target-$run.out"
  done
done

cmp "$ROOT/rules/clarity.md" "$home_dir/.claude/rules/clarity.md"
cmp "$ROOT/rules/clarity.md" "$home_dir/.gemini/antigravity-cli/rules/clarity.md"
grep -qx 'Keep my other rule.' "$home_dir/.claude/rules/custom.md"
python3 - "$home_dir/.codex/AGENTS.md" "$ROOT/rules/clarity.md" <<'PY'
import sys
from pathlib import Path
target, source = map(Path, sys.argv[1:])
expected = 'Keep my project instructions.\n\n<!-- Waza Clarity: start -->\n' + source.read_text().strip() + '\n<!-- Waza Clarity: end -->\n'
assert target.read_text() == expected, 'Repeated install changed existing instructions or duplicated the rule'
PY

echo "Clarity installer smoke: ok"
