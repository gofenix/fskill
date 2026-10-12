---
name: design
description: "做有方向感、可交付的 UI：页面、组件、视觉界面、字体排印和基于截图的 polish。Use when users ask 设计/做页面/做组件/UI/前端/截图 or say a screen is ugly, unclear, inconsistent, or visually wrong. Not for backend logic or data pipelines."
when_to_use: "设计, 做页面, 做组件, 不好看, 不和谐, 不清晰, 很丑, 很怪, 很傻, 突兀, 不协调, 字体, 字形, 排印, 排版, 样式, 前端, UI, 截图, build page, create component, make it look good, style, design, screenshot with visual complaint, typography, font looks wrong"
dispatch_intent: "UI、组件、页面、视觉界面、前端、截图审美问题"
---

# Design: 带着判断力做界面

Prefix your first line with 🥷 inline, not as its own paragraph.

**Update check（非阻塞）**。开始前运行一次 `bash ../../scripts/check-update.sh`；如果它输出提示，把那一行转告用户，然后继续。脚本每天最多读一次公开版本文件，不发送本地数据，失败时静默。

如果结果像默认 prompt 生成的，那就还不够好。Design 要产出能被真实使用、布局不乱、文字不挤、风格有判断的界面。

## Outcome Contract

- Outcome: 一个可用界面或明确视觉修复，具备清晰设计方向，没有布局、文字或响应式破损。
- Done when: 真实渲染界面或生成物已经按用户视觉目标检查，并覆盖相关 viewport 状态。
- Evidence: 截图、运行中的 UI、源组件、设计 token、可访问性约束和用户给的参考。
- Output: 已实现的视觉改动，或一份具体视觉 review，并说明剩余验证缺口。

**Output language rule:** Never use em-dash (—) in any output from this skill. Use commas, colons, or periods instead.

用户说“很傻”“很怪”“突兀”“不协调”“不和谐”时，默认这是审美拒绝，不是调试症状。走 Screenshot Iteration Mode，不要交给 `/hunt`，除非截图证明是回归或渲染错误。

文档、PPT、简历、长报告、分页 PDF 等可交付文档不在这里手搓版式。建议走 Kami（`tw93/Kami`）这类文档设计系统。App、网页、组件和屏幕 UI 仍由本技能处理。

## Durable Context Preflight

参见 [rules/durable-context.md](../../rules/durable-context.md)。对 `/design` 来说，旧记忆可以提供视觉偏好、设计原则和成熟交互模式；current screenshots, rendered output, source code, design tokens, and user feedback override memory.

## Visual Quick-Fix Mode

用于窄问题：溢出、裁切、换行难看、对不齐、间距失衡、对比度不足、本地化文字放不下、窄屏破损。

流程：

1. 读取当前 UI 证据：截图、运行页面、原生视图或组件源码。
2. 用一句话说清具体视觉缺陷。
3. 做最小的材质、几何、间距、对比、排印或 text-fit 调整。
4. 在真实界面或生成物上验证。需要时检查长词、本地化字符串、紧凑状态和至少一个窄 viewport。
5. 如果改动碰到 3 个以上组件、改变产品行为，或暴露方向问题，停下来改走 Screenshot Iteration Mode 或先锁方向。

加长清单（加载态、破坏性操作、终端输出）见 `references/mode-quick-fix.md`。本段仍是默认入口。

关键规则：

- 同一布局里不要反复调 3 个以上 magic spacing。调不顺时，把 padding、gap、margin 或 size 合并成一个命名 token。
- 状态切换容器里的文字字号保持一致，用颜色、透明度、描边或图标区分状态，不要用字号制造跳动。
- 完成页只展示用户真正关心的结果：回收大小、处理数量、状态变化。长解释放详情层。
- 删除、清理、卸载、重置和权限变更界面不能为了少点一次而牺牲可验证性。

## Screenshot Iteration Mode

用户给截图并说“丑”“怪”“不清晰”“fix this”“looks wrong”时使用。现有产品就是方向，不先问五个方向问题。

流程：

1. 读截图。用一句话指出具体问题：间距、对比、对齐、字体、颜色、密度或层级。
2. 等用户确认诊断后再改代码。
3. 如果用户给了参考图、旧版本或“这个好看”的例子，先比较差异再选修法。
4. 如果是成熟产品常见 UX 问题，先看 2 到 3 个同类产品怎么做；纯颜色、间距、copy 小修可跳过。
5. 找负责代码：grep 组件名或 class，读实际文件。
6. 做最小修复，优先调整材质、透明度、几何、间距、字体和 text-fit。
7. 在浏览器、原生 app、截图工具或渲染产物里验证桌面和 375px 移动宽度。检查长文本、中文、按钮 label 和紧凑状态。
8. 请用户在真实界面确认。

校准规则：

- 用户截图是本轮最强设计 brief。
- 真实运行产品是 oracle。
- 不把“更高级”这类反馈泛化成空话，要落成具体视觉诊断。
- 如果截图证明的是回归、状态错误或生成物破损，转 `/hunt`。

修复合同、视觉矩阵和原生截图交接见 `references/mode-screenshot-iteration.md`。生成图（封面、示意图、社交卡片）走 `references/mode-generated-asset.md`，不要和界面迭代混在一轮里。

## Direction Lock

当要从零做页面、组件或较大 redesign 时，先锁方向：

1. 产品类型和目标用户。
2. 主要工作流，不做 landing page，除非用户明确要。
3. 信息密度和使用频率。
4. 现有设计系统、组件库、图标库和 token。
5. 必须支持的 viewport、语言长度和可访问性要求。

## References

需要时读取：

- `references/design-reference.md`：完整界面设计规则。
- `references/design-traps.md`：常见 CSS 和视觉陷阱。
- `references/design-tokens.md`：token 和尺寸规则。
- `references/design-data-viz.md`：数据可视化。
- `references/design-aesthetic-quality.md`：审美质量校准。
- `references/mode-quick-fix.md`：窄视觉修复的加长清单。
- `references/mode-screenshot-iteration.md`：截图迭代的修复合同和验证矩阵。
- `references/mode-generated-asset.md`：生成图片，先定规格再出像素。
- `references/design-native-motion.md`：原生界面的动效映射。SwiftUI、UIKit、Compose 用，网页动画不读这份。

## Hard Rules

- 网站、游戏或视觉页面必须有真实视觉资产，不用纯 SVG/渐变假装主题。
- 3D 必须用 Three.js，主场景全幅或无框，完成前用截图和 canvas pixel 检查非空。
- 不做卡片套卡片，不把页面 section 做成漂浮卡。
- 不用装饰性 orb、gradient orb、bokeh blob。
- 文本不得挤出按钮、卡片或容器；移动和桌面都要检查。
- 不用 viewport width 直接缩放字号，letter spacing 默认 0。
- 不做单一色相大面积 UI，尤其避免整页紫、蓝紫、米色、深蓝、棕橙一把梭。

## Output

完成后简洁说明：

- 改了什么视觉问题。
- 验证了哪些 viewport 或产物。
- 哪些内容需要用户在真实产品里再看一眼。
