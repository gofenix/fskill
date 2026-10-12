# Waza Skill Resolver

## Shared Output Marker

所有技能都沿用同一个输出约定：首行内联带上 `🥷`，不要单独起段。这个约定写在各自的 `SKILL.md` 里，`scripts/verify_skills.py` 也会校验。

这份文档是给人看的集中路由索引。Claude Code 等宿主主要通过每个 `SKILL.md` 的 `description` 和 `when_to_use` 自动匹配；这里用于人工确认和漂移校验。改技能描述、触发词或范围时，同步更新这里。

> **Read the skill file before acting.** 两个技能都可能匹配时，两个都读。它们可以串联，例如 `/think` -> 实现 -> `/check`。

## 按工作流阶段分路

分组只用于阅读。`skills/` 保持扁平，不建分类目录。工程立场见 [rules/principles.md](../rules/principles.md)。核心技能不超过 10 个，`handoff` 计入。

### 想清楚

| 触发 | 技能 |
|---|---|
| 新功能、架构方案、怎么设计、用什么方案、判断要不要做、有没有必要、值不值得、需要可执行计划、grill me、压测方案、架构草图、先做原型 | `skills/think/SKILL.md` |
| 怎么工作的、走读、这段怎么跑、放在哪一层、where should this live、how does this work | `skills/how/SKILL.md` |

### 动手做

| 触发 | 技能 |
|---|---|
| UI、页面、组件、前端、字体排印、截图里说丑/怪/不清晰/不协调、视觉 polish | `skills/design/SKILL.md` |

测试纪律不是技能。只有用户明确要求或本地测试很便宜时，才读 [`skills/check/references/tdd-discipline.md`](check/references/tdd-discipline.md)。

### 找问题

| 触发 | 技能 |
|---|---|
| 报错、崩溃、测试失败、行为异常、为什么不工作、以前是好的现在坏了、回归、截图回归、缓存/队列/生成物边界、diagnose、缩小复现 | `skills/hunt/SKILL.md` |
| review、看看代码、合并前、实现完成、生成物检查、release gate、`code-review`、双轴审查、blast radius、影响面 | `skills/check/SKILL.md` |
| release、publish、push、commit、close issue、发布表情、registry/asset 检查 | `skills/check/SKILL.md` |
| 看 issue、看 PR、triage、批量处理、关闭 issue | `skills/check/SKILL.md` |
| 项目体检、项目评分、代码质量评分、scorecard、linus review、rate this codebase | `skills/check/SKILL.md` |

### 写作与学习

| 触发 | 技能 |
|---|---|
| 写作、改稿、润色、去 AI 味、本地化文案、tweet、release notes 文案、文档审阅、unslop | `skills/write/SKILL.md` |
| 深度研究陌生领域、多份材料综合、整理成文章、compile sources | `skills/learn/SKILL.md` |
| 消息含 http(s) URL、网页链接、PDF 路径、看这个链接、读一下 | `skills/read/SKILL.md` |

### 维护环境

| 触发 | 技能 |
|---|---|
| 检查 Claude/Codex/Pi 配置、agent 不听指令、hook/MCP 异常、AGENTS/CLAUDE/config 漂移、验证缺失、AI coding 腐化、维护性、上下文混乱、retro、复盘 | `skills/health/SKILL.md` |
| handoff、交接、写交接文档、dump context、summarize session、会话总结、compact conversation、下一会话用途、recall | `skills/handoff/SKILL.md` |

## Disambiguation（歧义消解）

1. **最具体优先**：UI 决策里 `/design` 比 `/think` 更具体。
2. **URL 先读取**：消息含 URL 时先 `/read` 取回内容；如果用户要深度研究，再接 `/learn`。
3. **改错 vs review**：代码已交付或 PR 准备好 -> `/check`；代码跑不通或行为错 -> `/hunt`。
4. **配置/维护性 vs 用户代码**：agent 指令、hooks/MCP、配置、上下文、验证面、AI 可维护性 -> `/health`；用户代码异常 -> `/hunt`。
5. **发布动作 vs 发布文案**：commit/tag/publish/push/release reaction/close issue -> `/check`；写 release notes/changelog -> `/write`。
6. **截图审美 vs 截图回归**：截图里说丑/怪/不清晰且是审美问题 -> `/design`；截图证明状态错误、渲染错或以前可用 -> `/hunt`。
7. **从零产出 vs 润色**：从材料到文章 -> `/learn`；已有稿子改写 -> `/write`。
8. **判断 vs 调试**：判断报错原因 -> `/hunt`；判断要不要做、该不该保留 -> `/think`。
9. **兜底**：仍然模糊时读候选技能的 `Not for` 段，用排除法；还不清楚就问用户。
10. **怎么工作 vs 要不要做**：解释现状、归属和分层走 `/how`；价值判断和计划走 `/think`。
11. **压测和草图仍是 think**：grill、架构草图、一次性原型都走 `/think`。
12. **影响面仍是 check**：双轴审查和 blast radius 走 `/check`，不是新技能。TDD 也只是 `/check` 的 reference。
13. **复盘环境是 health**：retro 看 agent 工作环境；代码对不对走 `/check` 或 `/hunt`。
14. **重建上下文是 handoff**：recall 不新开技能，默认不覆盖 `HANDOFF.md`。

## Chaining（常见串联）

技能默认不自动串联。每个技能完成后停下来，等用户决定下一步，除非当前请求已经明确授权后续动作。

- `/think` 出方案 -> 用户说“实现” -> 实施 -> 用户说 `/check` -> 审查
- `/think` 出可执行计划 -> 用户说 “Implement the plan / 可以干 / 直接改” -> 按计划实施，不重新争论方向
- `/hunt` 定位并修复 -> 用户说“发布 / push / 关闭 issue” -> `/check` 做发布前检查和收尾
- `/read` 取回来源 -> 用户说 `/learn` -> 综合成文 -> 用户说 `/write` -> 去 AI 味
- `/health` 发现配置问题 -> 用户说“修” -> 修完可再次运行 `/health`

## Latent vs Deterministic

Waza 的技能是 judgment-heavy Markdown 工作流；确定性约束放在 `scripts/verify_skills.py`、`scripts/check_routing_drift.py` 和 `rules/*.md`。

- 需要判断、适应语境、追问用户 -> skill
- 同样输入总是同样输出、校验、列举、状态检查 -> script 或 rule

不要把 lint 检查写成 skill，也不要把“研究一个陌生领域”塞进脚本。

## Project Context

通用工程能力沉淀在 Waza。进入具体项目时，先从公开项目上下文提炼约束，再执行技能：

- `code-review` / `/check`：从 diff、README、manifest、CI、release notes 中提炼验证命令、生成物、风险和发布规则。
- GitHub issue/PR/release：由 `skills/check/SKILL.md` 处理。目标是 GitHub 时优先使用可用 GitHub 工具或 `gh`。
- Release/publish：由 `skills/check/SKILL.md` 从公开发布文档、脚本和 CI 中确认前置条件、产物和验证命令。

本地 durable memory 可以帮助理解用户偏好和旧决策，但不属于公开项目约束；必须用当前代码、日志、测试、文档或远端状态重新验证。

不要把证书路径、私钥文件名、token、个人机器路径或未公开机器配置写进 Waza。
