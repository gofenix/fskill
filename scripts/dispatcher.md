---
name: fskill
description: 'Dispatch explicit fskill commands or route within the session after explicit /f-mode, guided by concise engineering principles. Direct commands remain available; /f-mode off stops automatic routing.'
---

# fskill: Lean Engineering Skills & Principles Dispatcher

Prefix your first line with 🥷 inline, not as its own paragraph.

Every skill takes `/name`, `$name`, `/fskill:name`, or `/fskill name`. `think`, `hunt`, and `check` may also trigger automatically when the task matches them; the other six (`f-mode`, `ui`, `write`, `learn`, `health`, `handoff`) start only on an explicit call or inside active `/f-mode`. The 8 engineering principles live in `skills/f-mode/references/principles.md` (mirrored from `rules/principles.md`), apply quietly without inflating output, and are cited only when they actually changed a concrete decision.

## Routing Table

<!-- routing-table:start -->
| Intent | Skill | File |
|--------|-------|------|
| 基于证据审查 diff/PR、项目体检、发版价值判断与发布收尾 | check | `skills/check/SKILL.md` |
| 显式开关会话路由并按目标选用原则与工作流技能 | f-mode | `skills/f-mode/SKILL.md` |
| 压缩当前会话供下一位 Agent 接手，或接入历史现场并核对最新状态 | handoff | `skills/handoff/SKILL.md` |
| 用确定性脚本审计 Agent 配置与可维护性、排查省 token 工具与做规则瘦身 | health | `skills/health/SKILL.md` |
| 用运行时证据证明根因，或对已定指标做单假设对照实验 | hunt | `skills/hunt/SKILL.md` |
| 抓取 URL/PDF 内容、多一手来源调研与代码系统梳理 | learn | `skills/learn/SKILL.md` |
| 动手前方案规划、价值判断、需求分类、grill-me 压测 | think | `skills/think/SKILL.md` |
| 构建可交互前端界面、视觉打磨与按截图逐层改进 | ui | `skills/ui/SKILL.md` |
| 中英文写作润色、发布说明与本地化文案、消除歧义与 AI 味 | write | `skills/write/SKILL.md` |
<!-- routing-table:end -->

## How This Works

1. Explicit skill commands and `/f-mode` controls take priority without closing `f-mode`. Outside `f-mode`, auto-select only `think`, `hunt`, and `check`.
2. Inside active `f-mode`, read the selected workflow section in full and consult `skills/f-mode/references/principles.md` when trade-offs or boundaries apply; never route `f-mode` into itself or expand action permissions.
3. Disambiguation:
   - Done/PR diff/release readiness -> `/check`; runtime error or broken metric -> `/hunt`; unsettled design or scope -> `/think`.
   - Visual polish/UI build -> `/ui`; render regression -> `/hunt`.
   - Fetch URL/PDF or primary-source research -> `/learn`; rewrite/localize prose -> `/write`.
   - Agent config, hooks, MCP, token tools, rule pruning -> `/health`; project code bugs -> `/hunt`.
   - Still ambiguous -> check each skill's exclusion clause or ask briefly.

## Path Resolution

In this distribution, sub-skill assets live under `skills/{name}/{references,scripts}/`. Resolve all relative paths from this file's directory, never from a home-directory cache.

## Chaining

Each skill stops when its requested outcome is complete; never chain automatically outside active `f-mode` or infer authorization for code edits, branch creation, push, release, or external writes.
