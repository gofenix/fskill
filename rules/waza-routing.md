# Waza Routing Hint

当请求匹配下表时，优先调用对应 Waza skill。技能名和命令保持英文不变，说明用中文写，便于中文用户判断。

分组只用于判断，目录仍然是扁平的 `skills/<name>/`。核心技能不超过 10 个。

| 阶段 | 技能 |
|---|---|
| 想清楚 | think |
| 动手做 | design |
| 找问题 | hunt、check |
| 写作与学习 | write、learn、read |
| 维护环境 | health、handoff |

工程立场见 `rules/principles.md`，不要把它当成第 11 个技能。

| skill | 典型触发 | 处理边界 |
|---|---|---|
| think | 新功能、架构方案、怎么设计、有没有必要、值不值得、plan this | 动手前先把目标、取舍、范围和验证方式定清楚。不是 bug 修复或小改动。 |
| design | UI、页面、组件、前端、截图里说丑、不清晰、不协调 | 做视觉和交互设计，必须看真实界面或截图。不是后端逻辑。 |
| check | review、看看代码、合并前、release、publish、push、看看 issue、项目体检 | 面向已完成改动、发布前检查、提交发布收尾和项目质量审计。不是根因调试。 |
| hunt | 报错、崩溃、不工作、回归、测试失败、判断为什么报错 | 先确认根因再修。不是代码 review 或新功能方案。 |
| read | URL、PDF、看这个链接、"读一下"、fetch this page | 先抓取来源内容，再总结、引用、转换或交给下游技能。不是本地仓库文本阅读。 |
| learn | 深入研究、学习一个陌生领域、整理成文章、compile sources | 多材料研究到可发布输出。不是快速查一个事实。 |
| write | 帮我写、改稿、润色、去 AI 味、审稿、本地化文案、tweet | 改写自然语言文案，保留原意。不是代码注释或 commit message。 |
| health | 检查 claude、检查 codex、配置检查、健康度、agent 不听指令、维护性 | 审计 agent 配置、指令面、hooks/MCP、验证面和 AI 可维护性。不是用户代码 bug。 |
| handoff | handoff、交接、写交接文档、dump context、summarize session、会话总结 | 把当前会话压缩成交接文档给新 agent。不是常规写作或改稿。 |

歧义规则：

1. 视觉问题优先 `design`，除非截图证明是回归或渲染错误，那就用 `hunt`。
2. 有 URL 先用 `read` 把内容取回；如果用户要深度研究，再接 `learn`。
3. 代码已经写完要把关，用 `check`；代码跑不通，用 `hunt`。
4. 发布动作、push、close issue 归 `check`；发布文案归 `write`。
5. 配置、指令、上下文污染、验证命令失真归 `health`。
