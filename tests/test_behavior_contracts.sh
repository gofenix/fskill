#!/usr/bin/env bash
# Static routing/contract checks for workflows and shared engineering principles.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

check="$ROOT/skills/check/SKILL.md"
think="$ROOT/skills/think/SKILL.md"
ui="$ROOT/skills/ui/SKILL.md"
traps="$ROOT/skills/ui/references/design-traps.md"
health="$ROOT/skills/health/SKILL.md"
write="$ROOT/skills/write/SKILL.md"
principles="$ROOT/rules/principles.md"
fmode_principles="$ROOT/skills/f-mode/references/principles.md"

grep -q '/check' "$check"
grep -q '显式调用' "$check"
grep -q '不扩大授权' "$check"
grep -q '/think' "$think"
grep -q '显式调用' "$think"
grep -q '不扩大授权' "$think"
grep -q '显式调用' "$ui"
grep -q '/ui' "$ui"
for skill_md in "$ROOT"/skills/*/SKILL.md; do
  grep -qx 'disable-model-invocation: true' "$skill_md"
  policy="$(dirname "$skill_md")/agents/openai.yaml"
  grep -q 'allow_implicit_invocation: false' "$policy"
done
grep -q 'references/design-traps.md' "$ui"
test -f "$traps"
grep -q 'summary 和 deep 都只生成报告' "$health"
grep -q '不自动切换技能' "$write"
grep -q '/write' "$write"
test -f "$principles"
cmp "$principles" "$fmode_principles"
grep -q '先减后增' "$principles"
grep -q '真实验收' "$principles"
grep -q '边界与单向门' "$principles"

echo "behavior contracts smoke: ok"
