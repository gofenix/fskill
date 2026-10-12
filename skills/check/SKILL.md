---
name: check
description: "审查代码 diff、PR、issue 队列、发布准备、commit、push、publish 和项目审计，并用规范轴、规格轴和影响面核对。Use when users ask review/看看代码/合并前/看看issue/PR/release/push/blast radius or to implement an approved plan, with safety gates for dirty and untracked worktrees. Not for exploring ideas, debugging root causes, or prose review."
when_to_use: "review, 看看代码, 检查一下, 有没有问题, 是否需要优化, 合并前, 继续优化, 优化代码, 看看issue, 看看PR, release, publish, push, release reaction, GitHub reaction, 发布, 提交, 关闭issue, 发布表情, release表情, close issue, issue close, review my code, check changes, before merge, before release, code review, code-review, audit, project audit, 项目体检, 项目评分, 给项目打分, 深入分析项目代码, 评估项目质量, 代码质量评分, scorecard, linus review, rate this codebase, score this project, blast radius, 影响面, 双轴审查"
dispatch_intent: "代码审查、合并前检查、发布门禁、生成物审查、commit/push/release 收尾、issue/PR triage、项目质量审计"
---

# Check: 交付前把关

Prefix your first line with 🥷 inline, not as its own paragraph.

**Update check（非阻塞）**。开始前运行一次 `bash ../../scripts/check-update.sh`；如果它输出提示，把那一行转告用户，然后继续。脚本每天最多读一次公开版本文件，不发送本地数据，失败时静默。

> `/review` 是 Anthropic 内置 PR review 命令。Waza 使用 `/check` 或别名 `code-review`，不要在本技能里重新触发 `/review`。

读取 diff，找问题，能安全修的直接修，不能安全修的问用户。Done 的含义是本轮验证跑过并给出结果。

## Outcome Contract

- Outcome: 基于当前 diff、项目上下文和实时证据的 review、release decision 或 maintainer action。
- Done when: findings、fixes、shipped state 或 blockers 都用命令、产物或远端状态证明。
- Evidence: worktree status、diff、公开项目文档、manifest、CI、package 内容、release/registry 状态和当前命令输出。
- Output: findings first；需要时再给 verification 和 shipped-state summary。

## Worktree Safety Preflight

任何 review、triage、ship、release、PR 操作前，先读取：

```bash
git status --short --branch -uall
```

Treat modified, staged, and untracked files as user work. 可以读取并纳入 review surface，但不能移动、隐藏、覆盖、清理或丢弃，除非用户本轮明确批准。

默认不要运行：`git switch`、`git checkout`、`git reset --hard`、`git clean`、`git stash -u`、`git stash --include-untracked`、`git stash -a`、`git stash --all`、`gh pr checkout`。如果确实需要换分支或清理，停下来问具体操作。

在脏工作区或多 agent checkout 里 commit/push 时，先记录 `git rev-parse HEAD`。commit 前、push 前都重新读取 `git status --short --branch -uall` 和 `git rev-parse HEAD`。如果 HEAD 移动、出现未知提交或工作区被别人改过，停下来报告，不要自行 rebase、recommit 或 push。

PR 检查优先用不会切换工作区的命令：`gh pr view`、`gh pr diff`、`git fetch origin pull/<n>/head:refs/tmp/pr-<n>`、`git merge-tree`。

## Durable Context Preflight

参见 [rules/durable-context.md](../../rules/durable-context.md)。对 `/check` 来说，旧记忆可以提供用户的发布习惯、审查重点和历史 guardrails；current diff, worktree status, public docs, CI, tests, artifacts, and remote state override memory.

## Mode Picker

| User intent | Mode |
|---|---|
| “implement this plan”、`/think` 输出交接 | Plan Execution |
| diff 或 PR 已准备好，review、看看代码、合并前 | Default Review |
| 看 issues、review PRs、triage、批量处理 | Triage Mode |
| 值不值得发版、is this worth a release | Release Worthiness Analysis |
| commit、push、publish、release、close issue、发布表情 | Ship / Release Follow-through |
| audit、项目体检、项目评分、scorecard、linus review | Project Audit |
| 规范是否遵守，以及是否做了规格里的事 | Dual-Axis Review |
| 会影响哪里、blast radius、改完别的会不会坏 | Blast Radius |
| 写 PR 说明 | 读取 `references/pr-body.md` |
| 文档、PDF、自然语言 prose review | 交给 `/write` |

每个模式前都先做 Project Context Extraction。

## Project Context Extraction

Waza 的 review 能力必须独立、公开、可移植，不依赖私有机器路径。

1. 读取 diff，识别变更语言、框架、manifest、生成物、release 文件和 CI。
2. 按需读取公开项目文件：README、AGENTS/CLAUDE、package manifest、lockfile、build/test config、workflow、release notes。
3. 压缩成 review context：验证命令、受保护或生成文件、release artifacts、领域风险和 public reply rules。
4. 项目上下文和本技能规则冲突时，采用更严格的规则。
5. 如果项目文档或 CI 指定验证命令，优先用它，不要自动猜。

上下文模板见 `references/project-context.md`。发布或 maintainer work 还要填 Release Gate 2.0 matrix：review base、dirty/staged/untracked、latest tag、origin sync、version fields、generated artifacts、package/archive contents、release assets、registry/appcast/CI、public issue/PR state。证据缺失时不能说 ready。

## Plan Execution Mode

当用户批准 `/think` 计划并要求实现时使用。

1. 复述正在执行的计划标题或核心目标。
2. 重新检查 repo drift：当前分支、HEAD、worktree、关键文件是否仍符合计划。
3. 如果 drift 会改变计划安全性，停下来说明；否则直接实施。
4. 实施中保持 scope，只改计划内文件。发现新问题时判断是否阻塞，不能擅自扩大目标。
5. 完成后运行计划里的验证命令，再进入 review sign-off。

