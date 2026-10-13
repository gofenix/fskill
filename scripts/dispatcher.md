---
name: fskill
description: 'Dispatch explicit fskill commands, or route engineering requests within the current session after the user explicitly enters /f-mode. Direct skill commands remain available; /f-mode off stops automatic routing.'
---

# fskill: Engineering Skills Dispatcher

Prefix your first line with 🥷 inline, not as its own paragraph.

Default invocation is explicit: `/name`, `$name`, or `/fskill name`. Discussing a command or matching a topic does not invoke it. `/f-mode` explicitly enables session routing; `/f-mode off` disables it, and `/f-mode status` only reports state. New sessions start with f-mode off. Read the f-mode section for its session rules; direct commands take priority without disabling f-mode.

## Routing Table

<!-- routing-table:start -->
| Intent | Skill | File |
|--------|-------|------|
| 主动架构机会识别、代码边界改进、模块深化、调用方认知成本、依赖与测试接缝、备选接口比较 | architect | `skills/architect/SKILL.md` |
| 代码与技术文档审查、合并前检查、已有PR状态与持续跟进、发布门禁、平台打包产物、mac 打包、macOS/Android 产物、release asset、commit/push/release 收尾、项目质量审计 | check | `skills/check/SKILL.md` |
| 主动领域建模、统一领域语言、术语歧义、行为与事件、bounded context、领域概念边界 | domain | `skills/domain/SKILL.md` |
| 显式开启或关闭 f-mode，在会话内自动选择已安装技能 | f-mode | `skills/f-mode/SKILL.md` |
| 交接文档、handoff、会话总结、接入恢复、本人相关历史与当前状态核对 | handoff | `skills/handoff/SKILL.md` |
| Agent 配置审计、Codex/Claude/Pi 指令漂移、hooks/MCP、验证面、AI 可维护性 | health | `skills/health/SKILL.md` |
| 错误、崩溃、回归、失败测试、异常行为、根因定位 | hunt | `skills/hunt/SKILL.md` |
| 批准任务图实施、ready frontier、coordinator、隔离worktree、integration branch、merger、阻塞解锁、实施恢复与集成验证 | implement | `skills/implement/SKILL.md` |
| 陌生领域深度研究、多来源综合、代码心智模型、历史决策研究、从材料到可发布输出 | learn | `skills/learn/SKILL.md` |
| 跨会话决策图、路线未明目标、共享决策票、依赖前沿、范围内迷雾、决策上下文恢复 | map | `skills/map/SKILL.md` |
| 持续指标优化、hillclimb、性能与成本改善、评测分数提升、可信测量基线、单假设实验、收益与回归门禁、保留撤回 | optimize | `skills/optimize/SKILL.md` |
| 一次性实验、领域状态与行为演示、UI 结构方案比较、验证明确设计假设 | prototype | `skills/prototype/SKILL.md` |
| URL 或 PDF 读取、网页抓取、链接摘要、Markdown 提取 | read | `skills/read/SKILL.md` |
| 工程复盘、改进沉淀、防复发经验、已确认术语与决策、可复用项目上下文、规则分流 | retro | `skills/retro/SKILL.md` |
| 确定规格、已定讨论固化、纵向切片、tracer bullet、实施票据、阻塞依赖、任务图、expand-contract迁移 | slice | `skills/slice/SKILL.md` |
| 新功能、架构方案、价值判断、动手前设计、决策完整实施计划 | think | `skills/think/SKILL.md` |
| issue/外部 PR intake、持续分诊、补充信息后重入、agent-ready brief、类别与处理状态 | triage | `skills/triage/SKILL.md` |
| UI、组件、页面、视觉界面、前端、截图审美问题 | ui | `skills/ui/SKILL.md` |
| 项目验证资产搭建、验证指南维护、launch/doctor/drive/evidence/cleanup、用户功能地图、harness漂移与现场覆盖 | verify | `skills/verify/SKILL.md` |
| 人工操作交接、交互式配置向导、凭据采集、依赖有序的人工迁移步骤 | wizard | `skills/wizard/SKILL.md` |
| 写作、改稿、润色、技术说明消歧、release notes、launch/social copy、去 AI 味 | write | `skills/write/SKILL.md` |
<!-- routing-table:end -->

## How This Works

1. Process explicit f-mode control or skill commands first. Outside f-mode, ordinary requests stay ordinary requests.
2. Inside active f-mode, match the user's goal to a working skill from the table, then read its section in full. Do not route f-mode back into itself.
3. Execute within the requested scope and existing authorization. Routing does not authorize extra actions.

If the message could match multiple skills, use these disambiguation rules:

1. Most specific wins: `/ui` is more specific than `/think` for UI decisions.
2. One URL or PDF to fetch or summarize -> `/read`; multi-source investigation -> `/learn`. The goal determines the skill, not the presence of a URL.
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

Common chains: `/think` -> implement approved plan -> `/check` | `/hunt` -> fix -> `/check` -> release/push/issue follow-through | `/read` -> `/learn` -> `/write`
