# 维护者工作流

仅在已有 PR 跟进、已授权交付或项目审计时读取对应章节；沿用入口中的工作区保护、项目上下文和验证要求。持续维护队列的类别、状态和重入由显式 `/triage` 处理，本参考只保留 PR 跟进、交付与质量检查。

## 交付与发布跟进

先按实际交付面选择检查，不把普通提交当成发布：

- 仅 commit/push：检查目标 diff、worktree 和 HEAD，运行相关必需验证并同步受影响生成物；push 后回读远端 SHA 和相关 CI。除非本次改动或项目规则要求，不强制 tag、release notes、registry 发布或上传 asset。
- 发布就绪判断、打包或发布：填写 `project-context.md` 的适用发布检查项，确认版本、tag、生成物、package、platform artifact 和 release asset 一致，相关 CI 或本地等价验证通过。平台产物记录路径、hash、大小和构建命令，上传后回读远端状态。
- 公共回复、关闭 issue 或 reaction：核对实际目标和交付渠道，执行已授权动作后回读确认。commit/push 授权不附带这些公共操作，force push 也需明确授权。

用户要打包或上传 release asset 时，读取 [release-artifacts.md](release-artifacts.md)。仅 diff 触及 macOS/Android 发布面时，审查相关配置和风险，验证范围仍按本次交付面选择。先从 README、AGENTS/CLAUDE、Makefile、package scripts、Gradle/Fastlane/Xcode/Electron/Tauri 配置和 CI release workflow 找官方命令；找不到时只给候选并问用户确认，不要凭平台习惯直接执行完整发布命令。

创建 tag、push、发布 GitHub release、上传 asset、删除或覆盖 asset 都必须有用户明确授权。已有明确授权且范围未变时完成对应动作和远端回读，不重复请求同一授权；新增破坏性动作或改变范围时单独确认。签名证书、keystore、notary credential、token 缺失时停止，只报告缺失项，不要求用户把 secret 发给 agent。

网络或 API 失败后先回读最终状态。发布、建 tag 或创建 release 的验证超时表示结果未知，不等于操作失败；按项目重试策略进行有界只读检查，仍不明确就报告具体缺口，不能为让验证通过而重复发布。交付时分别说明源码、CI、可安装产物和公共回复状态。

提交说明使用项目约定。这个仓库约定是 `{type}: {description}`，type 为 `feat`、`fix`、`refactor`、`docs`、`chore`。

## 已有 PR 的持续跟进

先区分仅查状态、处理讨论与获准持续推进；查状态不附带改代码、公共回复、调度或合并授权。沿用一个责任 owner，记录当前 head、base、CI 与未决讨论，使用宿主已有等待或事件机制，不建立重复的跟进者。

CI 失败先分类为产品回归、环境/基础设施或偶发；保留失败证据，只对已确认可重试且在预算内的情况有界重试。没有变化就不反复播报。改代码、更新基线或集成别人的成果后，把受影响验证绑定到新 revision，不能沿用旧绿灯。merge-ready 是就绪判断，合并仍需本任务适用授权。

检查以 `ACTION_REQUIRED` 结束时，先核对检查身份、详情及平台的审批状态。仅确认属于 code owner 审批门禁（例如 `Code Review Gate`）时分类为“等待审批”，不当作产品失败重试，也不当作已通过或可绕过审批；其他同名状态仍按真实原因分类，未知就保留待核实。

## 项目体检模式

项目体检输出评分表，不做大重构。

评估维度：

- 上下文面：README、AGENTS/CLAUDE、manifest、CI 是否告诉 agent 怎么安全工作。
- 验证面：是否有可复制命令，是否覆盖生成物和发布物。
- 架构面：模块边界、重复、热点、不可测试区域。
- 安全面：secret、危险命令、权限、外部系统。
- 维护性：大文件、隐式流程、陈旧文档、无人拥有的复杂区域。

每个发现项给证据和下一步，不把风格偏好当 bug。

架构维度只报告现有风险；用户要从现有系统主动寻找、比较重构机会时可建议 `/architect`，不在项目审计里另跑一遍机会发现流程。
