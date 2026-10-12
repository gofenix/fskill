# PR 正文

`/check` 在用户要求写 PR 说明，或 Ship 模式需要对外说明改动时读取。事实必须来自本轮 diff、命令输出和远端状态。

```markdown
## Summary

<一张能看懂改动的图、目录或三行以内的行为变化>

## Evidence

- Before: <失败的测试、旧输出或截图>
- After: <通过的测试、新输出或截图>

## Merge Danger

- Door: <单向或双向。单向表示合并后难撤销，例如迁移、删数据、改公开契约>
- Blast radius: <一个短语：谁会碰到这个改动>
- Leftover: <没跑的验证，或明确写没有>
```

写法：

1. Summary 写行为变化，不写文件清单。
2. Evidence 的前后必须是本轮看过的输出。没有前后对比就写「未采集」并说明原因。
3. 单向门要写出撤销成本。双向门写一句怎么回滚。
4. 不写营销句，不写没有跑过的「已全面验证」。

## Sources

- https://github.com/mattpocock/skills （`skills/engineering/pr`）

结构借鉴，正文已改写。
