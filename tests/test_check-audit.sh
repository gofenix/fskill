#!/usr/bin/env bash
# Smoke for skills/check/scripts/audit_signals.py.
# Builds a clean fixture (all PASS) and a dirty fixture (WARN/FAIL on the
# targeted blocks), runs the auditor against each, and greps for the
# expected status lines next to their headers.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

AUDIT="$ROOT/skills/check/scripts/audit_signals.py"

# Helper: check that the line right after `=== <block> ===` (one or more
# lines down) has the expected status. Looks for `status: <expected>` within
# the block (until the next === header).
assert_block_status() {
  local out="$1" block="$2" expected="$3"
  awk -v block="=== ${block} ===" -v expected="status: ${expected}" '
    $0 == block { in_block = 1; next }
    in_block && /^=== / { in_block = 0 }
    in_block && $0 == expected { found = 1 }
    END { exit found ? 0 : 1 }
  ' "$out" || {
    echo "FAIL: expected '$block' status=$expected; got:" >&2
    awk -v block="=== ${block} ===" '
      $0 == block { in_block = 1; print; next }
      in_block && /^=== / { exit }
      in_block { print }
    ' "$out" >&2
    return 1
  }
}

# Case 1: clean fixture -- everything PASS.
clean=$(make_tmpdir)
mkdir -p "$clean/.github/workflows" "$clean/tests" "$clean/src"
echo "1.0.0" > "$clean/VERSION"
cat > "$clean/.github/workflows/test.yml" <<'YAML'
name: test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
YAML
echo "print('hi')" > "$clean/src/main.py"
echo "def test_one(): pass" > "$clean/tests/test_main.py"
echo "# project" > "$clean/AGENTS.md"

clean_out="$clean/audit.out"
python3 "$AUDIT" --root "$clean" > "$clean_out"

assert_block_status "$clean_out" "FILE SIZE HOTSPOTS" "PASS"
assert_block_status "$clean_out" "HEREDOC BLOAT" "PASS"
assert_block_status "$clean_out" "TEST AND CI SURFACE" "PASS"
assert_block_status "$clean_out" "VERSION SOURCE COUNT" "PASS"
assert_block_status "$clean_out" "INSTALL URL PINNING" "PASS"
assert_block_status "$clean_out" "AGENT DOC DEDUP" "PASS"
assert_block_status "$clean_out" "DRIFT MARKERS" "PASS"
# Surfaces absent in the clean fixture -> N/A (not PASS).
assert_block_status "$clean_out" "PACKAGING FILTER POSTURE" "N/A"
assert_block_status "$clean_out" "CLI CONTRACT SURFACE" "N/A"
assert_block_status "$clean_out" "DUPLICATE SETUP SCRIPTS" "N/A"
assert_block_status "$clean_out" "DENYLIST IN BUILD" "N/A"

# Case 2: dirty fixture -- targeted WARN/FAIL.
dirty=$(make_tmpdir)
mkdir -p "$dirty/src" "$dirty/scripts"

# Two version sources with conflicting values -> VERSION SOURCE WARN
echo "1.0.0" > "$dirty/VERSION"
cat > "$dirty/package.json" <<'JSON'
{ "name": "x", "version": "9.9.9" }
JSON

# README install URL pinned to main -> INSTALL URL PINNING WARN
cat > "$dirty/README.md" <<'MD'
# x
Install: curl https://raw.githubusercontent.com/u/r/main/setup.sh | bash
MD

# Both CLAUDE.md and AGENTS.md, non-symlink, identical content -> WARN
echo "# guide" > "$dirty/AGENTS.md"
echo "# guide" > "$dirty/CLAUDE.md"

# Two large source files (>500 lines) -> FILE SIZE HOTSPOTS WARN
python3 -c "print('# big', *['line_'+str(i) for i in range(700)], sep='\n')" \
  > "$dirty/src/big_one.py"
python3 -c "print('# big', *['line_'+str(i) for i in range(900)], sep='\n')" \
  > "$dirty/src/big_two.py"

# Python heredoc >100 lines in a shell script -> HEREDOC BLOAT WARN
{
  echo '#!/bin/bash'
  echo "python3 - <""<'PY'"
  for _ in $(seq 1 130); do echo "x = 1"; done
  echo 'PY'
} > "$dirty/scripts/run.sh"

# Packaging script using denylist patterns + no allowlist -> PACKAGING WARN
cat > "$dirty/scripts/package.sh" <<'SH'
#!/bin/bash
tar --exclude=*.log -czf out.tgz src/
grep -v node_modules manifest.txt > manifest.filtered
SH

# No CI workflows, no tests -> TEST AND CI SURFACE FAIL
# (we intentionally do NOT create .github/workflows or tests/)

# Two near-duplicate setup scripts -> DUPLICATE SETUP SCRIPTS WARN
cat > "$dirty/scripts/setup-foo.sh" <<'SH'
#!/bin/bash
set -e
echo "setting up foo"
mkdir -p ~/.foo
touch ~/.foo/installed
SH
cp "$dirty/scripts/setup-foo.sh" "$dirty/scripts/setup-bar.sh"

dirty_out="$dirty/audit.out"
python3 "$AUDIT" --root "$dirty" > "$dirty_out"

