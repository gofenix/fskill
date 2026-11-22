---
name: f-mode
description: "显式进入 f-mode 后，按任务匹配原则与工作流技能，在原有授权范围内执行。Use when explicitly calling /f-mode or $f-mode to toggle session routing; 不用于未点名开启的普通请求，也不扩大操作权限。"
when_to_use: "/f-mode, $f-mode, /fskill:f-mode, /fskill f-mode, 进入 f-mode, 退出 f-mode"
disable-model-invocation: true
dispatch_intent: "显式开关会话路由并按目标选用原则与工作流技能"
---

# f-mode: 显式开启，按目标选路

首行内联带上 🥷，不要单独起段。

## 交付约定

- 目标: 用户显式开启后，在当前会话内自动匹配最贴合的技能与工程原则完成任务。
- 完成条件: 开关状态已确认或按选中流程完成且有对应实证；缺口直接说明。
- 依据: 用户目标、当前有效授权、已安装技能及本次应用到的原则。
- 交付形式: 开关操作一句确认；执行时先一句话说明选了哪条技能，原则只在确实改变具体决策时点名。

## 会话开关

默认关闭，新会话不继承。只有用户明确调用 `/f-mode`、`$f-mode`、`/fskill:f-mode` 或说“进入 f-mode”才开启；讨论或引用命令名不算开启。支持 `on`、`off`、`exit`、`status`。单条技能随时可直调，优先级高于 `f-mode` 且不关闭它。

## 选路与原则

1. 开启后按目标读 [技能路由](references/routing.md) 与 [工程原则索引](references/principles.md)，挑最贴合的技能和原则执行；不要把自己再选成子技能。
2. 动手前一句话交代选了哪个工作流技能（例如“用 hunt 查根因”）。原则只在真正改变决定时顺带点明，平时保持安静，不念清单。
3. 普通小修直接完成，不硬套厚流程；缺少某条技能或脚本时直接利用自身能力并标明缺口，不擅自下载或安装。
4. 选技能不扩大授权：方案确认不等于实施授权，修完 bug 不等于 push、发版或改动长期规则，遵循 `p-respect-boundaries` 原则（以实际安装技能为准）。
