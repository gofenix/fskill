# fskill Skill Resolver

20 个工作技能，加一个 mode 入口。默认显式调用 `/name` 或 `$name`，话题相近不会启动流程。显式进入 `/mode` 后，当前会话内可按目标自动选技能；`/mode off` 退出。单条命令优先，不关闭 mode。

## 路由

| 触发 | 技能 |
|------|------|
| 用户显式进入 mode，然后按下面各表点名一条 | `skills/mode/SKILL.md` |

## 想清楚

| 触发 | 技能 |
|------|------|
| 把想法收成能执行的计划，包含追问和值不值得做 | `skills/think/SKILL.md` |
| 页面、组件、截图审美 | `skills/ui/SKILL.md` |
| 一个词或一种行为的边界说不清，而且挡着当前决定 | `skills/domain/SKILL.md` |
| 目标会跨多次会话，路线还没清 | `skills/map/SKILL.md` |
| 规格已经定了，拆成能单独演示的纵切 | `skills/slice/SKILL.md` |
| 用一次性实验验证一个具体假设 | `skills/prototype/SKILL.md` |
| 看代码边界该保持、拆开、合并还是加深 | `skills/architect/SKILL.md` |

## 做出来

| 触发 | 技能 |
|------|------|
| 按已经批准的任务图实施、合入、验证 | `skills/implement/SKILL.md` |
| 已经坏了，先证明根因再修 | `skills/hunt/SKILL.md` |
| 指标已经定了，一次只试一个假设 | `skills/optimize/SKILL.md` |

## 交出去

| 触发 | 技能 |
|------|------|
| 审 diff、技术方案、合并前、push 前、发布 | `skills/check/SKILL.md` |
| 处理 issue 和外部 PR 队列 | `skills/triage/SKILL.md` |
| 维护项目的验证指南和操作入口 | `skills/verify/SKILL.md` |

## 读和写

| 触发 | 技能 |
|------|------|
| 一份已经给出来的 URL 或 PDF | `skills/read/SKILL.md` |
| 陌生领域、一套代码或一串历史决策 | `skills/learn/SKILL.md` |
| 改稿、润色、去掉 AI 味 | `skills/write/SKILL.md` |

## 下次还能用

| 触发 | 技能 |
|------|------|
| 交出或接回当前会话现场 | `skills/handoff/SKILL.md` |
| 把已经验证、还会再犯的教训写回去 | `skills/retro/SKILL.md` |
| 查 agent 配置、指令漂移、hooks | `skills/health/SKILL.md` |
| 必须人亲手做的配置或迁移 | `skills/wizard/SKILL.md` |

## 边界

- 没进入 `/mode` 时，下面的表不自动换技能。单条命令仍然直接进入对应技能。
- 上下文装不下走 `skills/handoff/SKILL.md`。路线还没清走 `skills/map/SKILL.md`。
- 已确认的术语和 ADR 走 `skills/retro/SKILL.md`。还在厘清概念走 `skills/domain/SKILL.md`。
- 已经坏了走 `skills/hunt/SKILL.md`。没有故障、要看 diff 能不能交，走 `skills/check/SKILL.md`。
- 方案设计走 `skills/think/SKILL.md`。界面走 `skills/ui/SKILL.md`。
