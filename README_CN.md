<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/logo.svg" width="120" />
  <h1>fskill</h1>
  <p><b>把 gofenix 的工程习惯，变成你的技能</b></p>
  <p><a href="README.md">English</a> · 中文 · <a href="README_TW.md">繁體</a> · <a href="README_JA.md">日本語</a> · <a href="README_KR.md">한국어</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a></p>
  <a href="https://github.com/gofenix/fskill/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/gofenix/fskill/test.yml?branch=main&style=flat-square&label=tests" alt="Tests"></a>
  <a href="https://github.com/gofenix/fskill/stargazers"><img src="https://img.shields.io/github/stars/gofenix/fskill?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/gofenix/fskill/releases"><img src="https://img.shields.io/github/v/tag/gofenix/fskill?label=version&style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://twitter.com/Higofenix"><img src="https://img.shields.io/badge/follow-gofenix-red?style=flat-square&logo=Twitter" alt="Twitter"></a>
</div>

<br/>

## 技能

每个技能是一个目录，里面有参考、脚本和踩过的坑。只在你输入 `/name` 或 `$name` 时进入；说到相关的词不会自动换技能。骨架来自 [tw93/Waza](https://github.com/tw93/Waza)，名字和正文是自己的。

| 技能 | 分组 | 它做什么 |
| :--- | :--- | :--- |
| [`/think`](skills/think/SKILL.md) [`/ui`](skills/ui/SKILL.md) [`/domain`](skills/domain/SKILL.md) [`/map`](skills/map/SKILL.md) [`/slice`](skills/slice/SKILL.md) [`/prototype`](skills/prototype/SKILL.md) [`/architect`](skills/architect/SKILL.md) | 想清楚 | 方案、界面、术语、跨会话地图、切片、试验、边界。 |
| [`/implement`](skills/implement/SKILL.md) [`/hunt`](skills/hunt/SKILL.md) [`/optimize`](skills/optimize/SKILL.md) | 做出来 | 已批准的任务图、根因、一次只动一个指标。 |
| [`/check`](skills/check/SKILL.md) [`/triage`](skills/triage/SKILL.md) [`/verify`](skills/verify/SKILL.md) | 交出去 | 合并、推送和发布前的审查，问题队列，验证说明。 |
| [`/read`](skills/read/SKILL.md) [`/learn`](skills/learn/SKILL.md) [`/write`](skills/write/SKILL.md) | 读和写 | 一个链接或 PDF、多来源研究、把文字改顺。 |
| [`/handoff`](skills/handoff/SKILL.md) [`/retro`](skills/retro/SKILL.md) [`/health`](skills/health/SKILL.md) [`/wizard`](skills/wizard/SKILL.md) | 下次还能用 | 会话交接、已经验证的教训、Agent 配置、人工安装。 |

## 安装

**Claude Code、Codex、Cursor 与其他 Agent**

```bash
npx skills add gofenix/fskill -a claude-code codex cursor -g -y
```

技能统一存放在 `~/.agents/skills` 共享目录，Claude Code 通过软链接接入，Codex、Cursor、Gemini CLI、Copilot、Amp、Kimi Code CLI 以及其他能读这个目录的 Agent 都会读到这 20 个技能。进入某个技能的流程仍要显式调用。有自己技能目录的 Agent 在 `-a` 后面写上它的 ID，比如 `antigravity-cli` 或 `qwen-code`，后续通过 `npx skills update -g -y` 保持更新。也可以直接告诉你的 Agent 帮你安装：
> 阅读 https://github.com/gofenix/fskill/blob/main/llms.txt 帮我安装 fskill

**宿主插件方式**，如果你更习惯使用宿主自有的更新命令（技能带有命名空间前缀，如 `/fskill:check`）：

```bash
# Claude Code（更新命令：claude plugin update fskill）
/plugin marketplace add gofenix/fskill
/plugin install fskill@fskill

# Codex（更新命令：codex plugin marketplace upgrade fskill，然后 codex plugin add fskill@fskill）
codex plugin marketplace add gofenix/fskill
codex plugin add fskill@fskill
```

**Claude Desktop**：下载 [fskill.zip](https://github.com/gofenix/fskill/releases/latest/download/fskill.zip)，打开 Customize > Skills > "+" > Create skill 并上传压缩包，更新时点击卡片上的 "..." 选择 Replace 再上传最新的 ZIP 即可

**Pi**：`pi install npm:@gofenix/fskill`，通过 `pi update npm:@gofenix/fskill` 更新

## 技能串联

顺序由你决定。每个技能做完自己的结果就停下。下一步用 `/name` 或 `$name` 自己调用。

**常见工作流：**

- **做新功能**：`/think` 想透方案，确认后动手实现，再用 `/check` 把关合并
- **排查修复**：`/hunt` 查清根因，动手修复，再用 `/check` 审查改动，需要时一并发布
- **调研成文**：`/read` 读取素材，`/learn` 消化梳理，`/write` 润色文字

## 项目上下文

fskill 只沉淀通用的工程习惯，`/check` 运行时从目标仓库公开的 README、包清单、Makefile、CI 配置和你的任务要求里提炼约束，绝不读取私有路径、凭证或 Token，具体上下文模板可参考 [`skills/check/references/project-context.md`](skills/check/references/project-context.md)。

## 附加工具与规则

下载脚本默认使用最新的 GitHub Release 资源，想用 main 上最新的脚本，可以在命令前加 `FSKILL_REF=main`。

### 状态栏

Claude Code 极简状态栏：显示上下文窗口、5 小时配额与 7 天配额，按用量着色，没有进度条，没有视觉噪音。

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/statusline.png" width="1000" />
</div>

```bash
(
  set -e
  FSKILL_STATUSLINE_SCRIPT="$(mktemp -t fskill-statusline.XXXXXX)"
  trap 'rm -f "$FSKILL_STATUSLINE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-statusline.sh -o "$FSKILL_STATUSLINE_SCRIPT"
  # 可以先检查脚本内容：less "$FSKILL_STATUSLINE_SCRIPT"
  bash "$FSKILL_STATUSLINE_SCRIPT"
)
```

**Codex** 原生支持状态栏字段，直接添加到 `~/.codex/config.toml`：

```toml
[tui]
status_line = ["model-with-reasoning", "current-dir", "context-used", "five-hour-limit", "weekly-limit"]
status_line_use_colors = true
```

Codex 显示剩余额度，上方 Claude Code 状态栏显示已用百分比（上游暂未提供 `five-hour-used` / `weekly-used`）。

### 可选规则

可选规则用于补充技能之外的长期习惯，写入 Agent 的持久化指令后生效，只安装技能默认不会开启，按需复制执行即可（在对应 Agent 上把 `claude-code` 换成 `codex` 或 `antigravity-cli`）：

```bash
(
  set -e
  FSKILL_RULE_SCRIPT="$(mktemp -t fskill-rule.XXXXXX)"
  trap 'rm -f "$FSKILL_RULE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-rule.sh -o "$FSKILL_RULE_SCRIPT"
  # 可以先检查脚本内容：less "$FSKILL_RULE_SCRIPT"

  # 英文写作教练：Prompt 中有英文表达错误时，在结尾追加一条简短的 😇 纠错建议
  bash "$FSKILL_RULE_SCRIPT" english claude-code

  # 行为防错守则：全局常驻约束（先看再改、不随意扩大范围、不主动输出冗余总结）
  bash "$FSKILL_RULE_SCRIPT" anti-patterns claude-code

  # 技能路由提示：技能名单，以及只在 /name 或 $name 时进入
  bash "$FSKILL_RULE_SCRIPT" fskill-routing claude-code

  # 日常清晰表达：术语统一、条件明确、保留不确定性
  # Clarity 规则目前在 main 分支可用，尚未进入正式发版
  FSKILL_REF=main bash "$FSKILL_RULE_SCRIPT" clarity claude-code
)
```

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/english-coaching.png" width="1000" />
</div>

[Clarity](rules/clarity.md) 借鉴了 ASD-STE100 的清晰写作原则，不会强加受控英文语法，也不会改变你的个人表达风格，重新运行命令即可更新，开一个新会话后生效。Codex 会在 `~/.codex/AGENTS.md` 写入标记块，Claude Code 与 Antigravity 则安装为规则文件，其他工具把规则复制进各自的自定义指令即可

## 为什么做 fskill

fskill 是 gofenix 自己的技能集。工作方式来自 [tw93/Waza](https://github.com/tw93/Waza)，名字不沿用，因为 Waza 是别人的。现在是 20 个技能，分成想清楚、做出来、交出去、读和写、下次还能用。每个技能写清结果、不能碰的线，以及怎么算做完。

调用是显式的：`/name` 或 `$name`。意思相近不会自动开始那套流程。

## 卸载

```bash
npx skills remove gofenix/fskill -g
rm -f ~/.claude/statusline.sh
rm -f ~/.claude/rules/english.md
rm -f ~/.claude/rules/anti-patterns.md
rm -f ~/.claude/rules/fskill-routing.md
rm -f ~/.claude/rules/clarity.md
```

状态栏还需从 `~/.claude/settings.json` 删掉 `statusLine` 条目，Claude Desktop 直接在 Customize > Skills 中删除 fskill，装过 Codex 规则的，从 `~/.codex/AGENTS.md` 删掉对应的 fskill 标记块，Antigravity 从 `~/.gemini/antigravity-cli/rules/` 删除对应规则文件，其他工具从自定义指令中移除即可，移除后开启新会话生效。

## 支持

如果 fskill 有用，给仓库点个 Star，或者开一个 Issue。

## 许可证

MIT License. Please feel free to use and contribute to the development.
