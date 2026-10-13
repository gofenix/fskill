#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

CHECKER="$ROOT/skills/health/scripts/check-maintainability.sh"

tmpdir=$(make_tmpdir)

# write_standard_agents_md comes from test_helpers.sh.
write_real_makefile() {
  printf 'test:\n\t@test -s AGENTS.md\n' > "$1"
}

# Case 1: clean project -> PASS, verification PASS.
good="$tmpdir/good"
mkdir -p "$good/.github/workflows" "$good/docs" "$good/src"
write_standard_agents_md "$good/AGENTS.md"
write_real_makefile "$good/Makefile"
printf '%s\n' \
  'name: ci' \
  'on: [push]' \
  'jobs:' \
  '  test:' \
  '    runs-on: ubuntu-latest' \
  '    steps:' \
  '      - run: make test' \
  > "$good/.github/workflows/test.yml"
printf '%s\n' 'export function ok() { return true }' > "$good/src/app.ts"
bash "$CHECKER" "$good" summary >"$tmpdir/good.out"
grep -q '^maintainability_status: PASS$' "$tmpdir/good.out"
grep -q '^verification_status: PASS$' "$tmpdir/good.out"

# Case 2: implementation with no verifier -> FAIL, while size and a missing
# instruction surface remain inventory rather than independent findings.
bad="$tmpdir/bad"
mkdir -p "$bad/src"
ROOT_BAD="$bad" python3 -c "
import os
from pathlib import Path
p = Path(os.environ['ROOT_BAD']) / 'src/huge.ts'
p.write_text('\n'.join(f'const item{i} = {i}; // TODO fix' for i in range(1300)) + '\n')
"
bash "$CHECKER" "$bad" summary >"$tmpdir/bad.out"
grep -q '^maintainability_status: FAIL$' "$tmpdir/bad.out"
grep -q '^context_status: UNKNOWN$' "$tmpdir/bad.out"
grep -q 'no substantive verifier evidence discovered' "$tmpdir/bad.out"
grep -q 'src/huge.ts' "$tmpdir/bad.out"
if grep -qE 'no agent instruction surface|hotspot_ownership' "$tmpdir/bad.out"; then
  echo "repository shape must not become a maintainability finding"; exit 1
fi

# Case 3: huge files inside excluded dirs (node_modules / dist / build) must
# not surface in summary or deep output.
excluded="$tmpdir/excluded"
mkdir -p "$excluded/src" "$excluded/node_modules/pkg" "$excluded/dist" "$excluded/build"
write_standard_agents_md "$excluded/AGENTS.md" "Avoid generated directories."
write_real_makefile "$excluded/Makefile"
printf '%s\n' 'export const ok = true;' > "$excluded/src/app.ts"
ROOT_EXC="$excluded" python3 -c "
import os
from pathlib import Path
root = Path(os.environ['ROOT_EXC'])
for path, n in [('node_modules/pkg/big.js', 2000), ('dist/out.js', 2000), ('build/big.py', 2000)]:
    (root / path).write_text('\n'.join('x' for _ in range(n)) + '\n')
"
bash "$CHECKER" "$excluded" summary >"$tmpdir/excluded.out"
if grep -qE 'node_modules|dist/out.js|build/big.py' "$tmpdir/excluded.out"; then
  echo "maintainability smoke should exclude generated/dependency directories"; exit 1
fi
bash "$CHECKER" "$excluded" deep >"$tmpdir/excluded-deep.out"
if grep -qE 'node_modules|dist/out.js|build/big.py' "$tmpdir/excluded-deep.out"; then
  echo "maintainability smoke should exclude generated/dependency directories"; exit 1
fi

# Case 4: a large file is inventory and remains PASS when a verifier exists.
hotspot_good="$tmpdir/hotspot-good"
mkdir -p "$hotspot_good/src"
printf '%s\n' \
  '## Project' \
  'Repository Map: src contains runtime code.' \
  '## Verification' \
  'Run `make test` before handoff.' \
  '## Boundaries' \
  'Do not rewrite unrelated modules.' \
  '## Hotspot Ownership' \
  '- `src/hotspot.ts`: owned runtime hotspot. Keep the module boundary stable and run `make test` after changes.' \
  > "$hotspot_good/AGENTS.md"