## Default Review

目标是找 bug、回归、遗漏测试、生成物漂移、发布风险和安全边界问题。Findings 必须排在最前，按严重度排序，并用文件/行号或命令输出定位。

流程：

1. 读取 diff：`git diff --stat`、`git diff`、必要时 `git diff --cached`。
2. 建立 review base：本地未提交、PR diff、或用户指定范围。
3. 读取相关实现和测试，不只看改动行。
4. 找问题，能安全 autofix 的修掉；不安全的作为 finding。
5. 跑验证命令，记录通过、失败或未运行原因。

Finding 格式：

```text
[P1] Title
File: path:line
Problem: ...
Impact: ...
Fix: ...
```

如果没有发现问题，明确说“未发现阻塞问题”，并说明测试覆盖和剩余风险。

## Dual-Axis Review

正式审查，或 diff 同时牵涉行为规格和仓库规范时使用。两条轴分开看，最后合并。小 diff 不要为了形式拆成两个子任务。

- **规范轴**：改动是否符合本仓库已经写下来的命令、生成物、风格和安全边界。证据来自 README、AGENTS、CI 和周围代码，不来自个人偏好。
- **规格轴**：改动是否做了用户、issue 或已批准计划要求的事，有没有漏掉验收条件。找不到规格时写「无规格」，不要编一个。

发现仍用 finding 格式，并在标题里标明轴。两条轴冲突时，更严格的那条留下，另一条写成假设。

## Blast Radius

用户问会影响哪里、blast radius、改完别的会不会坏时使用。

1. 从 diff 列出公开入口：导出符号、命令、路由、schema、配置键、生成物。
2. 在仓库里找调用方和下游测试，不把范围停在改动文件。
3. 把影响分成直接调用、契约变化、生成物或发布物、运行时状态。
4. 用一条能碰到最远消费者的命令证明，或写明没跑的原因。
5. 需要对外说明时套 `references/pr-body.md`。

工程立场见 [rules/principles.md](../../rules/principles.md)：看真实路径，一步一验。

## Autofix Boundary

可以自动修：

- 明确 typo、路径错误、测试期望同步、生成物 drift。
- 局部 bug，修法显然且验证成本低。
- 文档命令名、链接、metadata 同步。

不要自动修：

- 改 API 行为、数据迁移、安全策略、发布历史、用户未授权的分支/远端状态。
- 需要产品判断或架构取舍的问题。
- 会覆盖或移动用户未提交工作的操作。

## Specialist Review

必要时读取：

- `agents/reviewer-architecture.md`：架构、边界、复杂度。
- `agents/reviewer-security.md`：安全、权限、secret、危险操作。
- `references/persona-catalog.md`：选择 reviewer persona。
- `references/public-reply.md`：公共 issue/PR 回复风格。

只在风险匹配时加载，不要为了显得完整全部读取。

## Triage Mode

Issue/PR triage 先分类，后行动：

| Bucket | Meaning | Action |
|---|---|---|
| Bug | 可复现或有足够证据 | 修或排进修复 |
| Already fixed | 当前 main 已解决 | 回复证据并关闭或标记 |
| Needs info | 缺复现、版本、日志 | 问最小必要信息 |
| Accepted improvement | 低风险且符合方向 | 实施或排期 |
| Out of scope | 不符合项目边界 | 简短拒绝 |

公共回复要具体、礼貌、短，给出证据或下一步。

## Ship / Release Follow-through

发布、push、commit、close issue 前必须收集证据：

- worktree 和 HEAD 没有意外变化。
- 版本、tag、生成物、package、release asset 一致。
- CI 或本地等价验证通过。
- 远端状态明确，force push 只有用户明确授权时才允许。
- 发布后重新读取远端 release/registry/issue 状态确认。

Commit message 使用项目约定。这个仓库约定是 `{type}: {description}`，type 为 `feat`、`fix`、`refactor`、`docs`、`chore`。

## Project Audit Mode

项目体检输出 scorecard，不做大重构。

评估维度：

- 上下文面：README、AGENTS/CLAUDE、manifest、CI 是否告诉 agent 怎么安全工作。
- 验证面：是否有可复制命令，是否覆盖生成物和发布物。
- 架构面：模块边界、重复、热点、不可测试区域。
- 安全面：secret、危险命令、权限、外部系统。
- 维护性：大文件、隐式流程、陈旧文档、无人拥有的复杂区域。

每个 finding 给证据和下一步，不把风格偏好当 bug。

## Verification

优先顺序：

1. 用户或计划指定的命令。
2. 项目文档/CI 指定的命令。
3. 根据 manifest 推导的最小相关命令。
4. 无法运行时，说明原因和建议用户运行的命令。

本仓库常用：

```bash
python3 ./scripts/verify_skills.py --root .
make verify-generated
make test
make package
```

## Hard Stops

- 工作区有用户改动且目标操作会覆盖它。
- 需要 force push、删除 release、关闭 issue、改 tag，但用户没明确授权。
- 验证命令失败且失败和改动相关。
- 生成物、version、package、release asset 不一致。
- 发现 secret、token、私钥或内部路径将进入公共产物。

## Output

Review 输出顺序：

1. Findings first，按严重度排序。
2. Open questions / assumptions。
3. Verification。
4. Change summary，只作为次要上下文。

Ship 输出要说明：commit、push、release、issue/PR 状态和验证证据。PR 正文形状见 `references/pr-body.md`。

## Sources

- https://github.com/mattpocock/skills （`skills/engineering/code-review`，`skills/engineering/pr`）
- https://github.com/finografic/pstack （`skills/understand/blast-radius`）

结构借鉴，正文已改写。
