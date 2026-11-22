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

# The complete license ships once, at the archive root.
unzip -p "$tmpdir/fskill.zip" LICENSE > "$tmpdir/root-license"
cmp "$ROOT/LICENSE" "$tmpdir/root-license"
if grep -qiE '(^|/)NOTICE\.md$' "$tmpdir/manifest"; then
  echo "package contains duplicate NOTICE.md files"
  exit 1
fi

# RESOLVER.md is routing for direct installs; the ZIP root dispatcher already
# inlines the routing table, so shipping it would be dead weight.
if grep -qx 'skills/RESOLVER.md' "$tmpdir/manifest"; then
  echo "package smoke: skills/RESOLVER.md must not ship in the ZIP"
  exit 1
fi

# Required helper scripts and keeper references are bundled.
for required in \
  skills/f-mode/references/principles.md \
  skills/check/references/review-patterns.md \
  skills/check/references/release-artifacts.md \
  skills/check/references/incident-ledger.md \
  skills/hunt/references/ime-unicode.md \
  skills/learn/references/read-methods.md \
  skills/health/references/prune.md \
  skills/ui/references/design-traps.md \
  skills/write/references/write-zh.md \
  skills/check/scripts/audit_signals.py \
  skills/learn/scripts/fetch.sh \
  skills/health/scripts/block-pipe-to-shell.py \
  skills/health/scripts/check-agent-context.sh \
  skills/health/scripts/check-doc-refs.sh \
  skills/health/scripts/check-maintainability.sh \
  skills/health/scripts/check-verifier-output.sh \
  skills/health/scripts/conversation_audit.py \
  skills/health/scripts/read_skill_description.py \
  skills/health/scripts/run-health.ps1 \
  skills/health/scripts/scan_skill_security.py; do
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

# Root SKILL.md inlines every workflow section and rewrites relative refs.
root_skill=$(unzip -p "$tmpdir/fskill.zip" SKILL.md)
[[ "$root_skill" == *"SKILL: check"* ]] || { echo "expected 'SKILL: check' section in root SKILL.md"; exit 1; }
if [[ "$root_skill" == *"SKILL: p-"* ]]; then
  echo "unexpected p-* skill section in root SKILL.md"; exit 1
fi
unzip -p "$tmpdir/fskill.zip" skills/f-mode/references/principles.md > "$tmpdir/fmode-principles.md"
cmp "$ROOT/rules/principles.md" "$tmpdir/fmode-principles.md"
if [[ "$root_skill" == *"skills/check/SKILL.md"* ]]; then
  echo "package root should not reference nested SKILL.md"; exit 1
fi
if [[ "$root_skill" != *'[审查模式](skills/check/references/review-patterns.md)'* ]]; then
  echo "package root should rewrite inlined skill-relative Markdown links"; exit 1
fi
if [[ "$root_skill" != *'[发布产物](skills/check/references/release-artifacts.md)'* ]]; then
  echo "package root should rewrite release-artifacts link"; exit 1
fi

# Second-hop references inside shipped Markdown must also resolve from the ZIP root.
reviews=$(unzip -p "$tmpdir/fskill.zip" skills/check/references/review-patterns.md)
[[ "$reviews" == *'[事故台账](skills/check/references/incident-ledger.md)'* ]] || {
  echo "nested reference should qualify a same-directory link"; exit 1
}

echo "package smoke: ok"
