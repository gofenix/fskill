#!/usr/bin/env bash
# Failure-path smokes for the build/routing validators that otherwise only run
# their happy path (via `make package` / `make verify-routing`):
#   - scripts/validate_package.py   (post-package straggler + section checks)
#   - scripts/packaging_filter.py   (default-deny allowlist + structural excludes)
#   - scripts/check_routing_drift.py (stale RESOLVER.md refs)
# Each case forces the validator to reject bad input so a regression in the
# guard surfaces here instead of silently shipping.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

NINJA="Prefix your first line with 🥷 inline, not as its own paragraph."
SKILLS="think ui check hunt write learn read health"

# --- validate_package.py -----------------------------------------------------
stage=$(make_tmpdir)
{
  printf '%s\n' "$NINJA"
  for s in $SKILLS; do
    printf '\n# SKILL: %s\n\nbody for %s\n' "$s" "$s"
  done
} > "$stage/SKILL.md"

# Clean stage passes.
python3 "$ROOT/scripts/validate_package.py" "$stage" >/dev/null
echo "  validate_package clean stage: ok"

# A leaked nested ref for a skill OTHER than check/think must be rejected.
# Pre-fix this probed only ("check","think") and let skills/read/SKILL.md slip.
cp "$stage/SKILL.md" "$stage/SKILL.leak.md"
printf '\nsee skills/read/SKILL.md for details\n' >> "$stage/SKILL.leak.md"
leak_stage=$(make_tmpdir)
cp "$stage/SKILL.leak.md" "$leak_stage/SKILL.md"
if python3 "$ROOT/scripts/validate_package.py" "$leak_stage" >/dev/null 2>"$leak_stage/err"; then
  echo "FAIL: validate_package accepted leaked skills/read/SKILL.md ref" >&2
  exit 1
fi
grep -q "nested" "$leak_stage/err" || {
  echo "FAIL: validate_package failed for the wrong reason:" >&2
  cat "$leak_stage/err" >&2
  exit 1
}
echo "  validate_package straggler (read): ok"

# --- packaging_filter.py -----------------------------------------------------
flt=$(make_tmpdir)
cat > "$flt/allow.txt" <<'TXT'
# default-deny allowlist fixture
skills/**
rules/anti-patterns.md
README.md
TXT

out=$(printf '%s\n' \
  "skills/check/SKILL.md" \
  "skills/check/scripts/audit_signals.py" \
  "skills/check/__pycache__/x.pyc" \
  "rules/anti-patterns.md" \
  "README.md" \
  "secret.env" \
  "build/x.pyc" \
  ".DS_Store" \
  | python3 "$ROOT/scripts/packaging_filter.py" "$flt/allow.txt")

assert_filtered() { # label, needle, want-present(1)/absent(0)
  if printf '%s\n' "$out" | grep -qxF "$2"; then present=1; else present=0; fi
  if [ "$present" -ne "$3" ]; then
    echo "FAIL: packaging_filter $1 (got present=$present want=$3) for '$2'" >&2
    echo "filter output was:" >&2; printf '%s\n' "$out" >&2
    exit 1
  fi
}
assert_filtered "allows nested script" "skills/check/scripts/audit_signals.py" 1
assert_filtered "allows exact rule"    "rules/anti-patterns.md"                1
assert_filtered "allows README"        "README.md"                            1
assert_filtered "excludes per-skill SKILL.md" "skills/check/SKILL.md"         0
assert_filtered "excludes __pycache__/.pyc"   "skills/check/__pycache__/x.pyc" 0
assert_filtered "default-deny unmatched"      "secret.env"                    0
assert_filtered "excludes .pyc"               "build/x.pyc"                   0
assert_filtered "excludes .DS_Store"          ".DS_Store"                     0
echo "  packaging_filter default-deny + excludes: ok"

# --- check_routing_drift.py --------------------------------------------------
drift=$(make_tmpdir)
copy_repo "$drift"
# Clean copy is consistent (guards against a broken fixture).
python3 "$ROOT/scripts/check_routing_drift.py" --root "$drift" >/dev/null
# A skill name in RESOLVER.md with no skills/<name>/ directory is stale drift.
printf '\n<!-- fixture --> skills/ghostskill/SKILL.md\n' >> "$drift/skills/RESOLVER.md"
if python3 "$ROOT/scripts/check_routing_drift.py" --root "$drift" >/dev/null 2>"$drift/err"; then
  echo "FAIL: check_routing_drift accepted stale RESOLVER.md ref" >&2
  exit 1
fi
grep -q "stale skill refs in RESOLVER.md" "$drift/err" || {
  echo "FAIL: check_routing_drift failed for the wrong reason:" >&2
  cat "$drift/err" >&2
  exit 1
}
echo "  check_routing_drift stale resolver: ok"

echo "validators smoke: ok"
