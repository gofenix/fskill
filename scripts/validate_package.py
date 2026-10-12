#!/usr/bin/env python3
"""Post-package integrity check for the Claude Desktop dispatcher ZIP.

Invoked by scripts/package-skill.sh after the ZIP is unpacked into a temp
directory. Verifies the generated root SKILL.md exists, carries the ninja
marker, inlines every skill section, and has no broken nested SKILL.md path
references.

Lives in scripts/ (build-time only); never shipped to end users, so it stays
a real file rather than a heredoc.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


EXPECTED_SKILLS = [
    "think",
    "how",
    "design",
    "check",
    "hunt",
    "write",
    "learn",
    "read",
    "health",
    "handoff",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", type=Path, help="Extracted ZIP root")
    args = parser.parse_args()

    root_skill = args.stage / "SKILL.md"
    if not root_skill.exists():
        print("POST-PACKAGE ERROR: SKILL.md missing from extracted ZIP", file=sys.stderr)
        return 1

    text = root_skill.read_text()

    if "Prefix your first line with 🥷 inline" not in text:
        print(
            "POST-PACKAGE ERROR: root SKILL.md missing ninja prefix instruction",
            file=sys.stderr,
        )
        return 1

    for skill in EXPECTED_SKILLS:
        if f"# SKILL: {skill}" not in text:
            print(
                f"POST-PACKAGE ERROR: SKILL section '{skill}' not inlined in root SKILL.md",
                file=sys.stderr,
            )
            return 1

    # The packager rewrites `skills/<name>/SKILL.md` references to the inlined
    # section name. Any stragglers indicate a regex bug in the rewriter.
    for skill in EXPECTED_SKILLS:
        if f"skills/{skill}/SKILL.md" in text:
            print(
                "POST-PACKAGE ERROR: root SKILL.md still contains nested "
                f"SKILL.md path references (e.g. skills/{skill}/SKILL.md)",
                file=sys.stderr,
            )
            return 1

    print("ok: post-package validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
