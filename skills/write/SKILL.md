---
name: write
description: "改写和润色中英文自然语言，去掉 AI 味，审阅产品本地化文案，并保留原意。Use when users ask 帮我写/改稿/润色/去AI味/写一段/审稿/本地化文案/tweet/unslop/rewrite/proofread. Not for code comments, commit messages, or inline docs."
when_to_use: "帮我写, 改稿, 润色, 去AI味, 写一段, 审稿, 文档review, 本地化文案, 多语言文案, i18n copy, localization copy, check this document, 推特, twitter, X推文, tweet, social post, 连贯性, 段落连贯, draft, edit text, proofread, sound natural, polish, rewrite, unslop"
dispatch_intent: "写作、改稿、润色、release notes、launch/social copy、去 AI 味"
---

# Write: 去掉 AI 味

Prefix your first line with 🥷 inline, not as its own paragraph.

**Update check（非阻塞）**。开始前运行一次 `bash ../../scripts/check-update.sh`；如果它输出提示，把那一行转告用户，然后继续。脚本每天最多读一次公开版本文件，不发送本地数据，失败时静默。

把文案改到自然、有人的判断，但不炫技。不要“提升词汇”，要去掉表演式改进。

## Outcome Contract

- Outcome: 文案保留作者意图，同时更符合目标读者、场景和语言习惯。
- Done when: 除非用户要求改变事实或结构，否则意义、事实主张和结构被保留，AI 腔被去掉。
- Evidence: 用户提供的文本、目标读者、项目风格参考、当前 release/product 状态和目标语言。
- Output: 默认只给改好的文案；只有用户要求时才给 notes、variants 或 review comments。

## Core Stance

这个技能是气味目录，不是逐条执行 checklist。识别 AI 味后做判断：该删就删，该保留就保留。

- **过度编辑和编辑不足一样失败**。句子已经自然、清楚、稳定时，不要动。
- **作者声音优先**。保留作者原有口语、节奏和立场。规则是默认值，不是法律。
- **禁用词表和替换表只是例子**。看气味，不做机械 find-and-replace。
- **少而准**。三个有效改动比三十个机械替换更好。

把新经验沉淀进技能时，合并到已有原则，不要无限追加同义禁用词。

## Pre-flight

1. **Text present?** 用户没给要改的文本时，只问一句让他贴文本。
2. **Audience locked?** 读者不能从文本推断时先问。写给初级工程师和资深架构师完全不同。
3. **Language detected from the text being edited**，不是从用户命令判断：
   - 中文 + release notes 或社交发布：读取 `references/write-zh-release-notes.md`
   - 中文 + bilingual 或翻译审阅：读取 `references/write-zh-bilingual.md`
   - 产品/网站/app 本地化：读取 `references/write-product-localization.md`；有中文时也读 `references/write-zh-bilingual.md`
   - 默认中文 prose：读取 `references/write-zh-prose.md`；需要完整模式库时读 `references/write-zh.md`
   - 其他情况：读取 `references/write-en.md`，并按 `references/unslop-patterns.md` 看英文气味。中文表仍以 `write-zh*` 为准。

读取对应参考后再改。默认不解释修改。

## Durable Context Preflight

参见 [rules/durable-context.md](../../rules/durable-context.md)。对 `/write` 来说，旧记忆可以提供声音、格式和用户偏好；the supplied text, target audience, project docs, current release state, and source material override memory.

## Hard Rules

- **Meaning first, style second.** 去 AI 味会改变作者意思时，保留原文意思。
- **No silent restructuring.** 不擅自重排标题、段落、顺序或合并章节，除非用户要求。Long-form Article Mode 例外。
- **Artifact-grounded claims.** Launch copy、release notes、产品页和 public reply 的事实必须来自当前产品、可运行产物、截图、release page、changelog、issue/PR 或用户材料。
- **No em-dash.** 不输出 U+2014 或 U+2013。用逗号、句号、冒号、分号或括号。
- **Stop after output.** 默认只给改好的文本，不追加解释、修改列表或收尾话。

## Long-form Article Mode

长文（约 300 行以上，或多个 `##`、表格和图片）里，最大问题通常是结构重复，而不是单句不自然。

流程：

1. **Map first, read-only.** 先读完整文章，列出 `##` 章节、表格、列表和图片。标出三类问题：跨章节重复、复读表格、整段/整节冗余。
2. **Propose cuts as change-points.** 每个结构删改都给 before -> after，让用户选。不要静默删除整节。
3. **Then line-level de-AI.** 用户确认结构点后，再逐节做句子级去 AI 味。
4. **Output is change-points.** 默认给变更点，不直接吐整篇重写稿。用户说“直接改”时才输出完整改稿。

不要单轮重写 4 万字文章，那会覆盖作者手调的表达，也很难 review。

## Bilingual Review Mode

用于中英混排、Chinese copywriting、bilingual consistency、release notes。

规则：

- 中文和英文之间通常留空格，品牌名、命令、路径和代码除外。
- 不把英文术语硬翻译成别扭中文；必要时保留英文。
- 中英版本要事实一致、语气一致、编号一一对应。
- Release notes 要工程师可读，不做营销腔。
- 社交文案可以更口语，但不能夸大事实。

## Product Localization Mode

用于产品 UI、网站、应用商店、设置项、按钮、空状态、错误提示等本地化。

检查：

- 文案是否符合控件大小和状态。
- 是否把功能承诺说过头。
- 中文是否自然，英文是否像 native product copy。
- 多语言是否保持同一事实，不逐字硬译。
- 错误提示是否告诉用户下一步，而不是只解释失败。

参考 `references/write-product-localization.md`。

## English Editing

英文编辑时不要把文字变得更“高级”。目标是更自然、更准确、更像人写。

优先：

- 删掉总结腔和过度连接词。
- 把抽象名词改回具体动作。
- 保留作者的直接语气。
- 避免 em-dash、过密形容词和“not only... but also...”式模板。

参考 `references/write-en.md` 和 `references/unslop-patterns.md`。分类是气味，不是替换词表。

## Output

默认输出改好的文本本身。用户要求 review 时，输出：

```text
Verdict: ...

Main issues:
- ...

Suggested rewrite:
...
```

用户要求多个版本时，最多给 3 个，并说明每个版本的使用场景。

## Sources

- https://github.com/finografic/pstack （`skills/prose/unslop`）

结构借鉴，正文已改写。中文规则仍以本技能的 `write-zh*` 为准。
