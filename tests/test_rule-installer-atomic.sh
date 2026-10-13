#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

tmpdir=$(make_tmpdir)
home_dir="$tmpdir/home"
bin_dir="$tmpdir/bin"
prepare_codex_installer_bin "$bin_dir"

cat > "$bin_dir/curl" <<'CURL'
#!/bin/bash
outfile=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-o" ]; then outfile="$2"; shift 2; else shift; fi
done
printf '%s\n' 'partial download' > "$outfile"
exit 22
CURL
chmod +x "$bin_dir/curl"

mkdir -p \
  "$home_dir/.claude/rules" \
  "$home_dir/.codex" \
  "$home_dir/.gemini/antigravity-cli/rules"
printf '%s\n' 'original claude rule' > "$home_dir/.claude/rules/anti-patterns.md"
printf '%s\n' 'original codex guide' > "$home_dir/.codex/AGENTS.md"
printf '%s\n' 'original antigravity rule' > "$home_dir/.gemini/antigravity-cli/rules/anti-patterns.md"

for target in claude-code codex antigravity-cli; do
  if PATH="$bin_dir" HOME="$home_dir" /bin/bash \
    "$ROOT/scripts/setup-rule.sh" anti-patterns "$target" \
    >"$tmpdir/$target.out" 2>"$tmpdir/$target.err"; then
    echo "partial download should fail for $target"; exit 1
  fi
  grep -q 'could not fetch' "$tmpdir/$target.err"
  grep -q 'left untouched' "$tmpdir/$target.err"
done

grep -qx 'original claude rule' "$home_dir/.claude/rules/anti-patterns.md"
grep -qx 'original codex guide' "$home_dir/.codex/AGENTS.md"
grep -qx 'original antigravity rule' "$home_dir/.gemini/antigravity-cli/rules/anti-patterns.md"

if find "$home_dir" -name '*.tmp.*' -print -quit | grep -q .; then
  echo "failed installer left a temporary rule file"; exit 1
fi

# Ctrl-C mid-download must clean up the staged file, which no return path covers.
cat > "$bin_dir/curl" <<'CURL'
#!/bin/bash
outfile=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-o" ]; then outfile="$2"; shift 2; else shift; fi
done
printf '%s\n' 'partial download' > "$outfile"
kill -INT "$PPID"
exit 0
CURL
chmod +x "$bin_dir/curl"

for target in claude-code codex antigravity-cli; do
  if PATH="$bin_dir" HOME="$home_dir" /bin/bash \
    "$ROOT/scripts/setup-rule.sh" anti-patterns "$target" \
    >"$tmpdir/$target-int.out" 2>"$tmpdir/$target-int.err"; then
    echo "interrupted download should fail for $target"; exit 1
  fi
done

grep -qx 'original claude rule' "$home_dir/.claude/rules/anti-patterns.md"
grep -qx 'original codex guide' "$home_dir/.codex/AGENTS.md"
grep -qx 'original antigravity rule' "$home_dir/.gemini/antigravity-cli/rules/anti-patterns.md"

if find "$home_dir" -name '*.tmp.*' -print -quit | grep -q .; then
  echo "interrupted installer left a temporary rule file"; exit 1
fi

echo "rule installer atomic smoke: ok"
