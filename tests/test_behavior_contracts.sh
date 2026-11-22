#!/usr/bin/env bash
# Static routing/contract checks for workflows and p-* principle skills.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

check="$ROOT/skills/check/SKILL.md"
think="$ROOT/skills/think/SKILL.md"
ui="$ROOT/skills/ui/SKILL.md"
traps="$ROOT/skills/ui/references/design-traps.md"
health="$ROOT/skills/health/SKILL.md"
write="$ROOT/skills/write/SKILL.md"
principle="$ROOT/skills/p-subtract-before-add/SKILL.md"

grep -q '/check' "$check"
grep -q '无需用户点名' "$check"
grep -q '不扩大授权' "$check"
grep -q '/think' "$think"
grep -q '无需用户点名' "$think"
grep -q '不扩大授权' "$think"
grep -q '显式调用' "$ui"
grep -q '/ui' "$ui"
grep -q 'references/design-traps.md' "$ui"
test -f "$traps"
grep -q 'summary 和 deep 都只生成报告' "$health"
grep -q '不自动切换技能' "$write"
grep -q '/write' "$write"
grep -q 'disable-model-invocation: false' "$principle"

echo "behavior contracts smoke: ok"
