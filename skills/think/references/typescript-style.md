# TypeScript 写法

项目是 TypeScript 时，编写或修改 `.ts` / `.tsx` 遵循本节。看到根目录 `tsconfig.json`，或当前文件已是 TypeScript，就应用。不要为了确认风格扫全仓。

项目自己的说明、lint、formatter，以及当前文件里的既有写法优先。本节约束正在写的代码，不作为改写未触及文件的理由。

## 通用

- 能留在一个函数里就不要拆，除非它可组合或会被复用。
- 未知值只在拥有它的边界校验一次。schema、构造函数或内部类型已经保证的值，不要再写 `typeof value === "object"` 和属性存在性检查。
- 不要提前抽出只用一次的辅助函数。调用处能读懂就内联，除非它被复用、挡住真正复杂的边界，或有一个能改善调用方的独立名字。
- 为几乎不会发生的竞态或安全边界增加复杂度之前，先说明具体失败方式、可能性和复杂度代价，得到同意再写。
- 尽量不用 `try` / `catch`。
- 不用 `any`。
- 能靠推断就不要写显式类型或 interface。导出或确需可读性时再标注。
- 优先 `flatMap`、`filter`、`map`。`filter` 配 type guard，让后面的推断保持住。
- 只用一次的值不要先放进中间变量。

```ts
// 好
const journal = await readJson(path.join(dir, "journal.json"))

// 差
const journalPath = path.join(dir, "journal.json")
const journal = await readJson(journalPath)
```

项目在用 Bun 时，优先 Bun API，例如 `Bun.file()`。项目不是 Bun 时，不要为了这条换运行时。

## 解构

不必要的解构避免。用点号保留上下文。

```ts
// 好
obj.a
obj.b

// 差
const { a, b } = obj
```

## 导入

- 不要给导入起别名，不要写 `import { foo as bar }` 或 `resolve as pathResolve`。
- 不要在类型位置写 `import("...")`。只有两个导入真的撞名、且没有别的办法时，才允许 `import type { Plugin as PluginDefinition }`，仍然尽量不用。
- 不要用 star import：`import * as Foo` 和 `import type * as Foo` 都不要。
- 需要命名空间时，导入模块自己导出的命名空间，例如 `import { Project } from "..."`, 再写 `Project.ID`。
- 重模块只在部分路径用到时用动态 import，尤其是启动敏感入口。在最窄作用域顶部解构，读起来像普通导入。不要写 `await import("./module").then((mod) => mod.value())` 或 `(await import("./module")).value()`。分支才需要的导入留在分支里，保持懒加载。

## 变量

优先 `const`。用三元或提前返回，不要先 `let` 再赋值。

```ts
// 好
const foo = condition ? 1 : 2

// 差
let foo
if (condition) foo = 1
else foo = 2
```

## 控制流

避免 `else`。用提前返回。

```ts
// 好
function foo() {
  if (condition) return 1
  return 2
}

// 差
function foo() {
  if (condition) return 1
  else return 2
}
```

## 复杂逻辑

主函数读起来是顺利路径。校验分支和辅助细节放在下面的小函数里，靠近使用处。

```ts
// 好
export function loadThing(input: unknown) {
  const config = requireConfig(input)
  const metadata = readMetadata(input)
  return createThing({ config, metadata })
}

function requireConfig(input: unknown) {
  // ...
}
```

- 不要把简单表达式拆成一堆只用一次的函数。抽出的函数要有真实名字，例如 `requireConfig`、`readMetadata`。
- 注释只写不明显的约束和意外行为。

项目在用 Effect 时：

- generator 里先把 service 绑到具名变量，再调用方法。不要写 `yield* (yield* Foo.Service).bar()`。
- 辅助函数不做 effectful 工作时不要返回 `Effect`。同步解析、校验和选项构建保持同步。
- 解析不可信 JSON 时，优先 schema 辅助，例如 `Schema.UnknownFromJsonString` 和 `Schema.decodeUnknownOption`，不要用 `JSON.parse` 包一层 `Effect.try`。

## Drizzle

项目在用 Drizzle 时，字段名用 snake_case，列名不必再写成字符串。

```ts
// 好
const table = sqliteTable("session", {
  id: text().primaryKey(),
  project_id: text().notNull(),
  created_at: integer().notNull(),
})

// 差
const table = sqliteTable("session", {
  id: text("id").primaryKey(),
  projectID: text("project_id").notNull(),
  createdAt: integer("created_at").notNull(),
})
```
