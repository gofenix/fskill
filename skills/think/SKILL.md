---
name: think
description: "把粗略想法变成可批准、决策完整的实施计划，必要时压测决策树、画模块草图或做一次性原型。Use when users ask 出方案/给方案/深入分析/怎么设计/有没有必要/值不值得/plan this/how should I/should we keep this/grill me/architect this for features, architecture, or value judgments. Not for bug fixes, root-cause debugging, or small edits."
when_to_use: "出方案, 给方案, 深入分析, 怎么设计, 用什么方案, 判断一下, 有没有必要, 值不值得, what's the best approach, plan this, how should I, should we keep this, grill me, 压测方案, architect this, 架构草图, 先做原型, throwaway prototype"
dispatch_intent: "新功能、架构方案、价值判断、动手前设计、决策完整实施计划"
---

# Think: 动手前先把方向想透

Prefix your first line with 🥷 inline, not as its own paragraph.

**Update check（非阻塞）**。开始前运行一次 `bash ../../scripts/check-update.sh`；如果它输出提示，把那一行转告用户，然后继续。脚本每天最多读一次公开版本文件，不发送本地数据，失败时静默。

把一个模糊想法变成能被批准、能直接实施的计划。不要写代码、不要脚手架、不要伪代码，除非用户已经批准计划并要求实现。

直接给判断。说清你推荐什么、为什么，以及什么证据会改变这个判断。不要用空泛开场。

## Outcome Contract

- Outcome: 用户得到一个方向明确、边界清楚、可执行的推荐或实施计划。
- Done when: 目标、成功标准、约束、已选方案、被拒绝的取舍、验证方式和执行步骤足够具体，不需要实施者重新做关键决策。
- Evidence: 当前仓库状态、项目文档、必要的官方资料、已有决策、用户约束和当前运行证据。
- Output: 一个推荐方向，或一份带假设和验证步骤的实施计划。

## Durable Context Preflight

参见 [rules/durable-context.md](../../rules/durable-context.md)。对 `/think` 来说，`decision`、`preference` 和 `principle` 可以锁定用户已批准的方向、边界和默认偏好；`pattern`、`learning` 只能作为可复用经验。Current repo state, live docs, logs, tests, screenshots, and remote state override memory.

在输出计划前，扫描项目里的 `AGENTS.md`、`CLAUDE.md`、`.claude/rules/*.md`，以及用户指向的本地 agent memory 摘要。如果计划和其中的 hard rule 冲突，要在计划里点明冲突并给出建议处理方式；如果规则阻塞计划，先停下来问用户。

## Lightweight Mode

当问题已经定义好，用户只是问“怎么修”或“怎么做这个小改动”时使用。

输出一个推荐修法，2 到 3 句话即可：改哪里、怎么改、为什么。先说最朴素的暴力做法，再给推荐做法；除非用户要求优雅，否则默认选最稳的。列出涉及文件，如果超过 5 个文件要明确提醒。说一个主要风险，然后等用户确认再实现。

如果你发现至少 3 种真正不同、取舍接近的方案，升级到完整方案模式。用户要压测决策树时用 Grill Mode，要模块草图时用 Architect Sketch，要先看见一个答案再承诺时用 Prototype Mode。

## Evaluation Mode

当用户问“要不要做”“有没有必要”“值不值得”“should we keep this”时使用。这是价值判断，不是实施计划。

先说明判断对象和判断维度：价值、风险还是取舍。然后读取当前状态：它现在做什么、谁在用、什么依赖它。不要没 grep、没读文件就发表意见。

如果是产品转向、商业化或业务方向，先评估市场、用户、分发、付费意愿和维护成本，再谈技术。不要把商业判断伪装成技术方案。

输出格式：

第一行只写一个 verdict：**Kill** / **Keep** / **Pivot**。

然后给三条理由，必须基于用户的真实约束，比如时间、动机、商业模型、维护成本。不要列一堆通用优缺点。

如果 verdict 是 **Pivot**，每个方向单独一行，必须可行动。如果 verdict 是 **Kill** 或大改，先列影响范围：文件、依赖、迁移成本，再等用户确认。

## Triage Mode

当用户一次给出多个请求、issue、截图或需求包时使用。不要把它们直接当 todo list，先分类：

| Bucket | Meaning | Action |
|---|---|---|
| Bug | 有证据的破损行为 | 修 |
| Already works | 功能已有，只是报告者没看到 | 指出现有入口 |
| Accepted improvement | 真空缺、低风险、符合方向 | 实现 |
| Cosmetic / preference | 主观偏好，没有功能影响 | 记录，不默认实现 |
| Out of scope | 违背产品边界或增加不必要复杂度 | 用一句话拒绝 |

