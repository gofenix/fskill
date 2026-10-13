# 输入法与 Unicode

输入问题先区分输入法组合状态、事件顺序和字符串位置单位，再形成假设。

## 输入与事件顺序

记录 `compositionstart`、`compositionupdate`、`compositionend`、`beforeinput`、`input` 和 `keydown`，包括输入数据、选区和焦点变化。不要在输入法组合期间做会破坏候选词的格式化、DOM 重建、自动提交或光标跳转。

确认候选词的 Enter 应只提交文字，不能触发表单提交或导航，也不能把该动作排队到 `compositionend` 执行。`compositionend` 可能先于确认键的 `keydown`，此时 `isComposing` 已为 false；同样在 `compositionend` 清除的标志也会漏判。按实际 IME 和宿主采集事件顺序，不靠操作系统名称或固定延迟猜测。

回归验证覆盖两种事件顺序：候选词确认不提交表单，随后用户主动按 Enter 只提交一次。

## 字符与位置单位

- JavaScript 的 `str.length` 和文本节点 DOM 偏移使用 UTF-16 码元。
- `[...str]` 遍历码点，不能直接替代 DOM 偏移。
- 可见字符截断通常需要字素簇；使用 `Intl.Segmenter` 的 `grapheme` 粒度，并先确认接收位置的 API 使用什么单位。
- `👩‍🚒` 包含 3 个码点、1 个字素簇。ZWJ 序列被拆开时检查切片边界、实际字体和序列化前后字节。
- 检查 NFC/NFD 是否混用，以及全角空格、不可见空白和零宽字符。

需要检查 Python 字符值时：

```python
for ch in text:
    print(ch, hex(ord(ch)))
```

焦点切换、撤销粒度或原生窗口与 WebView 行为不同时，同时记录宿主输入事件；不要只修改页面键盘处理器。
