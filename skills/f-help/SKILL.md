---
name: f-help
description: "解答 fskill 的选技、调用、安装、排障与定制问题，给出有依据的说明和可直接使用的提示词。在显式调用或已开启的 f-mode 选中时使用：/f-help、$f-help 或 fskill 限定调用。不用于直接实施工程任务或一般技术问答。"
when_to_use: "/f-help, $f-help, /fskill:f-help, /fskill f-help, 调用 fskill 的 f-help, 用 fskill f-help skill, invoke fskill f-help, use fskill f-help skill"
disable-model-invocation: true
dispatch_intent: "解答 fskill 用法、推荐技能、解释模式和定制方式"
---

# f-help: 问清用法，再决定怎么用

首行内联带上 🥷，不要单独起段。

## 交付约定

- 目标: 让用户理解 fskill 的相关机制，知道当前问题该用什么、怎么调用。
- 完成条件: 问题已回答，建议与可读到的技能正文或指南一致，缺失的安装或能力已说明。
- 依据: 当前问题、[用法指南](references/guide.md)、[技能路由](references/routing.md)和宿主实际可用的技能。
- 交付形式: 先回答，再按需给一条可直接发送的提示词和对应的公开源码链接。

## 按问题读取

| 用户的问题 | 读取 |
|---|---|
| 不知道选哪条、两条技能有什么区别 | [技能路由](references/routing.md)，再读候选技能的适用与排除范围 |
| 安装更新、f-mode、catchup、sharpen、运行不对、修改技能、工程原则 | [用法指南](references/guide.md)中对应的小节 |

没有具体问题时，简短介绍 `/f-help <问题>` 和 `/f-mode <目标与验收条件>`，不展开整套手册。能从上下文判断就直接回答；确实缺少关键信息时，只问影响答案的宿主或目标。

推荐技能前，按宿主技能目录读其 `SKILL.md`；Desktop 包读根文档中的对应技能段。候选未安装时，说明路由表列的是仓库能力，给公开源码链接供确认，不假称已安装或自动下载。单独安装 f-help 也能读本目录内的指南和路由。

公开源码链接用 `https://github.com/gofenix/fskill/blob/main/` 加仓库相对路径，例如 `skills/hunt/SKILL.md`。回答基于已安装版本时说明这一点，main 可能更新；不把机器上的私有路径当作可访问链接。

## 边界

“该用什么”“怎么用”交付说明和提示词，不据此启动被推荐的流程。帮助不改变 f-mode 的开关；指南里的示例命令不算用户调用。

用户同时明确要求实际工作时，帮助只处理用法部分；实际工作按已有授权和宿主路由继续，不把它改成一份待用户重发的提示词。f-help 本身不执行其他技能，也不自动安装、改配置、发版或创建并行 agent。

不用于任意软件的客服、一般编程教学或代替目标技能执行工程任务。
