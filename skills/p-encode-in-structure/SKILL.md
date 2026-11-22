---
name: p-encode-in-structure
description: "结构防复发：把已验证的教训与易错边界固化进类型系统、schema、测试或检查脚本，不靠往文档追加口号防错。Use when capturing verified lessons, designing TypeScript types/boundaries, or preventing repeat failures; 不用于临时一次性偏好。"
when_to_use: "/p-encode-in-structure, $p-encode-in-structure, /fskill:p-encode-in-structure, 结构防复发, encode lessons in structure, 用类型与测试代替口头提醒, 复盘沉淀"
disable-model-invocation: false
dispatch_intent: "原则：结构防复发，把复发教训落成类型不变量、脚本或测试而非口号"
---

# 结构防复发（Encode Lessons in Structure）

凡是下次依然容易忘、靠人“多小心一点”拦不住的错，应该由编译器、类型、测试或脚本拦住，而不是往 `AGENTS.md` 多塞三行感叹号。

## 触发信号

- 同类 bug 或审查意见在不同改动里反复出现
- 刚修复或复盘完一个有证据的真实缺陷，正考虑是否写进长期规则
- 编写或重构 TypeScript 模块边界与状态表示

## 原则

1. 先结构，后文档：能让类型系统、schema 校验、静态测试或 CI 脚本机械阻断的问题，直接落到结构层；只有依赖上下文判断的约束才进规范文档或技能，且先合并同类项再增删，绝不堆私密路径或一次事故流水账。
2. TypeScript 令非法状态不可表示：不用 `any` 与随意类型断言；互斥状态用 discriminated union 与穷尽检查（`switch` + `never`）；未知输入只在入口边界用 schema/type guard 校验一次。
3. 枚举高危源头调用点：对于不可逆删文件、提权命令或安全敏感路径，优先在底层包装边界或全仓调用点扫描测试里加约束，不指望每个调用方自己记得。
4. 不靠假设写长期规则：尚未验证过的猜测或单次环境故障不写进仓库指导；必须满足“可能再犯 + 能改变下次行为 + 可验证/可执行”才沉淀。

## 坏 vs 好

- 坏：因为曾经漏处理空状态且在 `AGENTS.md` 里追加“请永远记住检查 `status === 'ready'`”。
- 好：把分散布尔标志改成 `{ status: 'pending' } | { status: 'ready'; payload: Data }` 联合类型，让未就绪分支在编译期就无法读取 `payload`。
