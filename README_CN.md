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

fskill 采用 **9 个精简工作流 + 8 条 `pstack` 风格工程原则（`p-*`）+ 确定性脚本**。单条技能通过 `/name` 或 `$name` 进入；`think`、`hunt`、`check` 与 8 条 `p-*` 原则在任务本身匹配时也可自动生效，其余 6 条只在显式调用或进入 `/f-mode` 后运行。基于 [Waza](https://github.com/tw93/Waza)，并融合 [Matt Pocock skills](https://github.com/mattpocock/skills) 与 [pstack](https://github.com/cursor/plugins/tree/main/pstack) 的原则化设计；完整来源见下方许可证。

| 技能 | 分组 | 它做什么 |
| :--- | :--- | :--- |
| [`/f-mode`](skills/f-mode/SKILL.md) | 路由 | 显式开启，按目标在会话内选用工作流并挂载 `p-*` 原则。 |
| [`/think`](skills/think/SKILL.md) | 想清楚 | 动手前方案规划、价值判断（放弃/保留/转向）、范围分类与 `grill me` 压测。 |
| [`/hunt`](skills/hunt/SKILL.md) | 找问题 | 用运行时证据查实根因；指标已定时单假设对照验证。 |
| [`/check`](skills/check/SKILL.md) | 做检查 | 审 diff/PR、发版价值判断、发布产物门禁、项目审计与事故重放。 |
| [`/ui`](skills/ui/SKILL.md) | 界面 | 做出有方向感、反 AI slop 的界面，按真实渲染与截图验收（显式调用）。 |
| [`/learn`](skills/learn/SKILL.md) [`/write`](skills/write/SKILL.md) | 读和写 | 抓取 URL/PDF 与一手调研；去掉中英文与发布说明 AI 味（显式调用）。 |
| [`/handoff`](skills/handoff/SKILL.md) [`/health`](skills/health/SKILL.md) | 下次还能用 | 会话交接与现状核对；Agent 配置/hooks/MCP/省 token 工具体检与规则瘦身（显式调用）。 |

**8 条 `pstack` 风格工程原则（`p-*`，自动触发）：** [`p-subtract-before-add`](skills/p-subtract-before-add/SKILL.md) · [`p-attack-the-premise`](skills/p-attack-the-premise/SKILL.md) · [`p-fix-root-causes`](skills/p-fix-root-causes/SKILL.md) · [`p-prove-it-works`](skills/p-prove-it-works/SKILL.md) · [`p-test-behavior`](skills/p-test-behavior/SKILL.md) · [`p-explain-the-number`](skills/p-explain-the-number/SKILL.md) · [`p-encode-in-structure`](skills/p-encode-in-structure/SKILL.md) · [`p-respect-boundaries`](skills/p-respect-boundaries/SKILL.md)

输入 `/f-mode`（Codex 用 `$f-mode`，插件用 `/fskill:f-mode`）进入，再直接描述任务；当前会话内持续自动选技能。`/f-mode off` 退出，`/f-mode status` 查看状态。直接 `/hunt` 等命令优先，不关闭 f-mode。新会话默认关闭；选路不扩大操作授权。完整路由见 [skills/RESOLVER.md](skills/RESOLVER.md)。

## 安装

**Claude Code、Codex、Cursor 与其他 Agent**

```bash
npx skills add gofenix/fskill -a claude-code codex cursor -g -y
```

技能统一存放在 `~/.agents/skills` 共享目录，Claude Code 通过软链接接入，Codex、Cursor、Gemini CLI、Copilot、Amp、Kimi Code CLI 以及其他能读这个目录的 Agent 都会读到这 9 个工作流和 8 条原则。仅限显式调用的工作流只在 `/ui`、`$ui` 等明确点名或 `/f-mode` 内进入。有自己技能目录的 Agent 在 `-a` 后面写上它的 ID，比如 `antigravity-cli` 或 `qwen-code`，后续通过 `npx skills update -g -y` 保持更新。也可以直接告诉你的 Agent 帮你安装：
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

在 f-mode 之外，顺序由你决定。每个技能做完自己的结果就停下。下一步用 `/name` 或 `$name` 自己调用。

**常见工作流：**

- **做新功能**：`/think` 用先减后增收拢方案，获准后直接动手，再用 `/check` 把关。
- **排查修复**：`/hunt` 拿运行时证据坐实根因并最小修复，再用 `/check` 核对改动与发布证据。
- **调研成文**：`/learn` 抓取 URL/PDF 或整合一手来源，`/write` 润色正文。

## 项目上下文

fskill 只沉淀通用的工程原则与工具。`/check` 运行时从目标仓库公开的 README、包清单、Makefile、CI 配置和你的任务要求里提炼约束，绝不读取私有路径、凭证或 Token；常见审查陷阱与发布门禁见 [`skills/check/references/review-patterns.md`](skills/check/references/review-patterns.md) 和 [`skills/check/references/release-artifacts.md`](skills/check/references/release-artifacts.md)。

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

  # 技能路由提示：think/hunt/check 可按任务自动进入，其余显式调用；进入 /f-mode 后按目标选技能
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

fskill 是 gofenix 自己的技能集。结合 [tw93/Waza](https://github.com/tw93/Waza) 的脚本与 [pstack](https://github.com/cursor/plugins/tree/main/pstack) 的原则化思路，砍掉已被现代前沿模型内化的重型 SOP，保留 **9 个精简工作流**（`f-mode`、`think`、`hunt`、`check`、`ui`、`learn`、`write`、`handoff`、`health`）、**8 条短工程原则**（`p-*`）以及确定性检查脚本。

每条技能都能用 `/name` 或 `$name` 调用；`think`、`hunt`、`check` 与 `p-*` 原则也会按任务匹配自动生效，其余 6 条只在显式调用或进入 `/f-mode` 后运行。

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

MIT 许可，UI 参考含 Apache-2.0 材料。感谢 [Waza](https://github.com/tw93/Waza)、[Matt Pocock skills](https://github.com/mattpocock/skills)、[pstack](https://github.com/cursor/plugins/tree/main/pstack)。UI 方法还吸收了 [Impeccable](https://github.com/pbakaus/impeccable)、[taste-skill](https://github.com/Leonxlnx/taste-skill) 和 [apple-design](https://github.com/emilkowalski/skills)。来源版本、改写说明与完整许可统一维护在根目录 [LICENSE](LICENSE)。gofenix 的署名对应原创新增和修改，上游署名对应各自沿用的材料。
