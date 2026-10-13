#!/usr/bin/env bash
# Release readiness lives in the check skill references, not a separate gate script.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

skill="$ROOT/skills/check/SKILL.md"
workflows="$ROOT/skills/check/references/maintainer-workflows.md"
artifacts="$ROOT/skills/check/references/release-artifacts.md"

test -f "$workflows"
test -f "$artifacts"
grep -q 'references/maintainer-workflows.md' "$skill"
grep -q 'release-artifacts.md' "$workflows"
grep -q '不能说已就绪' "$skill"

echo "release gate smoke: ok"
