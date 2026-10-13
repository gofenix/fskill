#!/usr/bin/env python3
"""Filter stdin paths through packaging.allowlist. Default-deny."""

import fnmatch
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skill_frontmatter import should_include_codex_mirror_file  # noqa: E402

# Nested SKILL.md files are inlined into the generated root SKILL.md by the
# packager, so they never ship as standalone files, and the resolver table is
# superseded by the dispatcher routing already inlined at the ZIP root.
# Cache/noise filtering is shared with the mirror generator and verifier via
# skill_frontmatter.
PACKAGING_EXCLUDE_RE = re.compile(r"^skills/([^/]+/)?SKILL\.md$|^skills/RESOLVER\.md$")


def load_patterns(path: Path) -> list[str]:
    patterns = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def allowed(path: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if pat.endswith("/**"):
            prefix = pat[:-3]
            if path == prefix or path.startswith(prefix + "/"):
                return True
        elif fnmatch.fnmatch(path, pat):
            return True
    return False


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: packaging_filter.py <allowlist-path>", file=sys.stderr)
        return 2
    patterns = load_patterns(Path(sys.argv[1]))
    for line in sys.stdin:
        path = line.rstrip("\n")
        if not path:
            continue
        if PACKAGING_EXCLUDE_RE.match(path) or not should_include_codex_mirror_file(Path(path)):
            continue
        if allowed(path, patterns):
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