write_real_makefile "$hotspot_good/Makefile"
ROOT_HG="$hotspot_good" python3 -c "
import os
from pathlib import Path
p = Path(os.environ['ROOT_HG']) / 'src/hotspot.ts'
p.write_text('\n'.join(f'export const item{i} = {i};' for i in range(1300)) + '\n')
"
bash "$CHECKER" "$hotspot_good" deep >"$tmpdir/hotspot-good.out"
grep -q '^maintainability_status: PASS$' "$tmpdir/hotspot-good.out"
bash "$CHECKER" "$hotspot_good" summary >"$tmpdir/hotspot-good-summary.out"
grep -q '^maintainability_status: PASS$' "$tmpdir/hotspot-good-summary.out"
grep -q 'src/hotspot.ts lines=1300' "$tmpdir/hotspot-good-summary.out"
if grep -q 'hotspot_ownership' "$tmpdir/hotspot-good-summary.out"; then
  echo "large files must not require a hotspot ownership map"; exit 1
fi

# Case 5: an undocumented large file does not warn by size alone.
hotspot_bad="$tmpdir/hotspot-bad"
mkdir -p "$hotspot_bad/src"
write_standard_agents_md "$hotspot_bad/AGENTS.md"
write_real_makefile "$hotspot_bad/Makefile"
ROOT_HB="$hotspot_bad" python3 -c "
import os
from pathlib import Path
p = Path(os.environ['ROOT_HB']) / 'src/huge.ts'
p.write_text('\n'.join(f'export const item{i} = {i};' for i in range(900)) + '\n')
"
bash "$CHECKER" "$hotspot_bad" deep >"$tmpdir/hotspot-bad.out"
grep -q '^maintainability_status: PASS$' "$tmpdir/hotspot-bad.out"
grep -q 'src/huge.ts' "$tmpdir/hotspot-bad.out"

# Case 6: verification guidance need not sit beside every large-file mention.
hotspot_missing_test="$tmpdir/hotspot-missing-test"
mkdir -p "$hotspot_missing_test/src"
printf '%s\n' \
  '## Project' \
  'Repository Map: src contains runtime code.' \
  '## Verification' \
  'Run `make test` before handoff.' \
  '## Boundaries' \
  'Do not rewrite unrelated modules.' \
  '## Hotspot Ownership' \
  '- `src/hotspot.ts`: owned runtime hotspot. Keep the module boundary stable.' \
  > "$hotspot_missing_test/AGENTS.md"
write_real_makefile "$hotspot_missing_test/Makefile"
ROOT_HM="$hotspot_missing_test" python3 -c "
import os
from pathlib import Path
p = Path(os.environ['ROOT_HM']) / 'src/hotspot.ts'
p.write_text('\n'.join(f'export const item{i} = {i};' for i in range(900)) + '\n')
"
bash "$CHECKER" "$hotspot_missing_test" deep >"$tmpdir/hotspot-missing-test.out"
grep -q '^maintainability_status: PASS$' "$tmpdir/hotspot-missing-test.out"

# Case 7: multiple verification commands but no Makefile test/check/verify wrapper.
wrapper="$tmpdir/wrapper"
mkdir -p "$wrapper/.github/workflows" "$wrapper/scripts"
printf '%s\n' \
  '## Project' \
  'Repository Map: scripts contains verification.' \
  '## Verification' \
  'Run `./scripts/check.sh --no-format`.' \
  '## Boundaries' \
  'Keep checks non-mutating.' \
  > "$wrapper/AGENTS.md"
printf 'build:\n\t@test -s AGENTS.md\n' > "$wrapper/Makefile"
printf '%s\n' '#!/bin/bash' 'set -euo pipefail' 'test -s AGENTS.md' > "$wrapper/scripts/check.sh"
printf '%s\n' \
  'name: check' \
  'on: [push]' \
  'jobs:' \
  '  check:' \
  '    runs-on: ubuntu-latest' \
  '    steps:' \
  '      - run: ./scripts/check.sh --no-format' \
  > "$wrapper/.github/workflows/check.yml"
bash "$CHECKER" "$wrapper" summary >"$tmpdir/wrapper.out"
grep -q '^verification_status: PASS$' "$tmpdir/wrapper.out"
grep -A8 '^verifier_evidence:$' "$tmpdir/wrapper.out" | grep -q './scripts/check.sh --no-format'
grep -q '^wrapper_status: WARN$' "$tmpdir/wrapper.out"
grep -q 'check documented or native entrypoints before recommending a wrapper' "$tmpdir/wrapper.out"

