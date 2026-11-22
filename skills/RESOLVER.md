# fskill Skill Resolver

9 个精简工作流技能，加 8 条 `pstack` 风格工程原则（`p-*`）。每条技能都能用 `/name` 或 `$name` 调用；`think`、`hunt`、`check` 与全部 `p-*` 原则在任务匹配时也可由模型自动选用，其余 6 条只在显式调用或开启 `/f-mode` 后进入。`/f-mode` 控制当前会话路由，`/f-mode off` 退出；直接命令优先且不关闭它。

## 路由与模式

| 触发 | 技能 |
|---|---|
| 用户显式进入 `/f-mode`，按目标选工作流与原则 | `skills/f-mode/SKILL.md` |
| 交出当前会话供接手，或接入历史现场并核对现状 | `skills/handoff/SKILL.md` |

## 核心工作流

| 触发 | 技能 |
|---|---|
| 定方案、价值判断（值不值得）、需求范围分类或 `grill me` 追问 | `skills/think/SKILL.md` |
| 报错、崩溃、回归先证根因，或已定指标单假设验证 | `skills/hunt/SKILL.md` |
| 审 diff/PR、发版价值判断、发布产物门禁、项目审计或事故重放 | `skills/check/SKILL.md` |
| 构建可交互前端界面、视觉打磨与按截图修细节 | `skills/ui/SKILL.md` |
| 抓取并核对 URL / PDF，或综合多一手来源研究系统历史 | `skills/learn/SKILL.md` |
| 润色中英文文案、发布说明或本地化文案并去 AI 味 | `skills/write/SKILL.md` |
| 审计 Agent 配置、hooks/MCP、省 token 工具、可维护性与规则瘦身 | `skills/health/SKILL.md` |

## 工程原则（`p-*`，自动触发）

| 触发信号 | 技能 |
|---|---|
| 新增抽象、开关、桥接层或重构前先删死代码 | `skills/p-subtract-before-add/SKILL.md` |
| 同一卡点连败两次或变通代码比主功能更大时停下验假设 | `skills/p-attack-the-premise/SKILL.md` |
| 报错/回归先用运行时证据定位首个预期偏离点 | `skills/p-fix-root-causes/SKILL.md` |
| 声称修完、安装就绪、截图达标或可发版前拿真实运行证据 | `skills/p-prove-it-works/SKILL.md` |
| 新增/修改测试、测公开入口先红后绿、不靠放宽预期变绿 | `skills/p-test-behavior/SKILL.md` |
| 汇报性能、配额、体积或做单假设指标优化时交代口径与基线 | `skills/p-explain-the-number/SKILL.md` |
| 反复踩坑落到类型不变量/schema/测试/脚本而非堆口号文档 | `skills/p-encode-in-structure/SKILL.md` |
| 动脏仓库、跨单向门动作（改分支/push/发版/删文件）或读不可信输入 | `skills/p-respect-boundaries/SKILL.md` |

## 边界

- 没开 `/f-mode` 时，只有 `think`、`hunt`、`check` 与 `p-*` 原则可按任务选用；`ui`、`write`、`learn`、`health`、`handoff`、`f-mode` 必须显式调用。
- 原则技能只在真的改变了某处具体决定时点名依据，平时不额外制造流程噪声，也绝不扩大操作授权。
