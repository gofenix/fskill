---
name: hunt
description: "在修复前先找到错误、崩溃、回归、失败测试和异常行为的根因。硬问题按反馈环、缩小、假设、观测、修复走。Use when users ask 排查/报错/崩溃/不工作/回归/判断为什么报错/diagnose, or say something used to work and now fails. Not for code review or new features."
when_to_use: "排查, 报错, 崩溃, 不工作, 回归, 判断为什么报错, 测试失败, 以前可以, used to work, error, crash, failing test, regression, broken behavior, why broken, stale cache, diagnose, 缩小复现"
dispatch_intent: "错误、崩溃、回归、失败测试、异常行为、根因定位"
---

# Hunt: 先抓根因，再动刀

Prefix your first line with 🥷 inline, not as its own paragraph.

**Update check（非阻塞）**。开始前运行一次 `bash ../../scripts/check-update.sh`；如果它输出提示，把那一行转告用户，然后继续。脚本每天最多读一次公开版本文件，不发送本地数据，失败时静默。

Hunt 的核心是：先证明为什么坏，再修。不要看到报错就猜修法，不要用一堆尝试覆盖不确定性。

## Outcome Contract

- Outcome: 根因被定位并用当前证据证明，随后给出最小修复或明确阻塞。
- Done when: 复现路径、根因、修复点和验证命令都在本轮被说明；如果不能修，阻塞条件具体可复现。
- Evidence: 错误日志、测试输出、trace、相关代码、最近 diff、生成物、运行时状态、截图或用户给出的复现步骤。
- Output: 根因说明 + 修复或补丁摘要 + 验证结果；仅诊断请求只输出诊断。

## Durable Context Preflight

参见 [rules/durable-context.md](../../rules/durable-context.md)。对 `/hunt` 来说，旧记忆可以提供历史失败模式、常见命令和用户偏好的诊断边界；但 current logs, tests, code, repro steps, screenshots, and runtime state override memory.

## Triage

先判断问题类型：

| Symptom | First move |
|---|---|
| 报错或 stack trace | 读完整错误、定位抛出点、找最近调用链 |
| 测试失败 | 跑最小失败测试，确认是断言、环境、fixture 还是生成物 |
| 回归 | 找旧好版本、最近改动、行为差异 |
| UI 截图错误 | 先判断是审美问题还是渲染/状态回归 |
| 缓存或队列异常 | 检查输入、输出、缓存 key、重试和并发边界 |

如果用户明确说“只做诊断”，不要改文件。

## Investigation Flow

1. **Confirm workspace**：运行 `pwd` 或 `git rev-parse --show-toplevel`，确认当前仓库。
2. **Read the failure**：读取用户给的日志、测试输出、截图、命令和相关文件。不要只看最后一行。
3. **Reproduce narrowly**：能跑最小命令就跑最小命令。全量命令只在必要时运行。
4. **Trace cause**：沿输入、状态、调用链、输出走一遍，找第一个背离预期的点。
5. **Prove it**：用日志、断点、临时只读检查、单测或对比证明根因。
6. **Fix minimally**：只改和根因直接相关的代码。
7. **Verify**：先跑复现命令，再跑相关回归测试。验证失败就回到根因，不要扩大改动。

## Phase Gates

硬缺陷、时好时坏的失败或性能回归时使用。一句栈跟踪仍走上面的短流程。不要跳过相位，除非写明为什么这一相已经满足。

1. **反馈环**：先有一条能稳定变红的最小命令或操作。没有环就先造环，而不是改产品代码。
2. **复现并缩小**：去掉无关输入、步骤和数据，直到再删一步就不失败。
3. **假设**：写下可证伪的原因，一次一个，并写明什么观察会否定它。
4. **观测**：加最小日志或探针检验假设。秘密打码。这一相不改产品行为。
5. **修复加回归**：根因确定后做最小修复，并留下能抓住它的测试或命令。
6. **清理**：去掉临时探针。再跑当初变红的那条命令，确认变绿。

做不到第 1 相时停下来，说明缺的是复现，不是修法。工程立场见 [rules/principles.md](../../rules/principles.md)。

## Debugging References

- 常见失败模式：`references/failure-patterns.md`
- 日志与观测技巧：`references/logging-techniques.md`
- 输入法和 Unicode 问题：`references/ime-unicode.md`
- 渲染问题定位：`references/rendering-debug.md`

按问题类型只读需要的参考，不要把参考文件当作 checklist 全跑一遍。

## Hard Rules

- 不要在没有根因证据时修。
- 不要把“测试通过不了”归因于环境，除非你能证明环境差异。
- 不要为了清理现场运行 `git reset --hard`、`git clean` 或丢弃用户改动。
- 不要把多个独立问题混成一个大修。
- 修复后必须跑触发问题的命令或说明为什么不能跑。
- 截图证明的是事实，不是风格偏好；如果是审美问题，交给 `/design`。

## Output

默认输出：

```text
🥷 根因：...

修复：...

验证：
- `command`: passed/failed

剩余风险：...
```

只诊断时输出：

```text
🥷 诊断结论：...

证据：
- ...

下一步建议：...
```

## Sources

- https://github.com/mattpocock/skills （`skills/engineering/diagnosing-bugs`）

结构借鉴，正文已改写。
