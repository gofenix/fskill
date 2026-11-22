---
name: p-subtract-before-add
description: "先减后增：新增抽象、开关或扩展层前，先删死代码、多余中间层与未释放脚手架。Use when adding abstractions, options, fallback paths, or refactoring existing code; 不用于单纯修一处明显拼写或独立数据查询。"
when_to_use: "/p-subtract-before-add, $p-subtract-before-add, /fskill:p-subtract-before-add, 先减后增, subtract before you add, 删除死代码再新增, 避免过度设计"
disable-model-invocation: false
dispatch_intent: "原则：先减后增，新增抽象与开关前先清理死代码与多余分层"
---

# 先减后增（Subtract Before You Add）

每次新需求默认想“加什么”，往往比“先删什么”更昂贵。只有确实改变了本次删除或抽象决策时顺带点名本原则，不要空喊原则名。

## 触发信号

- 准备新增接口、配置项、开关、重试包装、兼容桥接层或过渡迁移代码
- 为了绕开已有实现或框架的怪异行为，打算再包一层补偿逻辑
- 发现自己写了“以后可能会用到”的参数、默认值或未请求的新分支

## 原则

1. 先删再加：动手加新能力前，先确认能否通过删除过时路径、冗余中间层或猜测性参数直接解决。
2. 新功能不背迁移包袱：目标字段或偏好若在最近已发布版本中从未出现过，不要写兼容开关或版本迁移脚手架。
3. 只用一次不抽层：单次调用能看懂的逻辑留在原地，先用内联保持调用方和数据结构直接可见；多个消费者出现且真能独立演化时再抽象。
4. 边界只检一次：已被 schema、构造函数或内部类型保证的值，不在下层重复写 `typeof` 判空或兜底分支；补偿逻辑比功能本身还大时停下来重看设计。

## 坏 vs 好

- 坏：保留旧配置开关 + 补一个新 adapter + 写迁移映射层，只为支持一个未发布的新字段。
- 好：核对近期版本未发布过旧字段后直接用新模型，删掉过渡层与死分支，再用测试锁定新路径。