# Case 8: broken markdown link in deep mode -> WARN with named source.
links="$tmpdir/links"
mkdir -p "$links"
printf '%s\n' \
  '## Project' \
  'Repository Map: root docs.' \
  '## Verification' \
  'Run `make test`.' \
  '## Boundaries' \
  'Keep docs valid.' \
  > "$links/AGENTS.md"
write_real_makefile "$links/Makefile"
printf '%s\n' 'See [safe remove](journal/2026-03-11-safe-remove-design.md).' > "$links/SECURITY_AUDIT.md"
bash "$CHECKER" "$links" deep >"$tmpdir/links.out"
grep -q '^markdown_link_status: WARN$' "$tmpdir/links.out"
grep -q 'SECURITY_AUDIT.md:1 -> journal/2026-03-11-safe-remove-design.md' "$tmpdir/links.out"

# Case 9: inside a git repo, untracked source files are still part of the review
# surface. A local review must not go blind just because a new file has not been
# staged yet.
untracked="$tmpdir/untracked"
mkdir -p "$untracked/src"
write_standard_agents_md "$untracked/AGENTS.md"
write_real_makefile "$untracked/Makefile"
(cd "$untracked" && git init -q && git add AGENTS.md Makefile)
ROOT_UT="$untracked" python3 -c "
import os
from pathlib import Path
p = Path(os.environ['ROOT_UT']) / 'src/new_hotspot.ts'
p.write_text('\n'.join(f'export const item{i} = {i};' for i in range(1300)) + '\n')
"
bash "$CHECKER" "$untracked" summary >"$tmpdir/untracked.out"
grep -q 'src/new_hotspot.ts' "$tmpdir/untracked.out"

# Case 10: site-root links are routes, not local filesystem references.
routes="$tmpdir/routes"
mkdir -p "$routes"
write_standard_agents_md "$routes/AGENTS.md"
write_real_makefile "$routes/Makefile"
printf '%s\n' 'See [中文博客](/zh/blog/example).' > "$routes/README.md"
bash "$CHECKER" "$routes" deep >"$tmpdir/routes.out"
grep -q '^markdown_link_status: PASS$' "$tmpdir/routes.out"

# Case 11: large source and test files remain inventory, not ownership findings.
hotspot_dir="$tmpdir/hotspot-dir"
mkdir -p "$hotspot_dir/src/updaters" "$hotspot_dir/tests"
printf '%s\n' \
  '## Project' \
  'Repository Map: src contains runtime code.' \
  '## Verification' \
  'Run `make test` before handoff.' \
  '## Boundaries' \
  'Do not rewrite unrelated modules.' \
  '## Hotspot Ownership' \
  '- `src/updaters/`: owns update execution boundaries. Run `make test` after changes.' \
  > "$hotspot_dir/AGENTS.md"
write_real_makefile "$hotspot_dir/Makefile"
ROOT_HD="$hotspot_dir" python3 -c "
import os
from pathlib import Path
root = Path(os.environ['ROOT_HD'])
(root / 'src/updaters/large.ts').write_text('\\n'.join('export const x = 1;' for _ in range(900)) + '\\n')
(root / 'tests/large_test.ts').write_text('\\n'.join('assert(true);' for _ in range(900)) + '\\n')
"
bash "$CHECKER" "$hotspot_dir" deep >"$tmpdir/hotspot-dir.out"
grep -q '^maintainability_status: PASS$' "$tmpdir/hotspot-dir.out"

# Case 12: same-basename files do not create inferred ownership findings.
hotspot_collision="$tmpdir/hotspot-collision"
mkdir -p "$hotspot_collision/src" "$hotspot_collision/tools"
printf '%s\n' \
  '## Project' \
  'Repository Map: src and tools contain separate runtime modules.' \
  '## Verification' \
  'Run `make test` before handoff.' \
  '## Boundaries' \
  'Do not treat same-basename files as the same module.' \
  '## Hotspot Ownership' \
  '- `tools/main.py`: owned tooling hotspot. Run `make test` after changes.' \
  > "$hotspot_collision/AGENTS.md"
write_real_makefile "$hotspot_collision/Makefile"
ROOT_HC="$hotspot_collision" python3 -c "
import os
from pathlib import Path
p = Path(os.environ['ROOT_HC']) / 'src/main.py'
p.write_text('\\n'.join(f'item_{i} = {i}' for i in range(900)) + '\\n')
"
bash "$CHECKER" "$hotspot_collision" deep >"$tmpdir/hotspot-collision.out"
grep -q '^maintainability_status: PASS$' "$tmpdir/hotspot-collision.out"

