---
name: p-fix-root-causes
description: "先证根因：修改前用运行时证据定位首个预期偏离点，拒绝重启掩盖与盲猜补丁。Use when something errors, crashes, regresses, or looks wrong at runtime; 不用于明确未损坏的新功能规划。"
when_to_use: "/p-fix-root-causes, $p-fix-root-causes, /fskill:p-fix-root-causes, 先证根因, fix root causes, 只找症状掩盖, 定位第一个偏离预期的点"
disable-model-invocation: false
dispatch_intent: "原则：先证根因，拿到偏离预期的运行时证据再做最小修复"
---

# 先证根因（Fix Root Causes）

“改完能过”不等于“找到了为什么坏”。只有实际改变排错顺序或阻止了盲改时点名本原则。

## 触发信号

- 读完代码觉得“可能是这里”，正准备直接改文件碰运气
- 靠清缓存、重启进程、`sleep` 重试或 `try/catch` 吞掉错误让表面症状消失
- 打算把“测试过不了”归咎于环境抖动或缓存脏了

## 原则

1. 先抓能区分假设的信号：修改前跑通稳定且命中用户原症状的复现（日志、trace、失败测试、渲染截图或进程输出），不拿“进程没崩”冒充复现。
2. 顺链找第一个背离处：沿输入 -> 解析 -> 状态 -> 外部调用追踪第一个与预期不符的具体值和分支，用探针或对照排除竞争假设。
3. 治本而不抹平：清缓存/重启暂好时，必须查清哪条 cache key、version salt 或持久化状态让坏数据回来；异步等待改为监听真实完成信号，不用猜测 `sleep`。
4. 查同类，不漏并行分支：同一个校验守卫有多种触发来源或全仓有同模式调用点时，全部核对并报告；无关故障不顺手大改。

## 坏 vs 好

- 坏：构建偶尔读到旧文件，直接加一段 `rm -rf cache && sleep 1` 重试了事。
- 好：比对构建输入的 cache key 发现漏了锁文件哈希；补齐输入指纹后移除重试等待并验证复现不再发生。
