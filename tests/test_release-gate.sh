#!/usr/bin/env bash
# Release readiness lives in the check skill and release-artifacts reference.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

skill="$ROOT/skills/check/SKILL.md"
artifacts="$ROOT/skills/check/references/release-artifacts.md"

test -f "$artifacts"
grep -q 'references/release-artifacts.md' "$skill"
grep -q '不能说已就绪' "$skill"

echo "release gate smoke: ok"
