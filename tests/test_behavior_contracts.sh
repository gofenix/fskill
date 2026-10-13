#!/usr/bin/env bash
# Static routing/contract checks for the explicit-invocation skill set.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

check="$ROOT/skills/check/SKILL.md"
think="$ROOT/skills/think/SKILL.md"
ui="$ROOT/skills/ui/SKILL.md"
design="$ROOT/skills/ui/references/design-reference.md"
health="$ROOT/skills/health/SKILL.md"
write="$ROOT/skills/write/SKILL.md"

grep -q '显式调用' "$check"
grep -q '/check' "$check"
grep -q '不应用下文流程' "$check"
grep -q '显式调用' "$think"
grep -q '/think' "$think"
grep -q '显式调用' "$ui"
grep -q '/ui' "$ui"
grep -q 'references/design-reference.md' "$ui"
test -f "$design"
grep -q 'summary 和 deep 都只生成报告' "$health"
grep -q '不自动切换技能' "$write"
grep -q '/write' "$write"

echo "behavior contracts smoke: ok"
