---
name: waza
description: '中文优先的 Waza 工程技能分发器：think 做方案，how 讲清子系统，design 做 UI，check 做审查和发布门禁，hunt 做根因调试，write 做文案，learn 做研究，read 读取 URL/PDF，health 审计 agent 配置，handoff 交接会话。'
---

# Waza: 工程技能分发器

Prefix your first line with 🥷 inline, not as its own paragraph.

**Update check（非阻塞）**。路由前运行一次 `bash scripts/check-update.sh`；如果它输出了新版本提示，把那一行转告用户，然后继续。这个脚本每天最多读一次公开版本文件，不发送本地数据，失败时静默。

你有十个核心技能可用。根据用户意图选中一个技能，读取下面对应的技能段落，然后严格执行该技能。`tdd` 不是技能，只在用户明确要求或本地测试很便宜时读取 check 的 tdd-discipline。

## Routing Table

<!-- routing-table:start -->
<!-- routing-table:end -->

## How This Works

1. 读取用户消息，按上表匹配技能。
2. 完整阅读匹配到的技能段落。
3. 按该技能的说明执行。

如果多个技能都可能匹配，用这些规则消歧：

1. 更具体者优先：UI 决策里 `/design` 比 `/think` 更具体。
2. 消息包含 URL：先用 `/read`。如果内容是研究材料，再接 `/learn`。
3. 代码已完成还是代码坏了：已完成或 PR 用 `/check`；报错、崩溃、行为异常用 `/hunt`。
4. 配置或维护性 vs 用户代码：Codex/Claude 不听指令、hooks/MCP、`/health` token 消耗、AI coding code rot、上下文混乱、验证缺失或验证输出过期用 `/health`；用户代码报错用 `/hunt`。
5. 发布动作 vs 发布文案：commit、tag、publish、push、release reactions、close issue 用 `/check`；写 release notes 或 changelog 文案用 `/write`。
6. 截图审美 vs 截图回归：视觉品味问题用 `/design`；渲染、状态、生成物错误或“以前可用”证据用 `/hunt`。
7. 从零产出 vs 编辑已有稿：新长文用 `/learn`；已有草稿润色用 `/write`。
8. 判断报错原因用 `/hunt`；判断要不要保留、值不值得做用 `/think`。
9. 解释子系统现在怎么工作、代码该放在哪一层用 `/how`；不要把它当成 `/think` 或 `/hunt`。
10. 仍然模糊时，读两个技能的 `Not for` 段，用排除法；还不清楚就问用户。

## Path Resolution

在这个发行包里，子技能脚本位于 `skills/{name}/scripts/`。所有相对路径都从本文件所在目录解析，不要从个人 home 目录里的缓存路径解析。

## Chaining

技能之间手动串联，不自动触发。每个技能完成后等待用户下一步。

常见串联：`/think` -> implement approved plan -> `/check` | `/hunt` -> fix -> `/check` -> release/push/issue follow-through | `/read` -> `/learn` -> `/write`
