---
name: fskill
description: 'Dispatch explicit fskill commands, apply pstack-style engineering principles (p-*), or route within the session after explicit /f-mode. Direct commands remain available; /f-mode off stops automatic routing.'
---

# fskill: Lean Engineering Skills & Principles Dispatcher

Prefix your first line with 🥷 inline, not as its own paragraph.

Every skill takes `/name`, `$name`, `/fskill:name`, or `/fskill name`. `think`, `hunt`, `check`, and the eight `p-*` principle skills may also trigger automatically when the task matches them; the other six (`f-mode`, `ui`, `write`, `learn`, `health`, `handoff`) start only on an explicit call or inside active `/f-mode`. Principle skills (`p-*`) work silently and never add the `🥷` badge or workflow headers unless asked; cite one only when it actually changed a concrete decision.

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
| 原则：质疑前提，同一卡点连败两次或变通膨胀时直接证伪共有假设 | p-attack-the-premise | `skills/p-attack-the-premise/SKILL.md` |
| 原则：结构防复发，把复发教训落成类型不变量、脚本或测试而非口号 | p-encode-in-structure | `skills/p-encode-in-structure/SKILL.md` |
| 原则：解释数字，所有量化声明附真实口径与基线，指标实验单变量对照 | p-explain-the-number | `skills/p-explain-the-number/SKILL.md` |
| 原则：先证根因，拿到偏离预期的运行时证据再做最小修复 | p-fix-root-causes | `skills/p-fix-root-causes/SKILL.md` |
| 原则：真实验收，拿目标运行入口与真实产物证据结案并写明缺口 | p-prove-it-works | `skills/p-prove-it-works/SKILL.md` |
| 原则：边界与单向门，保护脏工作区与外部不可信数据边界，未授权不越单向门 | p-respect-boundaries | `skills/p-respect-boundaries/SKILL.md` |
| 原则：先减后增，新增抽象与开关前先清理死代码与多余分层 | p-subtract-before-add | `skills/p-subtract-before-add/SKILL.md` |
| 原则：行为测试，测公开契约且新测试必须先红后绿，不靠放宽门槛变绿 | p-test-behavior | `skills/p-test-behavior/SKILL.md` |
| 动手前方案规划、价值判断、需求分类、grill-me 压测 | think | `skills/think/SKILL.md` |
| 构建可交互前端界面、视觉打磨与按截图逐层改进 | ui | `skills/ui/SKILL.md` |
| 中英文写作润色、发布说明与本地化文案、消除歧义与 AI 味 | write | `skills/write/SKILL.md` |
<!-- routing-table:end -->

## How This Works

1. Explicit skill commands and `/f-mode` controls take priority without closing `f-mode`. Outside `f-mode`, auto-select only `think`, `hunt`, `check`, and relevant `p-*` principles.
2. Inside active `f-mode`, read the selected workflow section in full and let matching `p-*` principles shape decisions; never route `f-mode` into itself or expand action permissions.
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
