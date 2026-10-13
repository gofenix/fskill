#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

CHECKER="$ROOT/skills/health/scripts/check-agent-context.sh"

tmpdir=$(make_tmpdir)
project="$tmpdir/project"
home_dir="$tmpdir/home"
mkdir -p \
  "$project" \
  "$project/.pi/skills/local-skill" \
  "$home_dir/.codex" \
  "$home_dir/.pi/agent/skills/global-skill" \
  "$home_dir/.agents/skills/legacy-skill"

write_standard_agents_md "$project/AGENTS.md"
printf '%s\n' 'global codex rule' > "$home_dir/.codex/AGENTS.md"

# config.toml with sensitive keys that must be redacted before output.
{
  printf '%s\n' 'api_key = "SHOULD_NOT_LEAK"'
  printf '%s\n' 'token = "TOKEN_SHOULD_NOT_LEAK"'
  printf '%s\n' '[features]'
  printf '%s\n' 'hooks = true'
  printf '%s\n' '[plugins."github@openai-curated"]'
  printf '%s\n' 'enabled = true'
  printf '%s\n' "[projects.\"$project\"]"
  printf '%s\n' 'trust_level = "trusted"'
} > "$home_dir/.codex/config.toml"

printf '%s\n' '---' 'name: local-skill' '---' > "$project/.pi/skills/local-skill/SKILL.md"
printf '%s\n' '---' 'name: global-skill' '---' > "$home_dir/.pi/agent/skills/global-skill/SKILL.md"
printf '%s\n' '---' 'name: legacy-skill' '---' > "$home_dir/.agents/skills/legacy-skill/SKILL.md"
printf '%s\n' '{"pi":{"skills":["./skills"]}}' > "$project/package.json"

{
  printf '%s\n' '{'
  printf '%s\n' '  "skills": ["core"],'
  printf '%s\n' '  "packages": ["npm:@tw93/waza"],'
  printf '%s\n' '  "apiToken": "PI_TOKEN_SHOULD_NOT_LEAK"'
  printf '%s\n' '}'
} > "$home_dir/.pi/agent/settings.json"

{
  printf '%s\n' '{'
  printf '%s\n' '  "skills": {"local": true},'
  printf '%s\n' '  "packages": {"project-package": {"enabled": true}},'
  printf '%s\n' '  "password": "PROJECT_PI_PASSWORD_SHOULD_NOT_LEAK"'
  printf '%s\n' '}'
} > "$project/.pi/settings.json"

HOME="$home_dir" bash "$CHECKER" "$project" summary >"$tmpdir/context.out"
grep -q '^agent_instruction_status: PASS$' "$tmpdir/context.out"
grep -q '^codex_status: PASS$' "$tmpdir/context.out"
grep -q '^project_trust: exact:trusted$' "$tmpdir/context.out"
grep -q 'api_key=\[REDACTED\]' "$tmpdir/context.out"
grep -q 'token=\[REDACTED\]' "$tmpdir/context.out"
grep -q '^=== PI SURFACE ===$' "$tmpdir/context.out"
grep -q '^pi_status: PASS$' "$tmpdir/context.out"
grep -q '^global_settings_json: yes$' "$tmpdir/context.out"
grep -q '^project_settings_json: yes$' "$tmpdir/context.out"
grep -q '^global_pi_skill_roots: 1$' "$tmpdir/context.out"
grep -q '^project_pi_skill_roots: 1$' "$tmpdir/context.out"
grep -q '^global_agents_skill_roots: 1$' "$tmpdir/context.out"
grep -q '  ./skills' "$tmpdir/context.out"
grep -q '  global_settings.skills: core' "$tmpdir/context.out"
grep -q '  project_settings.skills: local' "$tmpdir/context.out"
grep -q '  global_settings.packages: npm:@tw93/waza' "$tmpdir/context.out"
grep -q '  project_settings.packages: project-package' "$tmpdir/context.out"
grep -q 'global_settings.apiToken=\[REDACTED\]' "$tmpdir/context.out"
grep -q 'project_settings.password=\[REDACTED\]' "$tmpdir/context.out"
if grep -q 'SHOULD_NOT_LEAK' "$tmpdir/context.out"; then
  echo "agent context leaked sensitive config"; exit 1
fi

# Global drift: Codex AGENTS.md with only generated identity context should be
# flagged when Claude has operational rules.
mkdir -p "$home_dir/.claude"
printf '%s\n' \
  '# Global Rules' \
  '## Git Safety' \
  'Do not auto-push.' \
  '## Verification' \
  'Run checks before claiming done.' \
  > "$home_dir/.claude/CLAUDE.md"
printf '%s\n' '<!-- nian-identity:start -->' 'identity only' '<!-- nian-identity:end -->' > "$home_dir/.codex/AGENTS.md"
HOME="$home_dir" bash "$CHECKER" "$project" summary >"$tmpdir/drift.out"
grep -q '^codex_status: WARN$' "$tmpdir/drift.out"
grep -q 'global Codex AGENTS.md has identity/memory context but lacks operational rules' "$tmpdir/drift.out"

# High-permission Codex config is a one-time user-tradeoff warning, not a
# per-project "add denies" action (Codex has no command-level deny mechanism).
{
  printf '%s\n' 'approval_policy = "never"'
  printf '%s\n' 'sandbox_mode = "danger-full-access"'
} >> "$home_dir/.codex/config.toml"
HOME="$home_dir" bash "$CHECKER" "$project" summary >"$tmpdir/danger.out"
grep -q 'Codex has no command-level deny mechanism' "$tmpdir/danger.out"

# Delegation: CLAUDE.md pointing to AGENTS.md should show delegates_to=yes and
# clear the conflict warning.
printf '%s\n' '@AGENTS.md' > "$project/CLAUDE.md"
HOME="$home_dir" bash "$CHECKER" "$project" summary >"$tmpdir/delegation.out"
grep -q '^claude_delegates_to_agents: yes$' "$tmpdir/delegation.out"
grep -q '^conflict_status: PASS$' "$tmpdir/delegation.out"

echo "agent context smoke: ok"
