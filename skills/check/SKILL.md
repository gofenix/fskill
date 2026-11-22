---
name: check
description: "基于现场证据审查 diff、PR、发布就绪状态与项目代码健康；只判断发版价值或按授权交付。Use when reviewing changes, assessing release readiness, auditing a project, or handling PRs and releases; 无需用户点名也可按任务选用。不用于尚未定性的方案设计或根因调试。"
when_to_use: "/check, $check, /fskill:check, /fskill check, code review, code-review, 审查代码, 值不值得发版, 发布收尾"
disable-model-invocation: false
dispatch_intent: "基于证据审查 diff/PR、项目体检、发版价值判断与发布收尾"
---

# Check: 交付前把关

首行内联带上 🥷，不要单独起段。

> `/review` 是宿主内置 PR 审查命令；本工作流使用 `/check` 或 `$check`，不转调 `/review`。

读取 diff，基于证据报告问题；仅在已有明确授权且范围内时局部修复并实证。所有结论贯彻「真实验收」与「边界与单向门」。

## 交付约定

- 目标: 靠真实 diff、测试、生成物与远端状态，输出可验证的审查结论、项目审计、发版价值判断或已交付状态。
- 完成条件: 每条问题落到文件行号或命令输出；修改或交付项均在最新状态复验且写明剩余缺口。
- 依据: 工作区状态、diff、项目公开文档/CI、产物与包内容、远端 PR/release 状态。
- 交付形式: 问题按 `P0`–`P3` 严重度置顶（无阻塞问题时明说“未发现阻塞问题”并交代测试覆盖与缺口），其次是验证结果与剩余风险。

## 长期上下文预检

先读取 [长期上下文预检](references/durable-context.md)。记忆仅作背景；当前 diff、公开文档、CI 与实测输出优先于旧记忆，旧记忆不授予任何修改或发布权限。

## 调用边界

显式调用、`/f-mode` 选中，或任务明确是要审 diff/PR/成稿 spec、判别“值不值得发版”、发布前检查、执行已授权的发布收尾、做项目审计或台账重放时进入；隐式选用前一句话交代理由。**不扩大授权**：只审或只判发版价值时不改文件；方案未定走 `/think`，根因排错走 `/hunt`，纯语言润色建议显式调用 `/write`，Agent 配置与规则瘦身用 `/health`。

## 工作区安全预检

任何审查、交付或 PR 操作前，先执行：

```bash
git status --short --branch -uall
```

把已修改、已暂存和未跟踪文件都视为用户工作；只可读取审查，不得擅自移动、覆盖、清理或丢弃。未获覆盖该动作的明确授权，绝不运行：`git switch`、`git checkout`、`git reset --hard`、`git clean`、`git stash -u`、`git stash --include-untracked`、`git stash -a`、`git stash --all`、`git worktree add`、`git worktree remove`、`gh pr checkout`。查外部 PR 优先用只读方式：`gh pr view`、`gh pr diff`、`git fetch origin pull/<n>/head:refs/tmp/pr-<n>`、`git merge-tree`。

在已有变更或多 agent 目录提交/推送前记录 `git rev-parse HEAD`，commit 前与 push 前重新核对 `git status --short --branch -uall` 和 `git rev-parse HEAD`；若 `HEAD` 意外移动或出现未知改动，停下来报告，不擅自 rebase 或强推。

## 审查与把关

1. **提取公开上下文**：从目标仓库公开的 `README`、`AGENTS/CLAUDE`、包清单、锁文件、构建脚本与 CI 工作流提取验证命令、受保护生成物和路径风险等级；不依赖本机私有路径。
2. **核对全量范围与需求**：冻结当前 `HEAD` 与待审 diff 列表；同时对照“需求真的要做对什么”与“代码有没有缺陷/多余抽象/安全漏洞/生成物漂移”。修改前按自动修复边界核对授权，若中途修过代码则重审当前版本。
3. **常见高危模式按需深读**：diff 涉及安装重试、非原子替换、破坏性通配/删除、门禁放宽、重复推导、视觉对比、测试路径失真或依赖变更时，读取 [审查模式](references/review-patterns.md)。TypeScript 变更对照「结构防复发」查状态与边界，只读审查不把排版偏好判成 bug。
4. **发版判断与发布产物**：仅问“值不值得发版”时给出 **该发 / 可以等 / 不该发** 与三条真实约束理由（影响、风险、时机），不顺手发布。涉及打包、签名、公证、release asset、版本号与发版就绪核对时读取 [发布产物](references/release-artifacts.md)；缺证据直接标缺口，**不能说已就绪**。
5. **项目审计模式**：做项目质量体检时定位已加载 `check` 目录为 `CHECK_DIR`，运行 `python3 "$CHECK_DIR/scripts/audit_signals.py" --root <project>` 并结合项目上下文核查；报告不带无契约分数的可行动问题。
6. **事故台账与重放**：项目维护 `docs/incidents.md` 且缺陷曾到达用户，或需评估 reviewer/技能变化后的回归时，读取 [事故台账](references/incident-ledger.md)。

## 验证

执行优先级：用户或计划指定命令 -> 项目文档/CI 指定命令 -> 由清单推导的最小相关命令 -> 无法运行则列出具体原因与建议命令。CLI、安装器、技能与打包变更必须检查真实安装后入口，单测通过不代替真机/隔离环境运行。
