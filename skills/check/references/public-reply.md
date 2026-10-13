# 公共回复

用于 issue、PR、发布评论和维护者回复。

原则：

- 先确认事实，再表达态度。
- 短，具体，有下一步；默认匹配发起者的语言，用户或项目另有明确要求时遵循该要求。
- 不把内部推理、私有路径、token、机器状态或未公开上下文写出去。
- 不承诺没有验证过的发布日期、性能数字或兼容范围。
- 分清源码已修复、CI 通过和用户可安装版本已发布；未发布时说明当前状态及有依据的下一步，不把 main 上的修复称为用户已可用。
- 下一步必须在用户报告的故障或无障碍限制仍存在时可执行，不能要求先关闭其必需的辅助能力。索取日志、截图或本地状态时只要最少的非敏感公开信息；私密支持渠道只能使用项目已公开提供的渠道。
- 关闭 issue 时给出支持关闭的 commit、release、测试或范围决策；“needs info”表示证据不足，应保留待定，不单凭无法复现而关闭。

常用形态：

```text
Thanks for the report. I reproduced this with {command/version}. The fix is in {commit/PR}; it will be available in {release/version}.
```

```text
I could not reproduce this yet. Please share {minimal info}. Without that, the next action would be guesswork.
```

```text
This is outside the current scope because {one concrete boundary}. I am closing this to keep the tracker focused.
```
