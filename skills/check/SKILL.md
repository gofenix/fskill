---
name: check
description: "审查代码、方案、发布和项目质量，处理 issue 与外部 PR 队列，并维护可复用的验证指南。在显式调用或已开启的 f-mode 选中时使用：/check、$check 或 fskill 限定调用。不用于尚未确定的设计取舍、根因调试或文字润色。"
when_to_use: "/check, $check, 调用 fskill 的 check, 用 fskill check skill, invoke fskill check, use fskill check skill"
disable-model-invocation: true
dispatch_intent: "代码与技术文档审查、合并前检查、发布门禁、项目质量审计、issue与外部PR队列、可复用验证指南与harness"
---

# Check: 交付前把关

首行内联带上 🥷，不要单独起段。

> `/review` 是 Anthropic 内置 PR 审查命令。fskill 使用 `/check` 或 `$check`，不要在本技能里重新触发 `/review`。

读取 diff，基于证据报告问题；用户已授权修复时，在授权范围内修改并验证。完成的含义是给出验证结果或明确的验证缺口。

## 调用边界

首次进入本技能时，须由用户显式输入 `/check`、`$check`、`调用 fskill 的 check`、`用 fskill check skill`、`invoke fskill check`、`use fskill check skill`，或 Desktop 根分发器已从 `/fskill check` 选中本技能，或当前会话里用户已进入 `/f-mode` 且 f-mode 点名了本技能。同一任务中的回答、补充、纠正和继续请求沿用已显式调用的技能，无需每轮重复命令；f-mode 关闭时，新任务或切换技能仍需显式调用；f-mode 开启时可由 f-mode 按当前目标重新选择。若宿主仅因语义相似自动加载本技能，不应用下文流程，按普通 Agent 请求继续处理。

## 交付约定

- 目标: 基于当前 diff、项目上下文和实时证据的审查、发布判断或维护操作。
- 完成条件: 发现、修复、已交付状态或阻塞都用命令、产物或远端状态证明。
- 依据: 工作区状态、diff、公开项目文档、manifest、CI、包内容、发布或 registry 状态和当前命令输出。
- 交付形式: 先给发现；需要时再给验证和已交付状态摘要。

## 工作区安全预检

任何审查、交付、发布或 PR 操作前，先读取：

```bash
git status --short --branch -uall
```

把已修改、已暂存和未跟踪文件都视为用户工作。可以读取并纳入审查范围，但不能移动、隐藏、覆盖、清理或丢弃，除非用户已明确授权该操作及其范围。

默认不要运行：`git switch`、`git checkout`、`git reset --hard`、`git clean`、`git stash -u`、`git stash --include-untracked`、`git stash -a`、`git stash --all`、`gh pr checkout`。如果确实需要换分支或清理，先核对该操作及范围是否已有明确授权；缺少授权时再问具体操作。

在脏工作区或多 agent checkout 里 commit/push 时，先记录 `git rev-parse HEAD`。commit 前、push 前都重新读取 `git status --short --branch -uall` 和 `git rev-parse HEAD`。如果 HEAD 移动、出现未知提交或工作区被别人改过，停下来报告，不要自行 rebase、recommit 或 push。

PR 检查优先用不会切换工作区的命令：`gh pr view`、`gh pr diff`、`git fetch origin pull/<n>/head:refs/tmp/pr-<n>`、`git merge-tree`。

## 长期上下文预检

可选读取长期上下文，但只作为背景。对 `/check` 来说，旧记忆可以提供用户的发布习惯、审查重点和历史约束；当前 diff、工作区状态、公开文档、CI、测试、产物和远端状态优先于旧记忆。不要把旧记忆中的命令、远端状态或发布结论当成当前事实。

## 模式选择

| 用户意图 | 模式 |
|---|---|
| diff 或 PR 已准备好，review、看看代码、合并前 | 默认审查 |
| 查已有 PR 状态、处理未决讨论或持续推进到就绪 | PR 跟进，按实际请求区分只读状态、讨论处理与持续推进 |
| 已成稿技术方案、PRD、spec 的正确性、一致性、完整性审查 | 技术文档审查 |
| issues/外部 PR 队列分类、补充信息重入、准备实施契约 | 读取 [队列](references/modes/triage/MODE.md)；已有 diff 的审查仍走默认审查 |
| 建立或维护可复用的验证指南和操作入口 | 读取 [验证指南](references/modes/verify/MODE.md)。只跑一次已有测试不进入这一节 |
| 值不值得发版、is this worth a release | 发版价值判断 |
| commit、push、publish、release、close issue、发布表情 | 交付与发布收尾 |
| 打包、mac 包、dmg、notarize、apk、aab、release asset | 发布产物检查 |
| audit、项目体检、项目评分、scorecard、linus review | 项目审计 |
| 只检查措辞、语法、可读性、去 AI 味或本地化文案 | 建议用户显式调用 `/write` |

