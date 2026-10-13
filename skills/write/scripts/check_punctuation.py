#!/usr/bin/env python3
"""Check common punctuation mistakes in prose files.

The checker is intentionally conservative: it skips fenced code blocks, inline
code, URLs, and link destinations, and it only reports patterns that are very likely to be style
bugs in human prose. It has no third-party dependencies so the copied write
skill can run standalone.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

CJK = r"\u3400-\u4dbf\u4e00-\u9fff"
KANA = r"\u3040-\u30ff"
HANGUL = r"\uac00-\ud7af"
CJK_OR_KANA = CJK + KANA
LATIN_OR_DIGIT = r"A-Za-z0-9"

CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.*?)\1(?!`)")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
MD_LINK_RE = re.compile(r"\[[^\]]*\](\((?:[^()]|\([^()]*\))*\))")
WIKILINK_RE = re.compile(r"\[\[[^\[\]\n]*\]\]")
REFERENCE_RE = re.compile(r"^ {0,3}\[[^\]]+\]:\s*\S")


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    column: int
    message: str

    def render(self) -> str:
        return f"{self.path}:{self.line}:{self.column}: {self.message}"


def protected_mask(line: str) -> list[bool]:
    """Protect code and destinations; wikilink dialects disagree on alias order."""
    mask = [False] * len(line)
    spans = [m.span() for pattern in (CODE_SPAN_RE, URL_RE, WIKILINK_RE)
             for m in pattern.finditer(line)]
    spans.extend(m.span(1) for m in MD_LINK_RE.finditer(line))
    for start, end in spans:
        mask[start:end] = [True] * (end - start)
    return mask


def mask_ignored_spans(line: str) -> str:
    """Keep finding columns stable while hiding protected content."""
    return "".join(" " if hidden else char
                   for char, hidden in zip(line, protected_mask(line)))


def text_lines(text: str):
    """Yield original lines and whether they belong to a protected block."""
    fence = None
    for line in text.splitlines(keepends=True):
        match = FENCE_RE.match(line.rstrip("\r\n"))
        if fence is not None:
            if (match and match[1][0] == fence[0]
                    and len(match[1]) >= fence[1] and not match[2].strip()):
                fence = None
            yield line, True
        elif match and not (match[1][0] == "`" and "`" in match[2]):
            fence = (match[1][0], len(match[1]))
            yield line, True
        else:
            yield line, line.startswith(("    ", "\t")) or bool(REFERENCE_RE.match(line))


def prose_lines(text: str):
    for number, (line, protected) in enumerate(text_lines(text), start=1):
        if not protected:
            yield number, mask_ignored_spans(line.rstrip("\r\n"))


def fix_prose(text: str, transform) -> str:
    output = []
    for line, protected in text_lines(text):
        if protected:
            output.append(line)
            continue
        mask = protected_mask(line)
        start = 0
        while start < len(line):
            end = start + 1
            while end < len(line) and mask[end] == mask[start]:
                end += 1
            chunk = line[start:end]
            output.append(chunk if mask[start] else transform(chunk))
            start = end
    return "".join(output)


def detect_language(text: str) -> str:
    kana = len(re.findall(f"[{KANA}]", text))
    hangul = len(re.findall(f"[{HANGUL}]", text))
    cjk = len(re.findall(f"[{CJK}]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if hangul > cjk + kana:
        return "ko"
    if kana:
        return "ja"
    if cjk:
        return "zh"
    if latin:
        return "en"
    return "en"


def add_regex_findings(
    findings: list[Finding],
    path: str,
    line_no: int,
    line: str,
    pattern: str,
    message: str,
):
    for match in re.finditer(pattern, line):
        findings.append(Finding(path, line_no, match.start() + 1, message))


def check_zh(path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_no, line in prose_lines(text):
        add_regex_findings(
            findings,
            path,
            line_no,
            line,
            rf"[{CJK_OR_KANA}][,;:!?]|[,;:!?][{CJK_OR_KANA}]",
            "中文语境里使用了半角标点，改成全角标点。",
        )
        add_regex_findings(
            findings,
            path,
            line_no,
            line,
            rf"[{CJK_OR_KANA}]\.(?!\d)|(?<!\d)\.[{CJK_OR_KANA}]",
            "中文语境里使用了半角句号，改成全角句号。",
        )
        add_regex_findings(
            findings,
            path,
            line_no,
            line,
            rf"[{CJK_OR_KANA}][{LATIN_OR_DIGIT}]|[{LATIN_OR_DIGIT}][{CJK_OR_KANA}]",
            "中文和英文/数字之间通常需要空格。",
        )
        add_regex_findings(findings, path, line_no, line, r"[\u2013\u2014]", "不要使用 en dash/em dash。")
        add_regex_findings(findings, path, line_no, line, r"\u3000", "不要使用全角空格。")
    return findings


def check_en(path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_no, line in prose_lines(text):
        add_regex_findings(
            findings,
            path,
            line_no,
            line,
            r"[，。！？；：、]",
            "英文语境里使用了中文全角标点。",
        )
        add_regex_findings(findings, path, line_no, line, r"[\u2013\u2014]", "Avoid en dash/em dash.")
        add_regex_findings(
            findings,
            path,
            line_no,
            line,
            r"[,;:](?=[A-Za-z])",
            "英文逗号、分号或冒号后需要空格。",
        )
    return findings


def check_ja(path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_no, line in prose_lines(text):
        add_regex_findings(
            findings,
            path,
            line_no,
            line,
            rf"[{CJK_OR_KANA}][,.;:!?]|[,.;:!?][{CJK_OR_KANA}]",
            "日文语境里使用了半角标点，改成日文标点。",
        )
        add_regex_findings(findings, path, line_no, line, r"[\u2013\u2014]", "不要使用 en dash/em dash。")
    return findings


def fix_zh(text: str) -> str:
    punctuation = {
        ",": "，",
        ".": "。",
        ":": "：",
        ";": "；",
        "!": "！",
        "?": "？",
    }
    fixed = text.replace("\u3000", " ")
    for ascii_punct, fullwidth in punctuation.items():
        escaped = re.escape(ascii_punct)
        fixed = re.sub(rf"([{CJK_OR_KANA}]){escaped}", rf"\1{fullwidth}", fixed)
        fixed = re.sub(rf"{escaped}([{CJK_OR_KANA}])", rf"{fullwidth}\1", fixed)
    fixed = re.sub(rf"([{CJK_OR_KANA}])([{LATIN_OR_DIGIT}])", r"\1 \2", fixed)
    fixed = re.sub(rf"([{LATIN_OR_DIGIT}])([{CJK_OR_KANA}])", r"\1 \2", fixed)
    return fixed


def fix_en(text: str) -> str:
    table = str.maketrans({"，": ",", "。": ".", "！": "!", "？": "?", "；": ";", "：": ":", "、": ","})
    fixed = text.translate(table)
    return re.sub(r"([,;:])(?=[A-Za-z])", r"\1 ", fixed)


def check_text(path: str, text: str, lang: str) -> list[Finding]:
    active = detect_language(text) if lang == "auto" else lang
    if active == "ko":
        return []
    if active == "zh":
        return check_zh(path, text)
    if active == "ja":
        return check_ja(path, text)
    return check_en(path, text)


def read_inputs(paths: list[str]) -> list[tuple[str, str]]:
    if not paths:
        return [("<stdin>", sys.stdin.read())]
    inputs = []
    for raw in paths:
        path = Path(raw)
        inputs.append((raw, path.read_text()))
    return inputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Files to check. Reads stdin when omitted.")
    parser.add_argument("--lang", choices=("auto", "zh", "en", "ja", "ko"), default="auto")
    parser.add_argument("--fix", action="store_true", help="Print fixed text to stdout for a single input.")
    args = parser.parse_args()

    inputs = read_inputs(args.paths)
    if args.fix:
        if len(inputs) != 1:
            raise SystemExit("--fix accepts exactly one file or stdin input")
        _path, text = inputs[0]
        active = detect_language(text) if args.lang == "auto" else args.lang
        if active == "zh":
            sys.stdout.write(fix_prose(text, fix_zh))
        elif active == "en":
            sys.stdout.write(fix_prose(text, fix_en))
        else:
            sys.stdout.write(text)
        return 0

    findings: list[Finding] = []
    for path, text in inputs:
        findings.extend(check_text(path, text, args.lang))
    if findings:
        for finding in findings:
            print(finding.render(), file=sys.stderr)
        return 1
    print("punctuation check: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