先输出分类表，等用户确认接受的子集。最常见的浪费是把已有功能误判成缺口，所以分类前先 grep 现有入口。

## Plan Mode

当用户需要完整方案或实施计划时使用。

流程：

1. **Grounding**：确认路径和状态，读取相关入口、配置、文档、测试、已有实现。能通过仓库发现的事实不要问用户。
2. **Intent lock**：明确目标、成功标准、用户/受众、范围内外、硬约束、偏好和取舍。高影响歧义必须问。
3. **Implementation lock**：明确方案、接口、数据流、失败模式、测试、验收和回滚。计划必须 decision-complete。
4. **Attack angles**：有外部依赖、高并发或数据迁移时，检查依赖失败、10x 规模、回滚成本。方案扛不住就改方案。

## Grill Mode

用户说 grill me、压测方案、把决策问完时使用。这是把计划里还没闭合的分支问清楚，不是另开一场头脑风暴。

把方案看成决策树。每一轮只问前置已经定下来、现在就能回答的问题。每个问题带一个推荐答案，推荐答案被接受时用户只要说是。问完这一轮就停，等用户答。能从仓库里查到的事实不要问。还依赖本轮答案的下一层问题，留到下一轮。

结束条件：没有还会改变实施、却没人拍板的分支。用户确认这是共同理解之前，不要写代码。

## Architect Sketch

用户要架构草图、模块边界或类型形状，而不是「要不要做」时使用。草图先于 Plan Mode 的实施步骤。

1. 读现有入口、调用方和数据落点，把问题钉在当前代码上。
2. 只画骨架：模块、谁拥有状态、主要类型、数据怎么流。不写实现，不写伪代码。
3. 标出还没决定的接口。超过三个模块互相传数据时补一张 ASCII 图，并检查有没有环。
4. 用户认可草图之后，再进入 Plan Mode，把草图展开成可执行步骤。

## Prototype Mode

可选。用户明确要一个扔掉的原型来回答一个问题时使用。问题只有两类：状态或逻辑是否说得通，界面方向是否值得做。问错了，整份原型作废。

1. 先写清这一份原型要回答的那一个问题。
2. 放在将来会被替换的代码附近，文件名或目录标明 prototype。一次命令或一次打开就能跑。
3. 默认不持久化，不做测试，不做抽象，不做错误处理以外的健壮性。
4. 每次操作都把相关状态显示出来。
5. 结论写回计划。原型不进主线，除非用户要求留下。

## Hard Rules

- 先读代码和文档，再给方案。工程立场见 [rules/principles.md](../../rules/principles.md)：少写、先减后加、用结构表达领域。
- 不要问能从仓库里查到的问题。
- 有官方方案、框架内置能力或生态标准时，默认采用，除非能说明为什么不适合。
- 一次只推荐一个主方案；只有取舍真的接近时才列一个替代方案。
- 不输出含 TBD、TODO、later、details to be determined 的批准计划。
- 计划若涉及超过 8 个文件或 1 个新服务，明确提醒复杂度。
- 多于 3 个组件交换数据时，画一个 ASCII 图并检查循环。
- 所有 API key、token、第三方账号、外部 CLI 都要在计划里列出，不要实施到一半才要凭据。

## Gotchas

| What happened | Rule |
|---|---|
| 路径相似但不是同一仓库 | 第一轮文件操作前运行 `pwd` 或 `git rev-parse --show-toplevel` |
| 用户说“判断一下报错” | 这是调试，交给 `/hunt`，不是 Evaluation Mode |
| 用户说“可以干/直接改/implement this plan” | 视为批准已有计划，不重新争论方向；先检查 repo drift，再执行 |
| 方案依赖 MCP/CLI 却没验证工具可用 | 交付计划前验证可用性或写成明确依赖 |
| 用户拒绝方案 | 问具体哪一点不行，带着约束收窄，不从零重启 |
| Grill 一轮问了依赖本轮答案的下一层 | 只问当前能问的，问完停下 |
| 原型被当成要合并的功能 | 原型只回答一个问题，结论进计划，代码不进主线 |

## Output

批准前输出：

- **Building**: 一段话说明要做什么。
- **Not building**: 明确不做什么。
- **Approach**: 推荐方案和理由。
- **Key decisions**: 3 到 5 条关键决策。
- **Unknowns**: 只列明确延期且有 owner 的事项；阻塞项不能留在这里。

用户批准后，只输出：

```text
Plan approved. To implement: say "implement this plan". After implementation, run `/check` to review before merging or release follow-through.
```

## Sources

- https://github.com/mattpocock/skills （`skills/productivity/grilling`，`skills/engineering/prototype`）
- https://github.com/finografic/pstack （`skills/design/architect`）

结构借鉴，正文已改写。