# Case 13: report-only file discovery must not execute Git fsmonitor hooks or
# follow repository-controlled symlinks outside the audited project.
guarded="$tmpdir/guarded"
mkdir -p "$guarded"
write_standard_agents_md "$guarded/AGENTS.md"
write_real_makefile "$guarded/Makefile"
(cd "$guarded" && git init -q && git add AGENTS.md Makefile && git \
  -c user.name=waza -c user.email=waza@test commit -qm init)
fsmonitor_marker="$tmpdir/maintainability-fsmonitor.executed"
fsmonitor_hook="$guarded/fsmonitor.sh"
printf '%s\n' \
  '#!/bin/sh' \
  "printf executed > '$fsmonitor_marker'" \
  'exit 0' \
  > "$fsmonitor_hook"
chmod +x "$fsmonitor_hook"
git -C "$guarded" config core.fsmonitor "$fsmonitor_hook"
outside_source="$tmpdir/private-maintainability.md"
printf '%s\n' '# PRIVATE_MAINTAINABILITY_TOKEN' '<!-- TODO -->' > "$outside_source"
ln -s "$outside_source" "$guarded/private-maintainability.md"
bash "$CHECKER" "$guarded" deep >"$tmpdir/guarded.out"
test ! -e "$fsmonitor_marker" || {
  echo "maintainability audit executed the target repository fsmonitor hook"; exit 1
}
if grep -qE 'PRIVATE_MAINTAINABILITY_TOKEN|private-maintainability.md' "$tmpdir/guarded.out"; then
  echo "maintainability audit followed a repository-controlled symlink"; exit 1
fi

# Case 14: a Markdown link may target a symlink whose final target remains
# inside the repository. This is the normal AGENTS.md / CLAUDE.md setup.
doc_symlink="$tmpdir/doc-symlink"
mkdir -p "$doc_symlink"
write_standard_agents_md "$doc_symlink/AGENTS.md"
ln -s AGENTS.md "$doc_symlink/CLAUDE.md"
write_real_makefile "$doc_symlink/Makefile"
printf '%s\n' 'See [Claude instructions](CLAUDE.md).' > "$doc_symlink/README.md"
bash "$CHECKER" "$doc_symlink" deep >"$tmpdir/doc-symlink.out"
grep -q '^markdown_link_status: PASS$' "$tmpdir/doc-symlink.out"

# Case 15: generated plugin mirrors are one logical maintenance surface, and
# fixture/documentation marker examples are not implementation debt.
mirrors="$tmpdir/mirrors"
mkdir -p "$mirrors/skills/demo" "$mirrors/plugins/waza/skills/demo" "$mirrors/tests"
write_standard_agents_md "$mirrors/AGENTS.md"
write_real_makefile "$mirrors/Makefile"
printf '%s\n' '# Demo' 'TODO is a documented placeholder example.' > "$mirrors/skills/demo/SKILL.md"
cp "$mirrors/skills/demo/SKILL.md" "$mirrors/plugins/waza/skills/demo/SKILL.md"
printf '%s\n' '# TODO fixture' > "$mirrors/tests/test_fixture.py"
bash "$CHECKER" "$mirrors" deep >"$tmpdir/mirrors.out"
grep -q '^generated_mirror_files_collapsed: 1$' "$tmpdir/mirrors.out"
grep -q '^generated_mirror_files_drifted: 0$' "$tmpdir/mirrors.out"
grep -q '^generated_mirror_comparison_gaps: 0$' "$tmpdir/mirrors.out"
grep -q '^todo_markers: 0$' "$tmpdir/mirrors.out"
grep -q '^fixture_or_instruction_marker_lines_ignored: 2$' "$tmpdir/mirrors.out"

