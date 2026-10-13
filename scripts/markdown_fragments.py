"""Markdown heading inventory using GitHub-compatible fragment semantics."""

from __future__ import annotations

import html
import re
from collections import Counter


ATX_HEADING_RE = re.compile(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$")
SETEXT_RE = re.compile(r"^ {0,3}(?:=+|-+)\s*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
REFERENCE_LINK_RE = re.compile(r"!?\[([^\]]*)\]\[[^\]]*\]")
CODE_SPAN_RE = re.compile(r"`+([^`]+?)`+")
AUTOLINK_RE = re.compile(
    r"<((?:https?://|mailto:)[^ >]+|[^ <>@]+@[^ <>]+)>",
    re.IGNORECASE,
)
HTML_TAG_RE = re.compile(r"<[^>]+>")
BLOCKQUOTE_RE = re.compile(r"^ {0,3}> ?")


def _rendered_heading_text(source: str) -> str:
    """Approximate the rendered text GitHub uses before slug generation."""
    text = INLINE_LINK_RE.sub(r"\1", source)
    text = REFERENCE_LINK_RE.sub(r"\1", text)
    text = CODE_SPAN_RE.sub(r"\1", text)
    text = AUTOLINK_RE.sub(r"\1", text)
    text = HTML_TAG_RE.sub("", text)
    return html.unescape(text)


def _base_fragment(source: str) -> str:
    rendered = _rendered_heading_text(source).lower().strip()
    rendered = re.sub(r"[^\w\-\s]", "", rendered)
    return re.sub(r"\s", "-", rendered)


def _heading_sources(markdown: str) -> list[tuple[str, int]]:
    sources: list[tuple[str, int]] = []
    paragraph: list[tuple[str, int]] = []
    paragraph_quote_depth = 0
    fence_char = ""
    fence_length = 0
    fence_quote_depth = 0

    for line_number, raw_line in enumerate(markdown.splitlines(), start=1):
        line = raw_line
        quote_depth = 0
        while (quote := BLOCKQUOTE_RE.match(line)) is not None:
            quote_depth += 1
            line = line[quote.end():]

        fence = FENCE_RE.match(line)
        if fence_char:
            if fence:
                marker = fence.group(1)
                if (
                    quote_depth == fence_quote_depth
                    and marker[0] == fence_char
                    and len(marker) >= fence_length
                    and not fence.group(2).strip()
                ):
                    fence_char = ""
                    fence_length = 0
                    fence_quote_depth = 0
            paragraph = []
            continue
        if fence:
            marker = fence.group(1)
            fence_char = marker[0]
            fence_length = len(marker)
            fence_quote_depth = quote_depth
            paragraph = []
            continue
        if line.startswith("    "):
            paragraph = []
            continue

        atx = ATX_HEADING_RE.match(line)
        if atx:
            sources.append((atx.group(1), line_number))
            paragraph = []
            continue

        if (
            SETEXT_RE.match(line)
            and paragraph
            and quote_depth == paragraph_quote_depth
        ):
            sources.append(
                ("".join(part.strip() for part, _ in paragraph), paragraph[0][1])
            )
            paragraph = []
            continue

        if not line.strip():
            paragraph = []
            continue
        if paragraph and quote_depth != paragraph_quote_depth:
            paragraph = []
        if not paragraph:
            paragraph_quote_depth = quote_depth
        paragraph.append((line, line_number))

    return sources


def github_heading_records(markdown: str) -> list[tuple[str, int]]:
    """Return collision-qualified GitHub anchors with their source line numbers."""
    records: list[tuple[str, int]] = []
    anchors: set[str] = set()
    for source, line_number in _heading_sources(markdown):
        base = _base_fragment(source)
        if not base:
            continue
        anchor = base
        suffix = 1
        while anchor in anchors:
            anchor = f"{base}-{suffix}"
            suffix += 1
        anchors.add(anchor)
        records.append((anchor, line_number))
    return records


def github_heading_inventory(markdown: str) -> tuple[set[str], Counter[str]]:
    """Return rendered anchors and pre-collision base counts for Markdown headings."""
    base_counts: Counter[str] = Counter()
    for source, _ in _heading_sources(markdown):
        base = _base_fragment(source)
        if not base:
            continue
        base_counts[base] += 1
    anchors = {anchor for anchor, _ in github_heading_records(markdown)}
    return anchors, base_counts
