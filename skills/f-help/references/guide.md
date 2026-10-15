# fskill 用法指南

按问题读取对应小节。技能适用范围以实际版本的 `SKILL.md` 为准；这里解释机制，不替用户执行示例。

## 从哪里开始

知道要用什么，就直接 `/hunt`、`$think`。不确定时，问 `/f-help`；希望当前会话按目标选技能，就显式进入 `/f-mode`。

一条提示词写清目标、现场和验收条件即可，无需自己编排整条技能链。例如：

```text
/f-mode 排查登录后偶发白屏。先复现并证明根因，修复后验证刷新与重新登录都正常。
```

问“该用哪个技能查白屏”只需要帮助；明确要求排查并修复才进入实际工作。规划只交付规划，发布等操作仍按当前授权处理。

## 选技与常见区别

完整索引见[技能路由](routing.md)。只选与当前交付物有关的技能。

| 容易混淆 | 区别 |
|---|---|
| think / map / slice / implement | 想清普通方案 / 跨会话探索路线 / 将已定规格切成任务 / 协调已批准任务图的实施 |
| hunt / check / health | 证明故障根因 / 审已有改动或方案 / 审 Agent 配置、指令和可维护性 |
| ui / prototype | 完成交付界面 / 用可丢弃的实验降低一个不确定性 |
| read / learn / write | 读取单个来源 / 形成研究结论 / 改写已有文字 |
| verify / check | 维护可复用验证指南与 harness / 判断这次改动能否交付；普通跑测试无需强套 verify |
| handoff / retro | 交接或恢复现场 / 把已经验证的经验沉淀到合适位置 |

没有技能适合时用 Agent 的普通能力，不把普通改代码硬套成任务图实施，也不为简单问题串起整套流程。

## f-mode 怎么工作

- `/f-mode` 或 `/f-mode on`：显式开启当前会话路由。
- `/f-mode off`、`/f-mode exit`：关闭；`/f-mode status`：只查看状态。
- 开启后按目标读取一条技能，必要时再切换。直接 `/hunt` 等命令优先，本次直调不关闭 f-mode。
- 新会话默认关闭。安装、读到命令示例、旧交接文档都不会开启它；`/f-help` 也不改变开关。
- 这是会话内的技能约定，不是 Cursor Custom Mode，不修改宿主 Plan Mode、权限或模型配置，也不保证宿主跨会话保存状态。

只加载当前需要的技能和 reference，不把全部正文一次读完。单独安装 f-mode 不会顺带安装它推荐的技能。

## 安装与更新

先分清正在用的宿主和安装渠道；介绍用法不执行安装。完整命令与宿主插件方式见[仓库说明](https://github.com/gofenix/fskill/blob/main/README_CN.md#安装)。

| 渠道 | 调用与更新 |
|---|---|
| 直接安装技能 | Claude Code 常用 `/f-help`，Codex 用 `$f-help`；`npx skills update -g -y` 更新 |
| 宿主插件 | 按实际命名空间调用，例如 `/fskill:f-help`；使用对应宿主的插件更新入口 |
| Claude Desktop ZIP | 用发行包导入，更新时替换 ZIP；技能正文合在根文档，配套 reference 仍按相对路径读取 |
| Multica | 需导入工作区技能库并绑定到相应 Agent；机器上装过不等于工作区里可用 |

只想安装帮助，可用 `npx skills add gofenix/fskill --skill f-help -a claude-code -g -y`；整个工具集的命令见仓库说明。新加到 main 的技能可能尚未进入最新发行 ZIP，不把源码、发行包和已安装版本当成同一个状态。

## 运行不符合预期

| 现象 | 先核对什么 |
|---|---|
| 找不到 f-help 或另一条命令 | 当前宿主、安装渠道、实际技能列表、是否只装了单条；插件调用检查命名空间 |
| 仓库改了，运行还是旧正文 | 安装目录是否更新、是否需要新会话；仓库源码不自动同步所有安装副本 |
| 普通聊天没有自动换技能 | 默认就是显式调用；想在当前会话选路需先进入 f-mode |
| 新会话没有延续 f-mode | 默认关闭；重新显式进入，不从旧文件恢复开启状态 |
| 只说“通过了”，没有效果证据 | 要求给出实际运行命令、退出状态及与验收相关的结果；编译成功不能证明界面或功能正确 |
| 消耗太多上下文 | 只调用所需技能、按需读 reference；检查重复指令，必要时用 health 审计配置与 RTK、CodeGraph 可用性 |

回答当前安装问题时先查相关状态，不根据插件缓存推断已启用，也不为一句用法问题扫描整个配置目录。

## 修改自己的 fskill

源码只有仓库顶层 `skills/<name>/` 一份。正文改 `SKILL.md`，按需材料进 `references/`，确定性逻辑进 `scripts/`。通用行为规则在 `rules/`；项目约束留在目标项目。

改作用域或触发词时同步 `skills/RESOLVER.md`。在仓库根运行 `make regenerate` 更新清单、路由副本和统一许可声明，再运行 `make test`；需要分发时用 `make package` 生成 ZIP。不要重建 `plugins/fskill` 技能镜像，也不要手改生成的路由或 NOTICE.md。修改仓库后，按实际渠道更新安装副本。

复盘已经验证的纠偏可用 `/retro`；不要把一次临时任务或未经验证的猜测固化成全局规则。许可证维护源是根 LICENSE，单技能携带生成的 NOTICE.md；致谢不替代原许可声明。

## 工程原则与工作流

f-mode 用[短原则索引](https://github.com/gofenix/fskill/blob/main/skills/f-mode/references/principles.md)连接现有正文：先减后增、质疑前提、真实验收、行为测试、解释数字、结构性防复发。工程任务按条件读取，普通问答和模式开关省略。索引只负责发现，详细规则继续维护在各自技能里。

可以这样定向纠偏：`/f-mode 用“质疑前提”重新检查这两次修复失败的原因；只诊断，不改文件。` 仅点名原则不会开启 f-mode。只读适用正文，读取不等于启动所属技能的流程；缺少对应技能时说明缺口，不自动安装。

原则真正改变选择时，f-mode 会结合证据说明，例如“质疑前提 → 放弃第三次调参数，先核对是否重复提交；日志中同一操作出现两次”。只引用本轮实际读过并应用的正文，没有影响就不凑报告栏目。没有独立 `/principle-*` 命令；pstack 的角色模型配置和 Custom Mode 也不属于 fskill。

压缩技能先合并重复提醒和模板，保留适用条件、操作边界、完成条件与单技能安装约束，用代表性任务对照后再删减；不把 10–20 行当硬指标。

说明与来源：[f-mode](https://github.com/gofenix/fskill/blob/main/skills/f-mode/SKILL.md)、[通用行为规则](https://github.com/gofenix/fskill/blob/main/rules/anti-patterns.md)、[贡献与分发约定](https://github.com/gofenix/fskill/blob/main/AGENTS.md)。