# Case 16: mirror comparison must read the complete file. Generated files that
# share a large prefix but differ after the text-audit limit remain separate.
large_mirrors="$tmpdir/large-mirrors"
mkdir -p "$large_mirrors/skills/demo" "$large_mirrors/plugins/waza/skills/demo"
write_standard_agents_md "$large_mirrors/AGENTS.md"
write_real_makefile "$large_mirrors/Makefile"
ROOT_LM="$large_mirrors" python3 -c "
import os
from pathlib import Path
root = Path(os.environ['ROOT_LM'])
prefix = b'x' * 2_000_000
(root / 'skills/demo/SKILL.md').write_bytes(prefix + b'source')
(root / 'plugins/waza/skills/demo/SKILL.md').write_bytes(prefix + b'mirror')
"
bash "$CHECKER" "$large_mirrors" deep >"$tmpdir/large-mirrors.out"
grep -q '^generated_mirror_files_collapsed: 0$' "$tmpdir/large-mirrors.out"
grep -q '^generated_mirror_files_drifted: 1$' "$tmpdir/large-mirrors.out"
grep -q '^drift_status: WARN$' "$tmpdir/large-mirrors.out"

# Case 17: an oversized mirror comparison stays bounded and reports a gap.
huge_mirrors="$tmpdir/huge-mirrors"
mkdir -p "$huge_mirrors/skills/demo" "$huge_mirrors/plugins/waza/skills/demo"
write_standard_agents_md "$huge_mirrors/AGENTS.md"
write_real_makefile "$huge_mirrors/Makefile"
ROOT_HM="$huge_mirrors" python3 -c "
import os
from pathlib import Path
root = Path(os.environ['ROOT_HM'])
payload = b'x' * 16_000_001
(root / 'skills/demo/SKILL.md').write_bytes(payload)
(root / 'plugins/waza/skills/demo/SKILL.md').write_bytes(payload)
"
bash "$CHECKER" "$huge_mirrors" summary >"$tmpdir/huge-mirrors.out"
grep -q '^generated_mirror_files_collapsed: 0$' "$tmpdir/huge-mirrors.out"
grep -q '^generated_mirror_comparison_gaps: 1$' "$tmpdir/huge-mirrors.out"
grep -q '^drift_status: WARN$' "$tmpdir/huge-mirrors.out"

# Case 18: sibling file size does not create a documentation requirement.
hotspot_sibling="$tmpdir/hotspot-sibling"
mkdir -p "$hotspot_sibling/src/services"
cat > "$hotspot_sibling/AGENTS.md" <<'EOF'
## Project
Repository Map: src contains runtime code.
## Hotspot Ownership
- `src/services/owned.py`: owns the indexed path. Verify with `make test`.
## Verification
Run `make test` before handoff.
## Boundaries
Do not rewrite unrelated modules.
EOF
write_real_makefile "$hotspot_sibling/Makefile"
ROOT_HS="$hotspot_sibling" python3 -c "
import os
from pathlib import Path
root = Path(os.environ['ROOT_HS'])
for name in ('owned.py', 'unowned.py'):
    (root / 'src/services' / name).write_text('x = 1\\n' * 1300)
"
bash "$CHECKER" "$hotspot_sibling" summary >"$tmpdir/hotspot-sibling.out"
grep -q '^maintainability_status: PASS$' "$tmpdir/hotspot-sibling.out"
grep -q 'src/services/owned.py lines=1300' "$tmpdir/hotspot-sibling.out"
grep -q 'src/services/unowned.py lines=1300' "$tmpdir/hotspot-sibling.out"

# Case 19: real Markdown debt is counted while explicit marker examples stay
# informational.
markdown_debt="$tmpdir/markdown-debt"
mkdir -p "$markdown_debt/docs"
write_standard_agents_md "$markdown_debt/AGENTS.md"
write_real_makefile "$markdown_debt/Makefile"
printf '%s\n' 'TODO: rotate signing key before release.' > "$markdown_debt/docs/release.md"
bash "$CHECKER" "$markdown_debt" deep >"$tmpdir/markdown-debt.out"
grep -q '^todo_markers: 1$' "$tmpdir/markdown-debt.out"
grep -q 'docs/release.md markers=1' "$tmpdir/markdown-debt.out"
grep -q '^maintainability_status: PASS$' "$tmpdir/markdown-debt.out"

# Case 20: a docs-only repository may intentionally have no agent instructions,
# project map, skills, or executable verifier.
docs_only="$tmpdir/docs-only"
mkdir -p "$docs_only"
printf '%s\n' '# Notes' 'Stable prose only.' > "$docs_only/README.md"
bash "$CHECKER" "$docs_only" summary >"$tmpdir/docs-only.out"
grep -q '^maintainability_status: PASS$' "$tmpdir/docs-only.out"
grep -q '^context_status: NOT_APPLICABLE$' "$tmpdir/docs-only.out"
grep -q '^verification_status: PASS$' "$tmpdir/docs-only.out"
if grep -qE 'no agent instruction surface|project_map|hotspot_ownership' "$tmpdir/docs-only.out"; then
  echo "docs-only projects must not inherit fixed inventory requirements"; exit 1
