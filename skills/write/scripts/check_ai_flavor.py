#!/usr/bin/env python3
"""Audit Chinese prose for common AI-flavor structure shells.

This is a review aid, not a rewriting tool. It skips fenced code, inline code,
URLs, and Markdown blockquotes, then reports high-signal patterns that often
make Chinese prose look assembled by a model.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

CJK = r"\u3400-\u4dbf\u4e00-\u9fff"
CODE_SPAN_RE = re.compile(r"`[^`]*`")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


@dataclass(frozen=True)
class Rule:
    rule_id: str
    label: str
    severity: int
    pattern: re.Pattern[str]


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    column: int
    rule_id: str
    severity: int
    message: str
    match: str

    def render(self) -> str:
        return (
            f"{self.path}:{self.line}:{self.column}: "
            f"[S{self.severity}] {self.message} ({self.rule_id}: {self.match})"
        )


RULES = [
    Rule(
        "binary_contrast",
        "二分对照壳。不是所有对照都要删，但空转的“不是 A，而是 B”要改成具体关系。",
        3,
        re.compile(r"(?:不是|并非|不在于|不只是|不止是|不仅是).{0,32}(?:而是|而在于|更是)|与其说.{0,32}不如说"),
    ),
    Rule(
        "staged_sequence",
        "机械先后顺序。只有真实顺序会改变结果时才保留。",
        2,
        re.compile(r"先.{0,24}(?:再|然后|后面|随后)|第一步.{0,60}第二步|从.{1,24}到.{1,24}"),
    ),
    Rule(
        "essence_claim",
        "本质拔高壳。直接说事实、动作或结果。",
        3,
        re.compile(r"真正.{0,24}(?:的是|在于|决定|重要|打动|改变)|本质上|核心在于|底层逻辑"),
    ),
    Rule(
        "route_marker",
        "助手路标词。进入内容本身，不要解释接下来怎么组织。",
        3,
        re.compile(r"下面我们来|接下来我会|我们可以看到|希望这能帮到你|作为AI|截至我的知识"),
    ),
    Rule(
        "lecture_marker",
        "讲义腔或总结腔。没有新信息时删掉。",
        2,
        re.compile(r"总的来说|值得注意的是|不可否认的是|不难看出|由此可见|在这个过程中|这背后其实|说白了|划重点|捋一捋|盘一盘|拆一拆|聊一聊"),
    ),
    Rule(
        "meta_structure",
        "元叙事。讨论写法时可以用，正文里直接写内容。",
        2,
        re.compile(r"按三段拆|压成一张表|从三个维度展开|从.+?维度来看|可以分成.{0,12}类|可以归纳为"),
    ),
    Rule(
        "easy_answer_colon",
        "很简单冒号模板。删掉铺垫，直接说条件、证据或决定。",
        2,
        re.compile(r"[^。！？\n]{1,18}很简单[：:]"),
    ),
    Rule(
        "principle_poster",
        "原则句或伪口语。点名具体对象、文件、动作和结果。",
        2,
        re.compile(r"把.{1,16}链路跑稳|写到下次会读到的地方|别让.{1,16}互相抢活|少踩雷|把坑填平"),
    ),
]

ENDING_QUESTION_RE = re.compile(r"(你觉得呢|是不是很有启发|你有没有类似经历|你现在卡在哪一步|大家怎么看)[？?]?$")
HEN_SENTENCE_RE = re.compile(r"^[^，,；;：:\n]{1,18}很[^，,；;：:\n]{1,12}$")
TEMPLATE_PREFIX_RE = re.compile(r"^(?:概念|问题|原因|结论|答案|核心|本质|关键|目标|方法|步骤|第一步|第二步|第三步|SOP)[：:]")


def mask_ignored_spans(line: str) -> str:
    def spaces(match: re.Match[str]) -> str:
        return " " * (match.end() - match.start())

    return URL_RE.sub(spaces, CODE_SPAN_RE.sub(spaces, line))


def prose_lines(text: str):
    in_fence = False
    for number, raw in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence or raw.startswith("    ") or raw.lstrip().startswith(">"):
            continue
        yield number, mask_ignored_spans(raw)


def detect_language(text: str) -> str:
    return "zh" if re.search(f"[{CJK}]", text) else "other"


def column_of(text: str, needle: str) -> int:
    idx = text.find(needle)
    return idx + 1 if idx >= 0 else 1


def add_rule_findings(path: str, text: str, findings: list[Finding]) -> None:
    for line_no, line in prose_lines(text):
        for rule in RULES:
            for match in rule.pattern.finditer(line):
                findings.append(
                    Finding(
                        path,
                        line_no,
                        match.start() + 1,
                        rule.rule_id,
                        rule.severity,
                        rule.label,
                        match.group(0),
                    )
                )
        stripped = line.strip()
        if ENDING_QUESTION_RE.search(stripped):
            findings.append(
                Finding(path, line_no, column_of(line, stripped), "ending_question", 3, "结尾泛互动问题。只有明确要 CTA 或评论引导时才保留。", stripped)
            )


def split_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def title_case_formal_name(cell: str, category: str) -> bool:
    words = cell.split()
    if len(words) < 2 or words[-1].lower() != category:
        return False
    return all(word[:1].isupper() for word in words if word)


def add_table_findings(path: str, text: str, findings: list[Finding]) -> None:
    lines = list(prose_lines(text))
    for index, (line_no, line) in enumerate(lines[:-2]):
        if "|" not in line:
            continue
        header = split_cells(line)
        separator = split_cells(lines[index + 1][1])
        if not is_separator(separator):
            continue
        categories: dict[int, str] = {}
        for col, cell in enumerate(header):
            lowered = cell.lower()
            if lowered in {"tool", "tools"}:
                categories[col] = "tool"
            elif lowered in {"skill", "skills"}:
                categories[col] = "skill"
            elif lowered in {"agent", "agents"}:
                categories[col] = "agent"
        if not categories:
            continue
        for row_no, row_line in lines[index + 2 :]:
            if "|" not in row_line:
                break
            cells = split_cells(row_line)
            for col, category in categories.items():
                if col >= len(cells):
                    continue
                cell = mask_ignored_spans(cells[col]).strip()
                if not cell:
                    continue
                if title_case_formal_name(cell, category):
                    continue
                if re.search(rf"(?i)(?:^|[\s_/.-]){category}s?$", cell):
                    findings.append(
                        Finding(
                            path,
                            row_no,
                            column_of(row_line, cells[col]),
                            "table_category_echo",
                            2,
                            f"表格内容复读表头。{category.title()} 列里通常不要写 'xxx {category}'。",
                            cell,
                        )
                    )


def add_shape_findings(path: str, text: str, findings: list[Finding]) -> None:
    template_lines: list[tuple[int, str]] = []
    hen_sentences: list[str] = []
    paragraph_lengths: list[int] = []

    for line_no, line in prose_lines(text):
        stripped = line.strip()
        if TEMPLATE_PREFIX_RE.match(stripped):
            template_lines.append((line_no, stripped))
    if len(template_lines) >= 3:
        findings.append(
            Finding(
                path,
                template_lines[0][0],
                1,
                "template_colon",
                2,
                "冒号模板重复。不要把普通段落拆成一串“概念：解释”。",
                f"{len(template_lines)} lines",
            )
        )

    for sentence in re.split(r"[。！？!?]\s*", text):
        sentence = sentence.strip()
        if sentence and not sentence.startswith("#") and HEN_SENTENCE_RE.match(sentence):
            hen_sentences.append(sentence)
    if len(hen_sentences) >= 3:
        findings.append(
            Finding(
                path,
                1,
                1,
                "dense_hen_judgments",
                2,
                "过密 `X 很 X` 判断句。合并、缩短或改成具体细节。",
                f"{len(hen_sentences)} sentences",
            )
        )

    for paragraph in text.split("\n\n"):
        stripped = paragraph.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(">"):
            continue
        compact = re.sub(r"\s+", "", stripped)
        if 24 <= len(compact) <= 90:
            paragraph_lengths.append(len(compact))
    if len(paragraph_lengths) >= 5 and max(paragraph_lengths) - min(paragraph_lengths) <= 12:
        findings.append(
            Finding(
                path,
                1,
                1,
                "over_even_paragraphs",
                1,
                "段落长度过于均匀。必要时打散段落重量。",
                str(paragraph_lengths[:8]),
            )
        )


def audit_text(path: str, text: str, lang: str) -> list[Finding]:
    active = detect_language(text) if lang == "auto" else lang
    if active != "zh":
        return []
    findings: list[Finding] = []
    add_rule_findings(path, text, findings)
    add_table_findings(path, text, findings)
    add_shape_findings(path, text, findings)
    findings.sort(key=lambda item: (item.line, -item.severity, item.rule_id))
    return findings


def read_inputs(paths: list[str]) -> list[tuple[str, str]]:
    if not paths:
        return [("<stdin>", sys.stdin.read())]
    inputs = []
    for raw in paths:
        inputs.append((raw, Path(raw).read_text()))
    return inputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Files to audit. Reads stdin when omitted.")
    parser.add_argument("--lang", choices=("auto", "zh"), default="auto")
    parser.add_argument("--fail-on-review", action="store_true", help="Exit 1 when a high-severity finding is present.")
    args = parser.parse_args()

    all_findings: list[Finding] = []
    for path, text in read_inputs(args.paths):
        all_findings.extend(audit_text(path, text, args.lang))

    if all_findings:
        for finding in all_findings:
            print(finding.render())
    else:
        print("ai flavor check: ok")

    has_high_severity = any(finding.severity >= 3 for finding in all_findings)
    return 1 if args.fail_on_review and has_high_severity else 0


if __name__ == "__main__":
    raise SystemExit(main())
