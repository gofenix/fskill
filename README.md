<div align="center">
  <img src="https://gw.alipayobjects.com/zos/k/2h/waza.svg" width="120" />
  <h1>Waza</h1>
  <p><b>把工程师已经知道的好习惯，变成 AI agent 能执行的技能。</b></p>
  <a href="https://github.com/gofenix/Waza/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/gofenix/Waza/test.yml?branch=main&style=flat-square&label=tests" alt="Tests"></a>
  <a href="https://github.com/gofenix/Waza/stargazers"><img src="https://img.shields.io/github/stars/gofenix/Waza?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/gofenix/Waza/releases"><img src="https://img.shields.io/github/v/tag/gofenix/Waza?label=version&style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://twitter.com/HiTw93"><img src="https://img.shields.io/badge/follow-Tw93-red?style=flat-square&logo=Twitter" alt="Twitter"></a>
</div>

<br/>

## 为什么

Waza（技，わざ）是日语里的“技法”：反复练到接近本能的动作。

好的工程师不只是写代码。他会先想清楚需求，审查自己的改动，系统地定位问题，设计有判断力的界面，阅读一手资料，也会把复杂事情写清楚、学透一个新领域。

AI 很擅长产出，但没有结构时容易滑向泛泛而谈。这条线维护在 [gofenix/Waza](https://github.com/gofenix/Waza)：把工程习惯变成可调用技能，让模型在明确目标、边界和证据要求里工作。核心技能不超过十个。

它和 [Kaku](https://github.com/tw93/Kaku)（書く）以及 [Kami](https://github.com/tw93/Kami)（紙）同一族：Kaku 写代码，Waza 练工程习惯，Kami 做可交付文档。上游习惯集见 [tw93/Waza](https://github.com/tw93/Waza)。

<div align="center">
  <img src="https://gw.alipayobjects.com/zos/k/qa/waza_repaired_v4.svg" width="1000" />
</div>

## Skills

每个技能都是一个工程习惯。Claude Code 里可以直接输入 slash command；Codex 或其他 agent 里按技能名调用即可。

| Skill | 什么时候用 | 它做什么 |
| :--- | :--- | :--- |
| [`/think`](skills/think/SKILL.md) | 新功能、架构决策、动手前 | 追问目标和取舍，压测方案，产出另一个 agent 可以直接实施的计划。 |
| [`/design`](skills/design/SKILL.md) | 前端界面、组件、截图审美问题 | 做有方向感的 UI，包括基于真实截图的视觉迭代，避免默认模板感。 |
| [`/check`](skills/check/SKILL.md) | 任务完成后、合并前、发布前 | 看 diff，提取项目约束，处理已批准的 commit/push/release/issue 收尾，并用证据验证。 |
| [`/hunt`](skills/hunt/SKILL.md) | 报错、崩溃、回归、异常行为 | 先找到根因再修，尤其适合“以前可以，现在不行”的问题。 |
| [`/write`](skills/write/SKILL.md) | 写作、改稿、去 AI 味 | 中英文文案改写和审阅，保留原意，让表达更自然。 |
| [`/learn`](skills/learn/SKILL.md) | 研究陌生领域或多份材料 | 六阶段研究流：收集、消化、搭结构、填内容、打磨、自审到可发布。 |
| [`/read`](skills/read/SKILL.md) | 任意 URL 或 PDF | 根据平台选择抓取方式。普通阅读给摘要，需要全文、引用、保存或下游处理时给 Markdown。 |
| [`/health`](skills/health/SKILL.md) | Agent 配置、指令、验证面、维护性审计 | 检查 Codex、Claude Code、Pi、项目指令、验证输出和 AI 可维护性。 |
| [`/handoff`](skills/handoff/SKILL.md) | 会话交接、压缩上下文 | 把当前会话写成 `HANDOFF.md`，让下一个 agent 接着干。 |

分组只用于阅读，目录保持扁平。

| 阶段 | 技能 |
| :--- | :--- |
| 想清楚 | `/think` |
| 动手做 | `/design` |
| 找问题 | `/hunt`、`/check` |
| 写作与学习 | `/write`、`/learn`、`/read` |
| 维护环境 | `/health`、`/handoff` |

每个技能文件夹里都有参考文档、辅助脚本和从真实失败里沉淀出的注意事项。工程立场见 [`rules/principles.md`](rules/principles.md)。

## 安装和更新

建议全局安装，这样每个项目都能使用同一套技能。

**Claude Code**

```bash
npx skills add gofenix/Waza -a claude-code -g -y
```

这会安装 `/think`、`/design`、`/check`、`/hunt`、`/write`、`/learn`、`/read`、`/health` 和 `/handoff`。只装单个技能可以用 `npx skills add gofenix/Waza --skill think -a claude-code -g -y`。

**Codex**

```bash
codex plugin marketplace add gofenix/Waza
codex plugin add waza@waza
```

这会从仓库 marketplace 安装 Waza Codex 插件。后续更新用 `codex plugin marketplace upgrade waza`，再运行 `codex plugin add waza@waza` 刷新本地快照。
如果你仍想用旧的 skills installer，可以运行 `npx skills add gofenix/Waza -a codex -g -y`；单技能安装用 `npx skills add gofenix/Waza --skill think -a codex -g -y`。

**Antigravity**

```bash
npx skills add gofenix/Waza -a antigravity -g -y
npx skills add gofenix/Waza -a antigravity-cli -g -y
```

`antigravity` 对应桌面端，`antigravity-cli` 对应终端 agent。两者都使用标准 `skills/<name>/SKILL.md` 布局。

**OpenCode**

```bash
npx skills add gofenix/Waza -a opencode -g -y
```

安装后 OpenCode 会通过原生 skill 工具加载 Waza。任务匹配时按 `think`、`design`、`check`、`hunt`、`write`、`learn`、`read`、`health` 或 `handoff` 调用。

**Claude Code plugin marketplace**（单技能入口需要 Claude Code v2.1.143+）

```bash
/plugin marketplace add gofenix/Waza
/plugin install waza@waza
```

这会安装全部九个核心技能。Claude Code v2.1.143 或更新版本可以只装一个：`/plugin install waza-<name>@waza`，例如 `waza-think@waza`。

**Claude Desktop**

下载 [waza.zip](https://github.com/gofenix/Waza/releases/latest/download/waza.zip)，在 Customize > Skills > "+" > Create skill 上传 ZIP。

**Pi coding agent**

```bash
pi install npm:@tw93/waza
```

Pi 可以从仓库或发布到 npm 的 `@tw93/waza` 包读取标准 `skills/<name>/SKILL.md` 布局。`/health` 会同时审计 Pi 设置、已配置包和本地 skill roots。

**Update**

```bash
npx skills update -g -y
```

Marketplace 安装用 `claude plugin update <skill>`。Claude Desktop 用户可以用最新 [waza.zip](https://github.com/gofenix/Waza/releases/latest/download/waza.zip) 替换旧版本。
Codex 插件安装用 `codex plugin marketplace upgrade waza`，再运行 `codex plugin add waza@waza`。
Pi 用户可以运行 `pi update npm:@tw93/waza`，或用 `pi update --extensions` 更新全部扩展。
想收到新版提醒，可以 watch [GitHub Releases](https://github.com/gofenix/Waza/releases)。

## 项目上下文

Waza 把通用工程习惯放在公共技能里。`/check` 进入具体项目时，会从目标仓库的公开上下文和用户本轮约束里提取规则。

- 项目命令来自 README、package manifest、Makefile、CI workflow 和用户明确说明。
- 项目 hard stops 包括生成物、受保护文件、版本同步、release assets 和领域安全风险。
- 公共文档和示例不能包含证书、私钥路径、token、个人机器路径或内部系统细节。

Review context 模板见 [`skills/check/references/project-context.md`](skills/check/references/project-context.md)。

## 技能串联

技能可以串起来用，但不会自动连锁。每个技能完成后都会停下，等你决定下一步。

常见流程：

- **设计功能**：`/think` -> approve -> say "implement X" -> `/check` -> merge
- **修复问题**：`/hunt` -> fix -> `/check` -> release/publish/push/issue follow-through
- **研究写作**：`/read` fetch sources -> `/learn` synthesize -> `/write` polish
- **调试验证**：`/hunt` root cause -> fix -> `/check` review changes

每个箭头都代表一次用户动作。技能不会自行触发下一个技能。

## Extras

### Statusline

Claude Code 的轻量 statusline：context window、5-hour quota 和 7-day quota。按用量上色，不做进度条，不加噪声。

<div align="center">
  <img src="https://gw.alipayobjects.com/zos/k/y9/RUgevg.png" width="1000" />
</div>

```bash
curl -sL https://github.com/gofenix/Waza/releases/latest/download/setup-statusline.sh | bash
```

**Codex** 有原生 statusline 项。加入 `~/.codex/config.toml`：

```toml
[tui]
status_line = ["model-with-reasoning", "current-dir", "context-used", "five-hour-limit", "weekly-limit"]
status_line_use_colors = true
```

Codex 显示剩余额度；Claude Code statusline 显示已用百分比。

### English Coaching

可选英语练习规则。你的英文提示有明显问题时，agent 会追加一条很短的 😇 correction；纯中文提示不触发。

<div align="center">
  <img src="https://gw.alipayobjects.com/zos/k/24/vfkGOi.png" width="1000" />
</div>

```bash
# Claude Code
curl -sL https://github.com/gofenix/Waza/releases/latest/download/setup-rule.sh | bash -s -- english claude-code

# Codex
curl -sL https://github.com/gofenix/Waza/releases/latest/download/setup-rule.sh | bash -s -- english codex
```

### Anti-Patterns

可选的全局护栏：先读再动手、不幻觉路径、不偷换范围、不主动写无意义总结。它不属于某个技能，安装后每个会话都能生效。

```bash
curl -sL https://github.com/gofenix/Waza/releases/latest/download/setup-rule.sh | bash -s -- anti-patterns claude-code
```

Codex 用 `codex` 替换 `claude-code`。Curl URLs use the latest GitHub release asset. Set `WAZA_REF=main` before the command if you want bleeding-edge scripts.

### Routing Hint

可选路由提示：告诉宿主在用户请求匹配时优先使用 Waza skills。Codex、Pi 和其他不会自动根据 `description` 路由的 agent 会更需要它；Claude Code 已经能通过 description 路由，所以也是可选项。

```bash
curl -sL https://github.com/gofenix/Waza/releases/latest/download/setup-rule.sh | bash -s -- waza-routing claude-code
```

Codex 用 `codex` 替换 `claude-code`。

## Uninstall

```bash
npx skills remove gofenix/Waza -g
rm -f ~/.claude/statusline.sh
rm -f ~/.claude/rules/english.md
rm -f ~/.claude/rules/anti-patterns.md
rm -f ~/.claude/rules/waza-routing.md
```

Claude Desktop 里从 Customize > Skills 删除 Waza。Codex rule 安装需要删除 `~/.codex/AGENTS.md` 中标记的 Waza 区块。

## Background

很多技能合集很强，但也容易太重：技能太多、配置太多、学习成本太高。

每写一条规则，也是在给模型设一个上限。Waza 的取向相反：每个技能只给清晰目标和关键约束，然后让模型发挥。随着模型变强，克制会带来复利。

核心技能不超过十个，覆盖真正常用的工程习惯。每个技能只做一件事，有清楚触发词，也知道什么时候不该介入。它来自真实项目和使用中的失败修正。

`/health` 来自 [这篇 Claude Code 框架文章](https://tw93.fun/en/2026-03-12/claude.html) 的六层审计思路，现在覆盖 Codex、Claude Code、Pi、验证面和 AI 可维护性。