fi

# Case 21: an implementation repo does not need a descriptive project map when
# its stable constraint and executable verifier are already discoverable.
no_map="$tmpdir/no-map"
mkdir -p "$no_map/src"
printf '%s\n' '# Rules' 'Do not publish without explicit authorization.' > "$no_map/AGENTS.md"
write_real_makefile "$no_map/Makefile"
printf '%s\n' 'export const ok = true;' > "$no_map/src/app.ts"
bash "$CHECKER" "$no_map" summary >"$tmpdir/no-map.out"
grep -q '^maintainability_status: PASS$' "$tmpdir/no-map.out"
if grep -q 'project_map' "$tmpdir/no-map.out"; then
  echo "a project map must not be a mechanical requirement"; exit 1
fi

# Case 22: a discovered command name is not verifier evidence when its target
# only prints. Inline recipes are common enough to cover explicitly.
hollow="$tmpdir/hollow"
mkdir -p "$hollow/src"
printf '%s\n' '# Rules' 'Do not publish without explicit authorization.' > "$hollow/AGENTS.md"
printf 'test:; @echo test\n' > "$hollow/Makefile"
printf '%s\n' 'export const ok = true;' > "$hollow/src/app.ts"
bash "$CHECKER" "$hollow" summary >"$tmpdir/hollow.out"
grep -q '^maintainability_status: FAIL$' "$tmpdir/hollow.out"
grep -q '^verification_status: FAIL$' "$tmpdir/hollow.out"
grep -A2 '^commands:$' "$tmpdir/hollow.out" | grep -q 'make test'
grep -A2 '^verifier_evidence:$' "$tmpdir/hollow.out" | grep -q '(none)'
grep -A2 '^hollow_verifiers:$' "$tmpdir/hollow.out" | grep -q 'make test'
grep -q 'discovered verifier entrypoints are hollow or non-substantive' "$tmpdir/hollow.out"

# Case 23: implementation plus a real verifier but no tracked instruction
# surface is UNKNOWN, not a fabricated clean context bill.
unknown_context="$tmpdir/unknown-context"
mkdir -p "$unknown_context/src"
printf 'test:\n\t@test -s src/app.ts\n' > "$unknown_context/Makefile"
printf '%s\n' 'export const ok = true;' > "$unknown_context/src/app.ts"
bash "$CHECKER" "$unknown_context" summary >"$tmpdir/unknown-context.out"
grep -q '^maintainability_status: WARN$' "$tmpdir/unknown-context.out"
grep -q '^context_status: UNKNOWN$' "$tmpdir/unknown-context.out"
grep -q '^verification_status: PASS$' "$tmpdir/unknown-context.out"
grep -q 'non-obvious project constraint reachability is unknown' "$tmpdir/unknown-context.out"

# Case 24: CI setup commands may be executable but are not verification. A
# dependency install that happens to name pytest must not manufacture evidence.
setup_only="$tmpdir/setup-only"
mkdir -p "$setup_only/.github/workflows" "$setup_only/src"
printf '%s\n' '# Rules' 'Do not publish without explicit authorization.' > "$setup_only/AGENTS.md"
printf '%s\n' 'export const ok = true;' > "$setup_only/src/app.ts"
printf '%s\n' \
  'name: setup' \
  'on: [push]' \
  'jobs:' \
  '  setup:' \
  '    runs-on: ubuntu-latest' \
  '    steps:' \
  '      - run: python3 -m pip install pytest' \
  > "$setup_only/.github/workflows/setup.yml"
bash "$CHECKER" "$setup_only" summary >"$tmpdir/setup-only.out"
grep -q '^maintainability_status: FAIL$' "$tmpdir/setup-only.out"
grep -q '^verification_status: FAIL$' "$tmpdir/setup-only.out"
grep -A2 '^verifier_evidence:$' "$tmpdir/setup-only.out" | grep -q '(none)'
grep -q 'none provide substantive verifier evidence' "$tmpdir/setup-only.out"

