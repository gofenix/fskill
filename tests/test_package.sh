#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

tmpdir=$(make_tmpdir)
"$ROOT/scripts/package-skill.sh" "$tmpdir/fskill.zip" >/dev/null
zipinfo -1 "$tmpdir/fskill.zip" >"$tmpdir/manifest"

# Root SKILL.md is present; nested SKILL.md files are inlined, never re-shipped.
grep -qx 'SKILL.md' "$tmpdir/manifest"
test "$(zipinfo -1 "$tmpdir/fskill.zip" | grep -ciE '(^|/)skill\.md$')" -eq 1

# RESOLVER.md is routing for direct installs; the ZIP root dispatcher already
# inlines the routing table, so shipping it would be dead weight.
if grep -qx 'skills/RESOLVER.md' "$tmpdir/manifest"; then
  echo "package smoke: skills/RESOLVER.md must not ship in the ZIP"
  exit 1
fi

# Required helper scripts are bundled.
for required in \
  skills/check/scripts/audit_signals.py \
  skills/read/scripts/fetch.sh \
  skills/health/scripts/block-pipe-to-shell.py \
  skills/health/scripts/check-agent-context.sh \
  skills/health/scripts/check-doc-refs.sh \
  skills/health/scripts/check-maintainability.sh \
  skills/health/scripts/check-verifier-output.sh \
  skills/health/scripts/conversation_audit.py \
  skills/health/scripts/read_skill_description.py \
  skills/health/scripts/run-health.ps1 \
  skills/health/scripts/scan_skill_security.py \
  skills/health/agents/inspector-maintainability.md; do
  grep -qx "$required" "$tmpdir/manifest"
done

# Allowlist contract: build-only files and dev metadata never ship.
for forbidden in \
  .gitignore \
  Makefile \
  VERSION \
  package.json \
  packaging.allowlist \
  scripts/check_routing_drift.py \
  scripts/verify_skills.py \
  scripts/verify-skills.sh \
  scripts/build_metadata.py \
  scripts/package-skill.sh \
  scripts/packaging_filter.py \
  scripts/skill_checks.py \
  scripts/skill_frontmatter.py \
  scripts/validate_package.py; do
  if grep -qx "$forbidden" "$tmpdir/manifest"; then
    echo "forbidden file leaked into package: $forbidden"; exit 1
  fi
done
if grep -qE '^(docs|tests|\.github|\.claude-plugin|\.codex-plugin|\.agents|plugins)/' "$tmpdir/manifest"; then
  echo "forbidden directory leaked into package"; exit 1
fi

# Root SKILL.md inlines every skill body and rewrites cross-refs. Read the
# bundled file once into memory; bash string matching avoids the SIGPIPE that
# `unzip -p | grep -q` would raise under `set -o pipefail`.
root_skill=$(unzip -p "$tmpdir/fskill.zip" SKILL.md)
[[ "$root_skill" == *"SKILL: check"* ]] || { echo "expected 'SKILL: check' section in root SKILL.md"; exit 1; }
if [[ "$root_skill" == *"skills/check/SKILL.md"* ]]; then
  echo "package root should not reference nested SKILL.md"; exit 1
fi
if [[ "$root_skill" != *'`skills/check/references/project-context.md`'* ]]; then
  echo "package root should rewrite inlined skill-relative backtick paths"; exit 1
fi
if [[ "$root_skill" != *'[references/review-patterns.md](skills/check/references/review-patterns.md)'* ]]; then
  echo "package root should rewrite inlined skill-relative Markdown links"; exit 1
fi

# Second-hop references inside shipped Markdown must also resolve from the ZIP
# root instead of pointing at nonexistent root references/ paths.
workflows=$(unzip -p "$tmpdir/fskill.zip" skills/check/references/maintainer-workflows.md)
[[ "$workflows" == *'[release-artifacts.md](skills/check/references/release-artifacts.md)'* ]] || {
  echo "nested reference should qualify a same-directory basename"; exit 1
}
prose=$(unzip -p "$tmpdir/fskill.zip" skills/write/references/write-zh-prose.md)
[[ "$prose" == *'`skills/write/references/write-zh.md`'* ]] || {
  echo "nested basename should resolve in another skill independently"; exit 1
}

echo "package smoke: ok"
