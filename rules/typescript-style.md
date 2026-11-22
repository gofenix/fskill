# TypeScript 写法

仅在项目已是 TypeScript 时遵循（根目录存在 `tsconfig.json` 或当前文件为 `.ts`/`.tsx`）；项目自己的 lint、formatter 与当前文件风格始终优先，不因此改写未触及的文件。

- **类型即不变量**：禁用 `any` 与无依据的非空断言；互斥状态用 discriminated union + `switch` 穷尽检查（`never`），使非法状态在编译期不可表示；能靠推断时少写冗余标注。
- **边界只检一次**：未知输入仅在入口用 schema 或 type guard 校验一次；已被 schema、构造函数或内部类型保证的值，不在内部重复写 `typeof` 判空。
- **控制流扁平**：优先 `const`、三元表达式与提前返回（避免冗余 `else` 和先 `let` 后赋值）；只用一次的简单表达式直接内联，不必拆出一堆单次 helper 或中间变量。
- **导入清晰**：不用 star import（`import *`）与导入别名；不在类型位置写 `import("...")`；仅启动敏感的重模块在最窄分支用顶层解构式动态 import（不写 `.then(m => ...)` 链式求值）。
- **异常处理克制**：不用 `try/catch` 吞掉内部错误；只在非 Effect 项目的外部解析边界按需捕获并返回明确失败状态；数组优先用带 type guard 的 `flatMap`/`filter`/`map`。
- **对象与注释**：非框架惯例（React props/hooks）尽量保留 `obj.prop` 点号上下文；注释只写不明显的约束与为什么，不解释字面含义。
- **生态按需生效**：仅在项目已使用时遵守 —— Bun 优先 `Bun.*` 原生 API；Effect 保持纯同步 helper 为同步函数，不可信 JSON 用 `Schema.UnknownFromJsonString` 而非 `Effect.try(JSON.parse)`，generator 里先绑定 service 再调方法；Drizzle 表字段用 `snake_case` 省略冗余列名字符串。