# Case 25: an empty instruction placeholder is presence inventory, not context
# evidence. It must not turn an implementation repository green.
empty_context="$tmpdir/empty-context"
mkdir -p "$empty_context/src"
: > "$empty_context/AGENTS.md"
printf 'test:\n\t@test -s src/app.ts\n' > "$empty_context/Makefile"
printf '%s\n' 'export const ok = true;' > "$empty_context/src/app.ts"
bash "$CHECKER" "$empty_context" summary >"$tmpdir/empty-context.out"
grep -q '^maintainability_status: WARN$' "$tmpdir/empty-context.out"
grep -q '^context_status: UNKNOWN$' "$tmpdir/empty-context.out"
grep -A2 '^instruction_files:$' "$tmpdir/empty-context.out" | grep -q 'AGENTS.md'
grep -A2 '^instruction_evidence_files:$' "$tmpdir/empty-context.out" | grep -q '(none)'

# Case 26: shell options, setup, and printing do not make a verifier wrapper
# substantive when no assertion/build/lint/test command ever runs.
hollow_script="$tmpdir/hollow-script"
mkdir -p "$hollow_script/src" "$hollow_script/scripts"
printf '%s\n' '# Rules' 'Do not publish without explicit authorization.' > "$hollow_script/AGENTS.md"
printf 'test:\n\t@./scripts/test.sh\n' > "$hollow_script/Makefile"
printf '%s\n' \
  '#!/usr/bin/env bash' \
  'set -euo pipefail # setup only' \
  'mkdir -p build' \
  'touch build/ready' \
  'echo ok' \
  > "$hollow_script/scripts/test.sh"
printf '%s\n' 'export const ok = true;' > "$hollow_script/src/app.ts"
bash "$CHECKER" "$hollow_script" summary >"$tmpdir/hollow-script.out"
grep -q '^maintainability_status: FAIL$' "$tmpdir/hollow-script.out"
grep -A2 '^verifier_evidence:$' "$tmpdir/hollow-script.out" | grep -q '(none)'
grep -A2 '^hollow_verifiers:$' "$tmpdir/hollow-script.out" | grep -q 'make test'

# Case 27: pyproject.toml alone does not prove that pytest is configured or
# that a test surface exists.
bare_pyproject="$tmpdir/bare-pyproject"
mkdir -p "$bare_pyproject/src"
printf '%s\n' '# Rules' 'Do not publish without explicit authorization.' > "$bare_pyproject/AGENTS.md"
printf '%s\n' '[project]' 'name = "demo"' 'version = "0.1.0"' > "$bare_pyproject/pyproject.toml"
printf '%s\n' 'VALUE = 1' > "$bare_pyproject/src/app.py"
bash "$CHECKER" "$bare_pyproject" summary >"$tmpdir/bare-pyproject.out"
grep -q '^maintainability_status: FAIL$' "$tmpdir/bare-pyproject.out"
grep -A2 '^verifier_evidence:$' "$tmpdir/bare-pyproject.out" | grep -q '(none)'
if grep -A2 '^commands:$' "$tmpdir/bare-pyproject.out" | grep -q 'pytest'; then
  echo "pyproject.toml alone must not invent a pytest command"; exit 1
fi

# Case 28: collected CI command labels redact literal credentials and private
# machine paths while the raw command remains available for classification.
redacted_ci="$tmpdir/redacted-ci"
mkdir -p "$redacted_ci/.github/workflows" "$redacted_ci/src"
printf '%s\n' '# Rules' 'Do not publish without explicit authorization.' > "$redacted_ci/AGENTS.md"
printf '%s\n' 'export const ok = true;' > "$redacted_ci/src/app.ts"
fake_token="ghp_$(printf 'A%.0s' {1..16})"
printf '%s\n' \
  'name: check' \
  'on: [push]' \
  'jobs:' \
  '  check:' \
  '    runs-on: ubuntu-latest' \
  '    steps:' \
  "      - run: TOKEN=$fake_token /Users/example/private/check.sh" \
  > "$redacted_ci/.github/workflows/check.yml"
bash "$CHECKER" "$redacted_ci" summary >"$tmpdir/redacted-ci.out"
grep -q '^verification_status: FAIL$' "$tmpdir/redacted-ci.out"
grep -q 'TOKEN=\[REDACTED\] \[PATH\]' "$tmpdir/redacted-ci.out"
if grep -qE "$fake_token|/Users/example" "$tmpdir/redacted-ci.out"; then
  echo "maintainability output leaked a credential or private path"; exit 1
fi

echo "maintainability smoke: ok"
