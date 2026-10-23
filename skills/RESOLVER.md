# fskill Skill Resolver

10 个工作技能，加 f-mode 路由和 f-help 帮助入口。默认显式调用 `/name` 或 `$name`，话题相近不会启动流程。显式进入 `/f-mode` 后，当前会话内可按目标自动选技能；`/f-mode off` 退出。单条命令优先，不关闭 f-mode。更细的做法是选中技能后的模式，不再各占一条命令。

## 路由

| 触发 | 技能 |
|------|------|
| 用户显式进入 f-mode，按目标选技能，并按需读取工程原则 | `skills/f-mode/SKILL.md` |
| 询问 fskill 用法、该选哪条、模式机制、安装排障或定制 | `skills/f-help/SKILL.md` |
| 只读核对本会话进展、变化、阻塞及仍待用户处理的事项 | `skills/catchup/SKILL.md` |

## 想清楚

| 触发 | 技能 |
|------|------|
| 把想法收成能执行的计划，包含追问和值不值得做 | `skills/think/SKILL.md` |
| 任务已经给定，校准方法、目标与约束后直接按授权工作 | `skills/think/SKILL.md` |
| 一个词或一种行为的边界说不清，而且挡着当前决定 | `skills/think/SKILL.md` |
| 目标会跨多次会话，路线还没清 | `skills/think/SKILL.md` |
| 规格已经定了，拆成能单独演示的纵切 | `skills/think/SKILL.md` |
| 用一次性实验验证一个具体假设 | `skills/think/SKILL.md` |
| 看代码边界该保持、拆开、合并还是加深 | `skills/think/SKILL.md` |
| 按已经批准的任务图实施、合入、验证。普通代码修改由当前 Agent 直接做 | `skills/think/SKILL.md` |

## 找问题

| 触发 | 技能 |
|------|------|
| 已经坏了，先证明根因再修 | `skills/hunt/SKILL.md` |
| 指标已经定了，一次只试一个假设 | `skills/hunt/SKILL.md` |

## 做检查

| 触发 | 技能 |
|------|------|
| 审 diff、技术方案、合并前、push 前、发布 | `skills/check/SKILL.md` |
| 处理 issue 和外部 PR 队列 | `skills/check/SKILL.md` |
| 维护项目的验证指南和操作入口 | `skills/check/SKILL.md` |

## 界面

| 触发 | 技能 |
|------|------|
| 从需求设计新界面，或评审、打磨现有页面、组件与截图 | `skills/ui/SKILL.md` |

## 读和写

| 触发 | 技能 |
|------|------|
| 请求读取、抓取、引用、转换或保存一份 URL 或 PDF | `skills/learn/SKILL.md` |
| 陌生领域、一套代码或一串历史决策 | `skills/learn/SKILL.md` |
| 改稿、润色、去掉 AI 味 | `skills/write/SKILL.md` |

## 下次还能用

| 触发 | 技能 |
|------|------|
| 交出或接回当前会话现场 | `skills/handoff/SKILL.md` |
| 把已经验证、还会再犯的教训写回去 | `skills/retro/SKILL.md` |
| 查 agent 配置、指令漂移、hooks | `skills/health/SKILL.md` |
| 必须人亲手做的配置或迁移 | `skills/health/SKILL.md` |

## 边界

- 没进入 `/f-mode` 时，下面的表不自动换技能。单条命令仍然直接进入对应技能。
- 上下文装不下走 `skills/handoff/SKILL.md`。路线还没清仍走 `skills/think/SKILL.md`。
- 已确认的术语和 ADR 走 `skills/retro/SKILL.md`。还在厘清概念走 `skills/think/SKILL.md`。
- 已经坏了，或指标已经定了，走 `skills/hunt/SKILL.md`。没有故障、要看 diff 能不能交，走 `skills/check/SKILL.md`。
- 方案、术语、路线、切片、一次性实验、代码边界、校准后就做、已批准任务图都走 `skills/think/SKILL.md`。可交付界面走 `skills/ui/SKILL.md`。普通代码修改由当前 Agent 直接做。
- 项目代码体检、队列和可复用验证指南走 `skills/check/SKILL.md`。Agent 配置和必须由人完成的迁移走 `skills/health/SKILL.md`。
