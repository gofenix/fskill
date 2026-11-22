---
name: p-explain-the-number
description: "解释数字：任何性能、大小、配额或评测数字必须附基线、负载口径与样本条件，指标改进一次只验一个假设。Use when reporting metrics, benchmarks, token savings, or running optimization experiments; 不用于常规功能规划。"
when_to_use: "/p-explain-the-number, $p-explain-the-number, /fskill:p-explain-the-number, 解释数字, explain the number, 单假设指标实验, 性能基线与评测口径"
disable-model-invocation: false
dispatch_intent: "原则：解释数字，所有量化声明附真实口径与基线，指标实验单变量对照"
---

# 解释数字（Explain the Number）

没有测试口径和对照基线的“提速 40%”“省下大量 token”比不写更误导人。

## 触发信号

- 汇报耗时、吞吐、体积变化、配额用量、拦截率或评测分数
- 在同一轮改动中同时叠了多个优化点并声称某一项生效
- 用单次本地跑分代替有代表性的工作负载

## 原则

1. 数字附口径：报数字时说清测量目标、相同条件下的基线与改动后值、样本规模/输入形态与已知波动；不能凭感觉或估算编出节省百分比。
2. 确认计时打对了地方：计时与 profile 必须覆盖用户真正关心的完整路径，同时记录错误数与实际完成工作量，不把中途失败或跳过工作当成变快。
3. 一次只验一个假设：已经进入明确指标优化循环时，定好基线与回退规则后一次只改一个变量；收益达标且无正确性回归再保留，否则立刻回退该假设。
4. 先稳后快：任何指标收益不能以吞掉校验、丢失边缘语义或引入回归为代价。

## 坏 vs 好

- 坏：同时改了缓存、并发数和序列化格式，跑一次小样本后汇报“性能提升约 3 倍”。
- 好：先固定 1,000 条真实样本基线（P50 180ms / P95 420ms，错误 0），单改批量序列化后重测 3 轮得 P50 92ms / P95 210ms（错误 0），保留该改动再评估下一步。
