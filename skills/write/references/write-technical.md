# 技术写作：有歧义的指令

用于读者必须执行动作或区分系统状态的段落：安装步骤、操作说明、错误文案、工具描述，以及仅修改措辞的 agent 指令编辑。在混合内容的 README 或文章中，只对这些段落使用此参考；其他部分仍遵循对应语言参考并保留作者声音。

目标是让读者能还原唯一含义，不是把句子压到最短。`SKILL.md` 中的核心立场和硬性规则仍然适用。清楚的指令无需改写。审阅或改写指令从不授权执行它、改变工具行为，或重新设计提示词的权限和工作流。

## 歧义目录

只使用能解释真实误读的条目。这些是语义检查，不是禁词表，也不是每句话都要套用的清单。

| 问题 | 判断边界 | 示例 |
|---|---|---|
| 名称漂移 | 同一作用域内，同一实体或动作使用已建立的名称。不同概念保留不同名称；UI 标签、API 标识符、标志、路径和占位符保持精确原文。动词相似不能证明动作相同。 | 两个名称都指同一对象时，把 "Select the workspace. Delete the project." 改为 "Select the workspace. Delete the workspace." 保留 "Check the address. Confirm delivery."：这两个动作不同。系统区分 `cancel`、`timeout` 和 `fail` 时，文案也要区分。 |
| 主体或指代缺失 | 两个主体或对象都有可能时，点明是哪一个。主体无关或未知时保留被动语态；不要为了主动句编造主体。 | "After the worker notifies the scheduler, it retries" 需要证据说明哪个组件重试。来源没有说明时，遵循下文未解决歧义的处理方式。 |
| 条件或否定被埋没 | 每个条件、例外和禁止都应紧贴其约束的动作。保留条件是充分还是必要、边界是否包含端点。不要把限定词移到它不约束的动作上。 | "Restart only if validation passes" 不能改为 "If validation passes, restart"：前者把验证通过设为必要条件，后者要求每次通过验证都重启。 |
| 逻辑被抹平 | 保留全部与任一、且与或、否定与例外，以及每个列表项的作用域。拆句不能把可选分支改成必须依次完成的步骤。明确 "otherwise" 分支判断什么：获准尝试动作与动作成功完成是不同条件。 | "Requires an owner or an editor with approval" 没有说清 owner 是否也需批准。创建权限列表前先确认该事实。"If automatic recovery does not succeed, notify the operator" 不能改为 "If automatic recovery is disabled, notify the operator"：启用的恢复也可能失败。 |
| 顺序或依赖丢失 | 分开动作能让顺序更清楚时再拆开，并保持前提或完成条件与动作相连。紧凑且无歧义的成对动作可以留在一起。只对真正的序列编号，不给备选项制造顺序。 | "After the upload completes, delete the local copy" 必须保留 "completes"。"Start the upload. Delete the local copy" 允许过早删除。 |
| 语法过度压缩或名词堆叠 | 还原名词之间的关系，保留理解关系所需的句子成分。简短 UI 标签和成熟技术术语不算病句。 | "worker task cancellation policy" 需要上下文：取消 worker 任务的策略，与 worker 用来取消任务的策略不同。没有证据时，不选听起来更顺的一种解释。 |
| 义务或状态改变 | 区分要求、许可、能力、确信程度和时间。去掉名词化只有在这些含义保留时才有用。面向 agent 的指令不意味着建议自动成为强制要求。 | "The client must perform validation" 可改为 "The client must validate." 保留 "You should inspect the report" 和 "The request may have failed"："Inspect the report" 提高了义务程度，"The request failed" 提高了确定性。已完成、已排队和已开始的工作要区分。 |
| 无证据的补救措施 | 区分已观察错误、可能原因和建议下一步。仅修改措辞时，不添加补救措施或要求，即便它看起来合理。用户要求实质增补时，以来源或实现为据，并与保留的文本区分。 | "Connection timed out" 不能证明凭据无效。不要改成 "Your password is wrong. Sign in again." "The export can be incomplete" 本身不要求重试或完整性检查。 |

## 受控英语的适用边界

这里可以借鉴 STE 的清晰表达原则，但不能套用一套通用受控英语语法。自然时态、`sign in` 这类短语动词、领域词汇和句子节奏能准确表达含义时，都应保留。不设置固定的句子、段落或名词数量上限。英文词数限制不能直接用于中文。项目已有标点约定仍适用。

术语一致性限定在文档及其产品模型内，不建立全局一词一义词典。只有读者需要且来源确定其含义时，才定义不熟悉的术语；不要每次输出都附术语表。优先使用真实界面术语，不换成用户在屏幕上找不到的简单同义词。

## 含义检查

从读者可作出的决策逐项对比改稿和原文：谁对什么执行动作、在何种条件下、按什么顺序、具有何种许可或义务、声称得到什么结果。保留已有的数值、单位、范围、例外、不确定性和界面原文。任一版本允许了另一版本排除的动作或解释，都需在交付前消除差异。不要只为补齐这些类别添加缺失事实："supports multiple providers" 不意味着 "keeps all data on your device"；警告也不隐含未写明的恢复流程。

标点和模式检查只覆盖其实现的语法；检查干净不能证明含义保留。同义词匹配或长句只是阅读上下文的理由，不是修改命令。评估此模式时，在相同请求和运行环境下，配对一个有问题的段落和一个相近但正确的段落，再检查真实输出是否消除了歧义、是否发生禁止的改动。包含无需编辑的案例，例如 "Select Sign in"、使用相似动词的不同动作、清楚的长句，以及作者自己的定稿。用具体情境评估权限和失败分支，包括动作获准但没有成功的情况；仅保留关键词不能证明这些情境仍得到相同指令。

歧义未解决时，审阅应列明相互竞争的解释。改写时，若消除歧义需要编造事实，就保留受影响的原文；只有歧义阻塞请求的编辑时，才提出聚焦的问题。不要默选最容易的解释，也不要在正文插入编辑说明。按 `SKILL.md` 给出请求的输出形式；默认不添加改动列表、规则评分和合规报告。

## 来源与边界

此参考是独立改编，借鉴了 [asd-ste100-skill 的写作规则摘要](https://github.com/danyuchn/asd-ste100-skill/blob/master/references/writing-rules.md)及其[范围与保留原则](https://github.com/danyuchn/asd-ste100-skill/blob/master/SKILL.md)。这里只采用部分清晰表达原则，不采用该项目的严格模式或 STE 风格模式。fskill 不复制批准词典，也不认证 ASD-STE100 合规性。任务明确要求该标准时，查阅 [ASD-STE100 官方来源](https://www.asd-ste100.org/)。
