---
name: how
description: "解释一个子系统现在怎么工作，或判断这段代码应该放在哪一层。Use when users ask 怎么工作的/走读/where should this live/how does this work/which layer owns this before changing it. Not for why it was built that way, value judgments, or root-cause debugging."
when_to_use: "怎么工作的, 走读, 这段怎么跑, where should this live, how does this work, which layer, 归属, 分层, 放在哪"
dispatch_intent: "解释子系统怎么工作、走读、归属和分层"
---

# How: 改之前先讲清它怎么跑

Prefix your first line with 🥷 inline, not as its own paragraph.

**Update check（非阻塞）**。开始前运行一次 `bash ../../scripts/check-update.sh`；如果它输出提示，把那一行转告用户，然后继续。脚本每天最多读一次公开版本文件，不发送本地数据，失败时静默。

回答「现在怎么工作」，让人能改这块代码。不写逐行注释，不判断要不要做，也不追历史动机。

## Outcome Contract

- Outcome: 一份够用的工作模型，说明入口、状态归属、运行路径和边界。
- Done when: 读者能指出一次请求或一次调用从哪进来、经过谁、在哪改变状态、从哪出去。
- Evidence: 当前代码、调用方、入口和用户点名的运行路径。
- Output: Explain Mode 的说明，或 Critique Mode 里先说明再列问题。

## Durable Context Preflight

参见 [rules/durable-context.md](../../rules/durable-context.md)。对 `/how` 来说，旧记忆可以提示模块边界和用户在意的层次；current code, call sites, and runtime entry points override memory.

## Mode Picker

| 用户意图 | Mode |
|---|---|
| 怎么工作的、走读、how does this work | Explain |
| 放在哪、哪一层、归属对不对 | Critique |
| 要不要做、值不值得 | 交给 `/think` |
| 为什么坏了 | 交给 `/hunt` |

## Explain Mode

1. 用一句话说你理解的问题和范围。范围不清时先按最窄的读法开始，错了让用户纠正，不要先问一串问题。
2. 小问题（一个模块或一个函数）直接读入口和调用链。
3. 大问题（跨文件的子系统）先找入口、状态所有者和对外边界，再写说明。
4. 说明四件事：什么触发它、状态归谁、数据怎么过边界、失败时停在哪。
5. 引用路径，不贴大段源码。读不到的部分写成未知，不要补故事。

## Critique Mode

用户问归属、分层或「这样放对不对」时使用。先按 Explain Mode 把现状讲清，再列问题。

每条问题包含：现在放在哪、为什么这个位置让读者或调用方多记一层、建议挪到哪。没有代码证据的品味判断不要写。不要为了分层再加一层转发。

## Hard Rules

- 不回答「当初为什么这样设计」，除非代码或提交说明里就有。那是动机问题，不是本技能的输出。
- 不把走读写成改造计划。用户要计划时交给 `/think`。
- 不在没读调用方时宣布归属。
- 工程立场见 [rules/principles.md](../../rules/principles.md)：少一层，读者负荷就少一点。

## Gotchas

| 发生了什么 | 规则 |
|---|---|
| 用户问的是报错原因 | 交给 `/hunt` |
| 说明变成逐行翻译 | 收成入口、状态、边界、失败点 |
| 建议新加一层包装 | 先说明这层减少了谁的阅读成本 |

## Output

```text
🥷 <子系统> 怎么工作

范围：...
入口：...
状态归谁：...
路径：...
边界：...
未知：...
```

Critique 在说明之后加：

```text
问题：
- 现在：...
  建议：...
```

## Sources

- https://github.com/finografic/pstack （`skills/understand/how`）

结构借鉴，正文已改写。