每个模式前都先做项目上下文提取。普通“实施这个计划”由当前 Agent 承接，不因此进入 `/check`。

## 项目上下文提取

从 diff 和公开项目上下文提炼审查依据，包括 README、AGENTS/CLAUDE、manifest、锁文件、构建与测试配置、CI 和发布说明，直到明确验证命令、生成或受保护文件、发布产物、领域风险及公共回复规则。不依赖私有机器路径或未公开指令。

- 项目上下文和本技能规则冲突时，按宿主指令优先级、规则适用范围和本任务已有授权判断；不能仅因某条更严格就覆盖有效授权。仅澄清仍未解决、会影响操作的冲突。
- 优先采用项目文档或 CI 指定的验证命令，并读取实际工作流。文档声称 CI 覆盖不算证据；检查、工具或平台仅在本地或 CI 一侧运行时，一侧通过不能证明另一侧通过。

上下文模板见 `references/project-context.md`。发布就绪判断、打包或发布还要填发布检查 2.0 矩阵；证据缺失时不能说已就绪。仅 commit/push 按 `references/maintainer-workflows.md` 验证源码交付，不要求无关的发布产物或 registry 状态。

## 默认审查

目标是找 bug、回归、遗漏测试、生成物漂移、发布风险和安全边界问题。发现必须排在最前，按严重度排序，并用文件/行号或命令输出定位。

流程：

1. 读取 diff：`git diff --stat`、`git diff`、必要时 `git diff --cached`。
2. 建立审查基准：本地未提交、PR diff、或用户指定范围。
3. 读取相关实现、测试和提交说明，不只看改动行；先确认行为变化是否符合本次意图，再从适用需求反查实现和验证证据，找出未进入 diff 的遗漏、部分实现或超范围行为，再判定回归。默认检查过度设计：逐项判断新增文件、选项、fallback、层次或抽象是否为目标所需，报告有证据可删的部分，不自动删除。
4. 报告问题；修改前按自动修复边界核对授权。多个发现共享同一根因时，先给出保留、调整、替换或证据不足的判断，再列局部修法；用户或项目已明确选定的路线不重新争论，审查结论不授权扩大为重构。
5. 跑验证命令，记录通过、失败或未运行原因。

规范和需求是两个独立视角：符合项目标准不能证明需求做对，满足需求也不能豁免规范。按需求逐项找实现与验证，再从代码检查规范、回归和额外行为。复杂变更可分别委派，最终按严重度合并同根因发现，不强制两名 reviewer 或固定篇幅。

diff 涉及安全前提、重复故障、视觉对比、异步完成、删减归并、安装与重试、破坏性匹配、重复计算、测试路径失真、依赖变更或验证门槛调整时，按需读取 [references/review-patterns.md](references/review-patterns.md) 的对应段落；复杂独立审查的分片与裁决也在该参考。实际委派 reviewer 前读取 [委派预算](references/delegation-budget.md)，配置不授予委派权限。TypeScript 变更按需读取 [references/typescript.md](references/typescript.md)，沿目标项目的类型、解析与兼容约定检查。

涉及 CLI、安装器、配置或环境变量时，验证命令契约和真实安装路径，修改终端文字或排版后重新运行命令、读取输出；修改型命令还要检查失败、重试与回退边界。涉及技能、插件、包、marketplace 或生成镜像时，重建并检查产物，在隔离环境验证安装后的入口、脚本与引用能解析；库测试、manifest JSON 和本地导入不能替代安装验证，缺失层明确报告。

问题格式：

```text
[P1] 标题
文件：path:line
问题：...
影响：...
修复：...
```

如果没有发现问题，明确说“未发现阻塞问题”，并说明测试覆盖和剩余风险。

## 技术文档审查

审查已经写好的技术方案、PRD、spec 或设计文档时，目标是验证内容能否正确指导实现，不是润色文字。