assert_block_status "$dirty_out" "FILE SIZE HOTSPOTS" "WARN"
assert_block_status "$dirty_out" "HEREDOC BLOAT" "WARN"
assert_block_status "$dirty_out" "TEST AND CI SURFACE" "FAIL"
assert_block_status "$dirty_out" "VERSION SOURCE COUNT" "WARN"
assert_block_status "$dirty_out" "PACKAGING FILTER POSTURE" "WARN"
assert_block_status "$dirty_out" "CLI CONTRACT SURFACE" "N/A"
assert_block_status "$dirty_out" "INSTALL URL PINNING" "WARN"
assert_block_status "$dirty_out" "AGENT DOC DEDUP" "WARN"
assert_block_status "$dirty_out" "DUPLICATE SETUP SCRIPTS" "WARN"

# Case 3: CLI entrypoint without contract coverage -> WARN.
cli_warn=$(make_tmpdir)
mkdir -p "$cli_warn/bin" "$cli_warn/src"
cat > "$cli_warn/bin/examplecli" <<'SH'
#!/usr/bin/env bash
echo run
SH
chmod +x "$cli_warn/bin/examplecli"
echo "print('lib')" > "$cli_warn/src/lib.py"

cli_warn_out="$cli_warn/audit.out"
python3 "$AUDIT" --root "$cli_warn" > "$cli_warn_out"
assert_block_status "$cli_warn_out" "CLI CONTRACT SURFACE" "WARN"

# Case 4: CLI entrypoint with only partial contract coverage -> WARN.
cli_partial=$(make_tmpdir)
mkdir -p "$cli_partial/bin"
cat > "$cli_partial/bin/examplecli" <<'SH'
#!/usr/bin/env bash
echo usage: examplecli
SH
chmod +x "$cli_partial/bin/examplecli"
cat > "$cli_partial/README.md" <<'MD'
# ExampleCLI

Usage: examplecli --help
MD

cli_partial_out="$cli_partial/audit.out"
python3 "$AUDIT" --root "$cli_partial" > "$cli_partial_out"
assert_block_status "$cli_partial_out" "CLI CONTRACT SURFACE" "WARN"

# Case 5: CLI entrypoint with help/version/stream/exit/install evidence -> PASS.
cli_pass=$(make_tmpdir)
mkdir -p "$cli_pass/bin" "$cli_pass/tests" "$cli_pass/.github/workflows"
cat > "$cli_pass/bin/examplecli" <<'SH'
#!/usr/bin/env bash
case "${1:-}" in
  --help) echo "usage: examplecli";;
  --version) echo "examplecli 1.0.0";;
  *) echo "run";;
esac
SH
chmod +x "$cli_pass/bin/examplecli"
cat > "$cli_pass/tests/test_cli.sh" <<'SH'
#!/usr/bin/env bash
set -e
tmpdir="$(mktemp -d)"
install -m 755 bin/examplecli "$tmpdir/examplecli"
PATH="$tmpdir:$PATH" examplecli --help >"$tmpdir/help.stdout" 2>"$tmpdir/help.stderr"
exit_code=$?
test "$exit_code" -eq 0
grep -q "usage:" "$tmpdir/help.stdout"
test ! -s "$tmpdir/help.stderr"
CI=1 PATH="$tmpdir:$PATH" examplecli --version >"$tmpdir/version.stdout" 2>"$tmpdir/version.stderr" </dev/null
grep -q "1.0.0" "$tmpdir/version.stdout"
SH
cat > "$cli_pass/.github/workflows/test.yml" <<'YAML'
name: test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: bash tests/test_cli.sh
YAML

cli_pass_out="$cli_pass/audit.out"
python3 "$AUDIT" --root "$cli_pass" > "$cli_pass_out"
assert_block_status "$cli_pass_out" "CLI CONTRACT SURFACE" "PASS"

# Script exits 0 even when findings surface (it's a reporter, not a gate).
python3 "$AUDIT" --root "$dirty" >/dev/null

# Case 6: report-only audit must not execute Git fsmonitor hooks or follow
# repository-controlled symlinks outside the audited root.
guarded=$(make_tmpdir)
printf '%s\n' '# safe' > "$guarded/README.md"
(cd "$guarded" && git init -q && git add README.md && git \
  -c user.name=waza -c user.email=waza@test commit -qm init)
fsmonitor_marker="$guarded-fsmonitor.executed"
fsmonitor_hook="$guarded/fsmonitor.sh"
printf '%s\n' \
  '#!/bin/sh' \
  "printf executed > '$fsmonitor_marker'" \
  'exit 0' \
  > "$fsmonitor_hook"
chmod +x "$fsmonitor_hook"
git -C "$guarded" config core.fsmonitor "$fsmonitor_hook"
outside_audit="$guarded-outside.md"
printf '%s\n' '# PRIVATE_AUDIT_TOKEN' '<!-- TODO -->' > "$outside_audit"
ln -s "$outside_audit" "$guarded/private-audit.md"
guarded_out="$guarded/audit.out"
python3 "$AUDIT" --root "$guarded" > "$guarded_out"
test ! -e "$fsmonitor_marker" || {
  echo "audit_signals executed the target repository fsmonitor hook"; exit 1
}
if grep -qE 'PRIVATE_AUDIT_TOKEN|private-audit.md' "$guarded_out"; then
  echo "audit_signals followed a repository-controlled symlink"; exit 1
fi

echo "check audit smoke: ok"
