<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/logo.svg" width="120" />
  <h1>fskill</h1>
  <p><b>gofenix's engineering habits, turned into your skills.</b></p>
  <p>English · <a href="README_CN.md">中文</a> · <a href="README_TW.md">繁體</a> · <a href="README_JA.md">日本語</a> · <a href="README_KR.md">한국어</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a></p>
  <a href="https://github.com/gofenix/fskill/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/gofenix/fskill/test.yml?branch=main&style=flat-square&label=tests" alt="Tests"></a>
  <a href="https://github.com/gofenix/fskill/stargazers"><img src="https://img.shields.io/github/stars/gofenix/fskill?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/gofenix/fskill/releases"><img src="https://img.shields.io/github/v/tag/gofenix/fskill?label=version&style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://twitter.com/Higofenix"><img src="https://img.shields.io/badge/follow-gofenix-red?style=flat-square&logo=Twitter" alt="Twitter"></a>
</div>

<br/>

## Skills

Each engineering habit gets an installed skill, a folder with reference docs, helper scripts, and gotchas from real failures. In Claude Code, type the slash command. In Codex, invoke the installed skill by name and follow the same playbook.

| Skill | When | What it does |
| :--- | :--- | :--- |
| [`/think`](skills/think/SKILL.md) [`/ui`](skills/ui/SKILL.md) [`/domain`](skills/domain/SKILL.md) [`/map`](skills/map/SKILL.md) [`/slice`](skills/slice/SKILL.md) [`/prototype`](skills/prototype/SKILL.md) [`/architect`](skills/architect/SKILL.md) | Decide | Plan, interface, terms, cross-session map, slices, experiments, boundaries. |
| [`/implement`](skills/implement/SKILL.md) [`/hunt`](skills/hunt/SKILL.md) [`/optimize`](skills/optimize/SKILL.md) | Build | Approved task graph, root cause, one-metric experiments. |
| [`/check`](skills/check/SKILL.md) [`/triage`](skills/triage/SKILL.md) [`/verify`](skills/verify/SKILL.md) | Ship | Diff and release review, issue queue, verification guide. |
| [`/read`](skills/read/SKILL.md) [`/learn`](skills/learn/SKILL.md) [`/write`](skills/write/SKILL.md) | Read and write | One URL or PDF, multi-source research, prose. |
| [`/handoff`](skills/handoff/SKILL.md) [`/retro`](skills/retro/SKILL.md) [`/health`](skills/health/SKILL.md) [`/wizard`](skills/wizard/SKILL.md) | Keep | Session handoff, verified lessons, agent config, human setup. |

