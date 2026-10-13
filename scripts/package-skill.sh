#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-"$ROOT/dist/waza.zip"}"
case "$OUT" in
  /*) ;;
  *) OUT="$ROOT/$OUT" ;;
esac

mkdir -p "$(dirname "$OUT")"
rm -f "$OUT"

cd "$ROOT"

MANIFEST="$(mktemp)"
FILTERED_MANIFEST="$(mktemp)"
STAGE="$(mktemp -d)"
VALIDATE_DIR="$(mktemp -d)"
trap 'rm -f "$MANIFEST" "$FILTERED_MANIFEST"; rm -rf "$STAGE" "$VALIDATE_DIR"' EXIT

git ls-files --cached --others --exclude-standard > "$MANIFEST"

# Default-deny: only paths matching packaging.allowlist ship. Structural
# excludes (per-skill SKILL.md, __pycache__, etc.) live inside the filter.
python3 "$ROOT/scripts/packaging_filter.py" "$ROOT/packaging.allowlist" \
  < "$MANIFEST" > "$FILTERED_MANIFEST"

tar -cf - -T "$FILTERED_MANIFEST" | (cd "$STAGE" && tar -xf -)

# Shipped reference files resolve runtime paths from the package root, just
# like the generated root dispatcher. Qualify each skill-relative path before
# the archive is built, including references loaded after the first hop.
find "$STAGE/skills" -type f -name '*.md' -print0 |
  while IFS= read -r -d '' markdown; do
    relative="${markdown#"$STAGE/skills/"}"
    skill="${relative%%/*}"
    skill_relative="${relative#"$skill/"}"
    python3 "$ROOT/scripts/validate_package.py" \
      --rewrite-skill-paths "$skill" \
      --skill-root "$ROOT/skills/$skill" \
      --source-relative "$skill_relative" \
      --rewrite-file "$markdown"
  done

# Dispatcher body is codegen output: scripts/dispatcher.md. Source of truth is
# scripts/dispatcher-template.md plus SKILL.md frontmatter; regenerate with
# `make regenerate` if the template or any dispatch_intent changes.
if [ ! -f "$ROOT/scripts/dispatcher.md" ]; then
  echo "ERROR: scripts/dispatcher.md missing; run 'make regenerate' first" >&2
  exit 1
fi
cp "$ROOT/scripts/dispatcher.md" "$STAGE/SKILL.md"

find skills -mindepth 2 -maxdepth 2 -name SKILL.md | sort | while IFS= read -r path; do
  skill="$(basename "$(dirname "$path")")"
  {
    printf '\n---\n\n# SKILL: %s\n\n' "$skill"
    awk 'BEGIN{skip=0} /^---$/{if(NR==1){skip=1;next} if(skip){skip=0;next}} !skip' "$path"
  } | python3 "$ROOT/scripts/validate_package.py" \
    --rewrite-skill-paths "$skill" \
    --skill-root "$ROOT/skills/$skill" \
    --source-relative "SKILL.md" >> "$STAGE/SKILL.md"
done

perl -0pi -e 's#`skills/([a-z][a-z0-9_-]*)/SKILL\.md`#the **$1** section below#g' "$STAGE/SKILL.md"
find "$STAGE/skills" -type d -empty -delete 2>/dev/null || true

(cd "$STAGE" && find . -type f | sed 's#^\./##' | sort | zip -q "$OUT" -@)

if ! zipinfo -1 "$OUT" | awk '$0 == "SKILL.md" { found = 1 } END { exit found ? 0 : 1 }'; then
  echo "ERROR: root SKILL.md missing from $OUT" >&2
  exit 1
fi

SKILL_COUNT="$(zipinfo -1 "$OUT" | awk '$0 ~ /(^|\/)SKILL\.md$/ { count++ } END { print count + 0 }')"
if [ "$SKILL_COUNT" -ne 1 ]; then
  echo "ERROR: expected exactly one SKILL.md in $OUT, found $SKILL_COUNT" >&2
  exit 1
fi

SIZE=$(wc -c < "$OUT" | tr -d ' ')
echo "OK: wrote $OUT (${SIZE} bytes)"

# Post-package validation lives in scripts/validate_package.py so it's
# py_compile-checked in CI and unit-testable.
unzip -q "$OUT" -d "$VALIDATE_DIR"
python3 "$ROOT/scripts/validate_package.py" "$VALIDATE_DIR"
