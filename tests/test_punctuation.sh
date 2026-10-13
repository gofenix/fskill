#!/usr/bin/env bash
# The write checker reports Chinese messages on stderr and "punctuation check: ok" on stdout.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

CHECKER="$ROOT/skills/write/scripts/check-punctuation.sh"
tmpdir=$(make_tmpdir)

run_check() {
  local dest="$1"
  shift
  bash "$CHECKER" "$@" >"$dest" 2>&1
}

printf '%s\n' '这是一句中文。下一句也正常。' > "$tmpdir/clean.md"
run_check "$tmpdir/clean.out" --lang zh "$tmpdir/clean.md"
grep -q 'punctuation check: ok' "$tmpdir/clean.out"

printf '%s\n' '这是一句中文,后面接英文.' > "$tmpdir/bad.md"
if run_check "$tmpdir/bad.out" --lang zh "$tmpdir/bad.md"; then
  echo "should reject half-width punctuation in zh"; exit 1
fi
grep -q '半角标点' "$tmpdir/bad.out"

printf '%s\n' '见 `中文,标点` 的写法。' > "$tmpdir/code.md"
run_check "$tmpdir/code.out" --lang zh "$tmpdir/code.md"
grep -q 'punctuation check: ok' "$tmpdir/code.out"

printf '%s\n' '用了一个月的Claude感觉不错。' > "$tmpdir/space.md"
if run_check "$tmpdir/space.out" --lang zh "$tmpdir/space.md"; then
  echo "should flag missing space between CJK and Latin"; exit 1
fi
grep -q '需要空格' "$tmpdir/space.out"

printf '%s\n' '这里不该出现—这个符号。' > "$tmpdir/dash.md"
if run_check "$tmpdir/dash.out" --lang zh "$tmpdir/dash.md"; then
  echo "should flag an em dash"; exit 1
fi
grep -q 'em dash' "$tmpdir/dash.out"

printf '%s\n' '这里有　全角空格。' > "$tmpdir/wide.md"
if run_check "$tmpdir/wide.out" --lang zh "$tmpdir/wide.md"; then
  echo "should flag an ideographic space"; exit 1
fi
grep -q '全角空格' "$tmpdir/wide.out"

echo "punctuation smoke: ok"