Commands are explicit (`/think`, `$think`). Saying a related word does not switch skills. Refined from [tw93/Waza](https://github.com/tw93/Waza).

## Install

**Claude Code, Codex, Cursor, and other agents**

```bash
npx skills add gofenix/fskill -a claude-code codex cursor -g -y
```

One copy lands in `~/.agents/skills`, the shared skills directory. Claude Code is symlinked in; Codex, Cursor, Gemini CLI, Copilot, Amp, Kimi Code CLI, and every other agent that reads that directory picks the twenty skills up as `/check`, `/think`, and so on. Agents with a private skills directory take their id after `-a` (for example `antigravity-cli` or `qwen-code`). Update with `npx skills update -g -y`. You can also tell your agent to install it:
> Install fskill for me by reading https://github.com/gofenix/fskill/blob/main/llms.txt

**Host plugin**, if you prefer the host's own update command (skills are namespaced, `/fskill:check`)

```bash
# Claude Code (update: claude plugin update fskill)
/plugin marketplace add gofenix/fskill
/plugin install fskill@fskill

# Codex (update: codex plugin marketplace upgrade fskill, then codex plugin add fskill@fskill)
codex plugin marketplace add gofenix/fskill
codex plugin add fskill@fskill
```

**Claude Desktop**: download [waza.zip](https://github.com/gofenix/fskill/releases/latest/download/waza.zip), open Customize > Skills > "+" > Create skill, and upload the ZIP. To update, click "..." on the skill card, choose Replace, and upload the latest ZIP.

**Pi**: `pi install npm:fskill`, update with `pi update npm:fskill`.

## Chaining Skills

You decide the order. Each skill stops when its outcome is done. Call the next one with `/name` or `$name`.

**Common workflows:**

- **Plan a feature**: `/think` to settle the plan, implement after approval, then `/check` before merging
- **Ship a fix**: `/hunt` to find the root cause, fix it, then `/check` to review the changes and, when needed, handle release, publish, push, and issue follow-through
- **Research and write**: `/read` to fetch sources, `/learn` to synthesize, `/write` to polish

## Project Context

fskill ships only generic engineering habits. `/check` becomes project-aware at runtime by reading the target repository's public context (READMEs, package manifests, Makefiles, CI workflows) and your task constraints, never private paths, credentials, or tokens. See [`skills/check/references/project-context.md`](skills/check/references/project-context.md) for the review context template.

## Extras

Curl URLs use the latest GitHub release asset. Set `WAZA_REF=main` before the command if you want bleeding-edge scripts.

### Statusline

A minimal statusline for Claude Code: context window, 5-hour quota, and 7-day quota. Color-coded by usage, no progress bars, no noise.

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/statusline.png" width="1000" />
</div>

```bash
(
  set -e
  WAZA_STATUSLINE_SCRIPT="$(mktemp -t fskill-statusline.XXXXXX)"
  trap 'rm -f "$WAZA_STATUSLINE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-statusline.sh -o "$WAZA_STATUSLINE_SCRIPT"
  # review it first: less "$WAZA_STATUSLINE_SCRIPT"
  bash "$WAZA_STATUSLINE_SCRIPT"
)
```

**Codex** has native statusline items. Add to `~/.codex/config.toml`:

```toml
[tui]
status_line = ["model-with-reasoning", "current-dir", "context-used", "five-hour-limit", "weekly-limit"]
status_line_use_colors = true
```

Codex shows remaining quota; the Claude Code statusline above shows used percentage (upstream does not yet expose `five-hour-used` / `weekly-used`).

### Optional Rules

Optional rules apply beyond skill invocations when installed into your agent's persistent instructions. Installing fskill skills alone does not enable them. Copy the ones you want (swap `claude-code` for `codex` or `antigravity-cli` on those agents):

```bash
(
  set -e
  WAZA_RULE_SCRIPT="$(mktemp -t fskill-rule.XXXXXX)"
  trap 'rm -f "$WAZA_RULE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-rule.sh -o "$WAZA_RULE_SCRIPT"
  # review it first: less "$WAZA_RULE_SCRIPT"

  # English coaching: appends a short 😇 correction when your prompt has an English mistake
  bash "$WAZA_RULE_SCRIPT" english claude-code

  # Anti-patterns: always-on cross-skill guardrails (read before acting, no scope creep, no unsolicited summaries)
  bash "$WAZA_RULE_SCRIPT" anti-patterns claude-code

  # Routing hint: the skill names and the rule that invocation is explicit, /name or $name
  bash "$WAZA_RULE_SCRIPT" fskill-routing claude-code

  # Clear everyday replies: consistent terms, explicit conditions, preserved uncertainty
  # Clarity is available on main; it is not in the current release yet.
  WAZA_REF=main bash "$WAZA_RULE_SCRIPT" clarity claude-code
)
```

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/english-coaching.png" width="1000" />
</div>

[Clarity](rules/clarity.md) uses clear-writing principles from ASD-STE100 without imposing controlled-English grammar or changing your voice. Re-run its command to update the installed rule, then start a new session. Codex installs a marked block in `~/.codex/AGENTS.md`; Claude Code and Antigravity install a rule file. For other tools, copy the rule into their persistent custom instructions.

## Why

fskill is gofenix's skill set. The working shape comes from [tw93/Waza](https://github.com/tw93/Waza); the name does not, because Waza belongs to someone else. There are twenty skills, in five groups: decide, build, ship, read and write, and leave something the next session can use. Each skill states the outcome, the lines it does not cross, and how you know it is done.

You enter a skill with `/name` or `$name`. A similar word does not start that workflow.

## Uninstall

```bash
npx skills remove gofenix/fskill -g
rm -f ~/.claude/statusline.sh
rm -f ~/.claude/rules/english.md
rm -f ~/.claude/rules/anti-patterns.md
rm -f ~/.claude/rules/fskill-routing.md
rm -f ~/.claude/rules/clarity.md
```

For the statusline, also remove the `statusLine` entry from `~/.claude/settings.json`. For Claude Desktop, delete fskill from Customize > Skills. For Codex rule installs, remove the marked fskill blocks from `~/.codex/AGENTS.md`. For Antigravity, remove the selected rule file from `~/.gemini/antigravity-cli/rules/`. Remove copied rules from other tools' custom instructions. Start a new session after removing a rule.

## Support

If fskill helped, star the repo or open an issue.

## License

MIT License. Please feel free to use and contribute to the development.
