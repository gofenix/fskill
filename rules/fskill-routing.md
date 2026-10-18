# fskill 路由

fskill 提供 21 个工作流技能，以及 catchup 进展汇报、f-mode 路由和 f-help 使用指南。未开启 f-mode 时，用 `/name` 或 `$name` 调用技能。显式输入 `/f-mode` 后，为当前会话开启路由；`/f-mode off` 关闭路由，`/f-mode status` 查询状态。直接命令优先，不改变 f-mode 的开关。新会话默认关闭路由。相似词或引用的命令不会开启 f-mode。路由前先读取 f-mode，只加载选中的技能。路由不扩大操作权限。

| 技能 | 使用场景 |
|---|---|
| f-mode | 显式控制会话路由，或开启后按目标选择技能 |
| f-help | 了解 fskill 用法、选择技能，或询问安装与定制 |
| catchup | 只读核对进展、变化、阻塞和待用户决定的事项 |
| sharpen | 校准方法、目标与约束，再完成已授权的任务 |
| think | 把想法变成可执行计划 |
| ui | 构建页面、组件，并按截图打磨视觉 |
| domain | 术语或行为边界阻碍决策 |
| map | 目标跨多个会话，推进路线还不清楚 |
| slice | 规格已经确定，需要拆成纵向切片 |
| prototype | 用可丢弃的实验检验一个假设 |
| architect | 判断代码边界是否需要拆分、合并或加深 |
| implement | 执行已批准的任务图 |
| hunt | 已有故障，修复前先证明根因 |
| optimize | 指标已经确定，每次检验一个假设 |
| check | 审查 diff、规格，或核对合并、推送、发布前的状态 |
| triage | 分类处理 issue 或外部 PR 队列 |
| verify | 维护项目验证指南和验证工具 |
| read | 读取、抓取、引用、转换或保存一个 URL 或 PDF |
| learn | 研究陌生领域、代码库或决策历史 |
| write | 改写文案，去掉 AI 味 |
| handoff | 交接或恢复当前会话 |
| retro | 记录经过验证、能改变下次做法的经验 |
| health | 审计 Agent 配置、指令漂移和 hooks |
| wizard | 指导必须由人完成的配置或迁移 |

两个技能都匹配时，读取各自 `SKILL.md` 的排除范围。仍无法判断，再询问用户。

完整路由表：<https://github.com/gofenix/fskill/blob/main/skills/RESOLVER.md>
