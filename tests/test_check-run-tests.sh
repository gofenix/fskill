#!/usr/bin/env bash
# Behavioral smoke for check's run-tests.sh: detects a Makefile test target in
# the current working directory, and fails cleanly when no verification
# command exists (the skill treats that exit as "ask the user").
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

tmpdir=$(make_tmpdir)

proj="$tmpdir/proj-make"
mkdir -p "$proj"
printf 'test:\n\t@echo fixture-tests-ok\n' > "$proj/Makefile"
out=$(cd "$proj" && bash "$ROOT/skills/check/scripts/run-tests.sh")
case "$out" in
  *fixture-tests-ok*) ;;
  *)
    echo "run-tests smoke: expected Makefile test target to run, got: $out"
    exit 1
    ;;
esac

empty="$tmpdir/proj-empty"
mkdir -p "$empty"
if out=$(cd "$empty" && bash "$ROOT/skills/check/scripts/run-tests.sh" 2>&1); then
  echo "run-tests smoke: empty project should exit non-zero"
  exit 1
fi
case "$out" in
  *"no test command detected"*) ;;
  *)
    echo "run-tests smoke: expected no-test-command message, got: $out"
    exit 1
    ;;
esac

echo "run-tests smoke: ok"
