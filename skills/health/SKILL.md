---
name: health
description: "做预算友好的 agent-assisted engineering health 审计，覆盖指令/配置漂移、hooks/MCP、验证面、AI 可维护性和会话复盘。Use when users ask 检查claude/检查codex/检查pi/配置检查/健康度/retro or report agents ignoring instructions, missing validation, or code becoming hard to maintain. Not for debugging code or reviewing PRs."
when_to_use: "检查claude, 检查codex, 检查pi, Codex 配置, Pi 配置, AGENTS.md, config.toml, agent instructions, 健康度, 配置检查, 配置对不对, AI coding 腐化, 代码变烂, 维护性, 上下文混乱, 验证缺失, 验证命令失真, Claude ignoring instructions, Pi coding agent, check config, settings not working, audit config, retro, 复盘, 回顾这次"
dispatch_intent: "Agent 配置审计、Codex/Claude/Pi 指令漂移、hooks/MCP、验证面、AI 可维护性"
---

# Health: Agent-assisted engineering health

Prefix your first line with 🥷 inline, not as its own paragraph.

**Update check（非阻塞）**。开始前运行一次 `bash ../../scripts/check-update.sh`；如果它输出提示，把那一行转告用户，然后继续。脚本每天最多读一次公开版本文件，不发送本地数据，失败时静默。

按这个框架审计当前项目：

`agent config -> instruction surfaces -> tools/runtime -> verifiers -> maintainability`

目标是找出错位层，而不是把项目“打扮得更复杂”。

## Outcome Contract

- Outcome: 一份预算友好的 health report，区分 agent 配置风险和 AI 可维护性风险。
- Done when: 每个发现都写明错位层、证据、影响和可复制的行动或诊断命令。
- Evidence: health 脚本输出、项目指令、运行配置摘要、验证日志、hooks/MCP 表面和必要 live probes。
- Output: 按优先级排列的 findings，包含状态、影响和下一步；如果干净，给出 clean bill 和剩余风险。

两条线共用一份报告：

- **Agent config health**：Codex/Claude/Pi 指令漂移、权限、hooks、MCP、skills、memory supply chain。
- **AI maintainability health**：项目上下文面、verifier wrapper、生成物检查、hotspot ownership、陈旧或误导性的 durable docs。

**Output language**：按顺序选择语言：(1) 项目 agent instructions，`AGENTS.md` 优先；(2) 全局 agent instructions；(3) 用户最近语言；(4) English。

## Durable Context Preflight

参见 [rules/durable-context.md](../../rules/durable-context.md)。对 `/health` 来说，旧记忆可以解释历史配置漂移、验证缺口和用户偏好；current agent files, config, hooks, MCP status, verifier output, and repo maintainability evidence override memory.

## Budget Posture

默认先做 summary audit，不直接深挖。

升级条件：

- 用户要求 deep audit、深入检查、全量体检。
- summary audit 出现高风险发现，需要定位具体层。
- agent 明显不听指令、验证命令失真、MCP/hook 失败反复出现。

不要一上来读取大量缓存、历史会话或 raw transcripts。先让当前项目证据说话。用户要复盘这次协作时用 Retro Mode，仍然不默认去读原始会话转储。

## Summary Audit Flow

1. 运行 `skills/health/scripts/collect-data.sh auto` 收集摘要。
2. 读取项目 agent 指令：`AGENTS.md`、`CLAUDE.md`、`.codex/AGENTS.md`、`.claude/rules/*.md` 等存在的文件。
3. 检查验证入口：README、Makefile、package scripts、CI workflow、测试脚本。
4. 检查生成物和发布面：是否有验证命令覆盖，是否容易被手改。
5. 检查维护性热点：大文件、重复规则、过期文档、没有 owner 的复杂区域。
6. 输出 findings，按风险排序。

## Deep Inspection

只在需要时读取这些 inspector：

- `agents/inspector-context.md`：上下文和指令面。
- `agents/inspector-control.md`：控制面、hooks、MCP、runtime。
- `agents/inspector-maintainability.md`：AI 可维护性和热点。

每个 inspector 都要带着具体问题读，不要把它们当作固定仪式。

辅助脚本：

- `scripts/check-agent-context.sh`
- `scripts/check-doc-refs.sh`
- `scripts/check-maintainability.sh`
- `scripts/check-verifier-output.sh`
- `scripts/collect-data.sh`
- `scripts/scan_skill_security.py`：扫描技能说明面里的提示覆盖、破坏性命令和疑似密钥。输出是有界收据，不是最终裁决。

## Retro Mode

用户说 retro、复盘、回顾这次、agent 哪里费劲时使用。对象是 agent 的工作环境，不是给人写绩效，也不是代码 review。

只看当前会话里已经发生的事，加上仓库里的指令、验证命令和目录。用户点名某份笔记时才读那一份。不扫描本机的会话目录。

候选按严重度排，没有证据的类别跳过：

| 类别 | 看什么 |
|---|---|
| 导航 | 找对文件是否绕了远路，缺一个稳定指针 |
| 自动检查 | 这次错误能不能被仓库已有的 lint、测试或 CI 抓住。没有门禁本身就是发现 |
| 规范 | 机械规则应该变成检查。只有判断才留在文档里 |
| 指令膨胀 | 指令如果删掉也不会改变行为，标成无效 |
| 工具成本 | 有没有又贵又重复的查找 |

每条给证据和下一步。不要顺手改仓库，除非用户说修。

## Finding Format

```text
[P1] Finding title
Layer: agent config | instruction surface | tools/runtime | verifiers | maintainability
Evidence: exact file/command/output
Impact: why this matters
Next action: copy-pasteable command or concrete edit
```

优先级：

- **P0**：会导致 agent 破坏用户工作、泄露秘密、发布错误产物。
- **P1**：会稳定导致 agent 跑偏、验证失真或维护成本迅速上升。
- **P2**：中等风险，值得排期。
- **P3**：清理项或文档改善。

## Hard Rules

- 不要把健康审计变成代码 review；代码 bug 交给 `/hunt` 或 `/check`。
- 不要把私有路径、token、内部系统写进公共建议。
- 不要要求用户重述能从文件里读到的配置。
- 不要把“没找到证据”写成“没有问题”；写成剩余风险。
- 修改建议要落在正确层：配置问题改配置，验证问题改验证入口，维护性问题改结构或规则。

## Output

如果有问题，先列 findings，再给最小行动顺序和验证命令。如果没有问题，说清检查了什么、剩余风险是什么。

## Sources

- https://github.com/mattpocock/skills （`skills/engineering/retro`）

结构借鉴，正文已改写。