1. 以用户指定文档为审查基准，提取字段定义、状态、流程、边界条件、校验规则和示例。
2. 按请求读取相关需求、代码、schema、接口、测试和 CI，验证文档主张与当前实现是否一致。
3. 交叉检查术语与字段定义、适用矩阵、执行顺序、不变量、异常路径和示例，定位矛盾、遗漏和不可实现之处。
4. 先列发现，并用文档行号、代码位置或命令证据说明；只改用户授权的文档或实现。
5. 如果核心方案仍未确定，且用户要比较方向或重新做取舍，建议显式调用 `/think`；如果只需改措辞和可读性，建议显式调用 `/write`。

## 自动修复边界

仅审查或判断是否可发布的请求，默认交付发现和建议。修法简单不代表获得修改授权。

同一任务已有明确且仍有效的修复授权时，直接完成范围内的局部 bug、文档、路径、metadata 和必要生成物修复，并运行相关验证；不因换轮或进入审查流程而重复索要批准。用户随后收窄或撤回授权时，以新边界为准。只有规范支持期望变化时才更新测试，不能为让测试变绿而改期望。

新增产品取舍、扩大重构范围、破坏性操作或外部状态变更需要各自适用的授权；发现问题本身不提供这些授权。保护无关的用户改动，遵循工作区安全预检。

## 专项审查

必要时读取：

- `agents/reviewer-architecture.md`：架构、边界、复杂度。
- `agents/reviewer-security.md`：安全、权限、secret、危险操作。
- `references/persona-catalog.md`：选择审查视角。
- `references/public-reply.md`：公共 issue/PR 回复风格。

只在风险匹配时加载，不要为了显得完整全部读取。

## PR 跟进与交付收尾

在 PR 跟进、交付或发布收尾模式下读取 [references/maintainer-workflows.md](references/maintainer-workflows.md) 的对应章节；查状态不附带修改、公共回复或合并授权。

## 项目审计模式

仅在此模式下读取 [references/maintainer-workflows.md](references/maintainer-workflows.md) 的对应章节。

## 验证

优先顺序：

1. 用户或计划指定的命令。
2. 项目文档/CI 指定的命令。
3. 根据 manifest 推导的最小相关命令。
4. 无法运行时，说明原因和建议用户运行的命令。

对脚本或 bug 修复，先用已知正确和已知错误的输入验证检查器，预期结果应来自需求而非当前实现。Agent 指令的关键词检查只能证明文本保留；行为验证要检查工具操作、产物和禁止的副作用，并在相同运行环境和输入下比较基线与候选。无法执行行为验证时明确说明，不能把文字校验通过当成行为正确。

本仓库常用：

```bash
python3 ./scripts/verify_skills.py --root .
make verify-generated
make test
make package
```

## 复盘沉淀建议

验证完成后可以判断本轮是否有值得沉淀的经验，但不得自动执行 `/retro` 或发起原任务范围外的沉淀写入。

触发信号：

- 用户纠正了测试方式、日志 API、架构分层、命名、发布步骤或验证入口。
- 本轮发现并修复了项目文档没写清楚、但会让 agent 反复犯错的约束。
- 审查中出现了可以被验证器、冒烟测试或 `AGENTS.md` 阻止的重复风险。

处理方式：

1. 没有可复用教训时，不输出单独段落。
2. 有可复用教训时，用一句话建议用户显式调用 `/retro` 或 `$retro`。
3. 未收到显式调用前，不为额外沉淀经验而修改 `AGENTS.md`、规则、references、ADR 或验证器；用户已授权的原任务修复仍按自动修复边界完成。建议落点应是目标 Agent 实际会读取的最窄受版本管理指南；UI 约束只有在运行入口会加载时才放进 `.claude/rules/*.md`。
4. 用户显式调用 retro 或继续其同一任务时，按该技能的调用边界和落点选择处理。

## 合并阻断项

- 工作区有用户改动且目标操作会覆盖它。
- 需要 force push、删除 release、关闭 issue、改 tag，但用户没明确授权。
- 验证命令失败且失败和改动相关。
- 生成物、version、package、release asset 不一致。
- 平台 manifest 版本、tag 或 release asset 名称不一致。
- 签名材料、notary credential、keystore 或 token 缺失，或 release asset 已存在但用户未授权覆盖/删除/重传。
- 发现 secret、token、私钥或内部路径将进入公共产物。

## 输出

审查输出顺序：

1. 先列发现，按严重度排序。
2. 待确认问题与假设。
3. 验证。
4. 复盘沉淀建议，仅在发现可复用教训时输出。
5. 改动摘要，只作为次要上下文。

交付输出要说明：commit、push、release、issue/PR 状态和验证证据。
