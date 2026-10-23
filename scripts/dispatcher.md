---
name: fskill
description: 'Dispatch explicit fskill commands, or route engineering requests within the current session after the user explicitly enters /f-mode. Direct skill commands remain available; /f-mode off stops automatic routing.'
---

# fskill: Engineering Skills Dispatcher

Prefix your first line with 🥷 inline, not as its own paragraph.

Default invocation is explicit: `/name`, `$name`, or `/fskill name`. Discussing a command or matching a topic does not invoke it. `/f-mode` explicitly enables session routing; `/f-mode off` disables it, and `/f-mode status` only reports state. New sessions start with f-mode off. Read the f-mode section for its session rules; direct commands take priority without changing f-mode state. `/catchup` reports progress. Calibration and an approved task graph are modes inside `/think`, not separate commands.

## Routing Table

<!-- routing-table:start -->
| Intent | Skill | File |
|--------|-------|------|
| 本会话进展回顾、变化与阻塞、仍待用户处理的决策和批准，只读汇报 | catchup | `skills/catchup/SKILL.md` |
| 代码与技术文档审查、合并前检查、发布门禁、项目质量审计、issue与外部PR队列、可复用验证指南与harness | check | `skills/check/SKILL.md` |
| 解答 fskill 用法、推荐技能、解释模式和定制方式 | f-help | `skills/f-help/SKILL.md` |
| 显式开启或关闭 f-mode，在会话内选择技能并按需应用工程原则 | f-mode | `skills/f-mode/SKILL.md` |
| 交接文档、handoff、会话总结、接入恢复、本人相关历史与当前状态核对 | handoff | `skills/handoff/SKILL.md` |
| Agent 配置审计、指令漂移、hooks/MCP、验证入口、AI 可维护性、必须由人完成的配置或迁移向导 | health | `skills/health/SKILL.md` |
| 错误、崩溃、回归、失败测试、异常行为、根因定位、指标优化、可信测量基线、单假设实验、收益与回归门禁 | hunt | `skills/hunt/SKILL.md` |
| 陌生领域深度研究、多来源综合、代码心智模型、历史决策研究、URL或PDF读取、网页抓取、链接摘要 | learn | `skills/learn/SKILL.md` |
| 工程复盘、改进沉淀、防复发经验、已确认术语与决策、可复用项目上下文、规则分流 | retro | `skills/retro/SKILL.md` |
| 新功能、价值判断、动手前设计、决策完整计划、术语边界、跨会话路线、纵向切片、一次性实验、代码边界、校准后按授权完成、已批准任务图实施 | think | `skills/think/SKILL.md` |
| UI、组件、页面、视觉界面、前端、截图审美问题 | ui | `skills/ui/SKILL.md` |
| 写作、改稿、润色、技术说明消歧、release notes、launch/social copy、去 AI 味 | write | `skills/write/SKILL.md` |
<!-- routing-table:end -->

## How This Works

1. Process explicit f-mode control or skill commands first. Outside f-mode, ordinary requests stay ordinary requests.
   `/f-help` answers usage questions without changing f-mode state or starting the recommended workflow; a separate explicit work request keeps its existing authorization.
2. Inside active f-mode, match the user's goal to a working skill from the table, then read its section in full. Do not route f-mode back into itself.
3. Execute within the requested scope and existing authorization. Routing does not authorize extra actions.

If the message could match multiple skills, use these disambiguation rules:

1. Most specific wins: `/ui` is more specific than `/think` for UI decisions.
2. One URL or PDF, and a multi-source investigation, both use `/learn`. One source reads that skill's single-source mode. The goal determines the mode, not a separate command.
3. Code already done vs. code broken: done/PR -> `/check`; error/broken -> `/hunt`.
4. Config/maintainability vs. code: Codex/Claude misbehaving, hooks/MCP, `/health` token usage, AI coding code rot, unclear context, missing verification, or stale verifier output -> `/health`; user code errors -> `/hunt`.
5. Release action vs. release prose: commit/tag/publish/push/release reactions/close issue -> `/check`; write release notes/changelog text -> `/write`.
6. Screenshot taste vs. screenshot regression: visual taste complaint -> `/ui`; broken render/state/generated output or used-to-work evidence -> `/hunt`.
7. From scratch vs. editing: new long-form output -> `/learn`; existing draft to polish -> `/write`.
8. "Judge this" + error -> `/hunt`; "judge this" + should we keep it -> `/think`.
9. Still ambiguous: read both skills' "Not for" sections; use exclusion. If still unclear, ask the user.

## Path Resolution

In this distribution, sub-skill scripts live at `skills/{name}/scripts/`. Resolve all relative paths from this file's directory, not from a personal home-directory skill cache.

## Chaining

Each skill stops at the requested outcome. Inside active f-mode, select the next skill only when needed for that outcome; otherwise switching requires a direct command. Complete an already authorized workflow without approval at every transition. Do not infer authorization to implement a planning-only request, publish a fix, or write durable lessons.

Common chains: `/think` -> the current agent does ordinary work, or `/think` coordinates an approved task graph -> `/check` | `/hunt` -> fix -> `/check` -> release/push/issue follow-through | `/learn` -> `/write`
