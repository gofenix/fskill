#!/usr/bin/env python3
"""Verify dispatcher routing table and RESOLVER.md cover every skill.

Both files must reference the same set of skill names found under
`skills/*/SKILL.md`. Treated as a sanity tripwire alongside the codegen in
`build_metadata.py`; cheap enough to keep even after routing tables become
generated.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skill_frontmatter import skill_ref_diff  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root (default: parent of scripts/)",
    )
    args = parser.parse_args()
    root = args.root.resolve()

    expected = {
        p.parent.name for p in (root / "skills").glob("*/SKILL.md")
    }
    if not expected:
        print("ERROR: no skills found under skills/*/SKILL.md", file=sys.stderr)
        return 1

    drift = False
    for label, path in (
        ("scripts/dispatcher.md", root / "scripts" / "dispatcher.md"),
        ("RESOLVER.md", root / "skills" / "RESOLVER.md"),
    ):
        missing, stale = skill_ref_diff(path.read_text(), expected)
        if missing:
            print(
                f"ROUTING DRIFT: skills missing from {label}: {missing}",
                file=sys.stderr,
            )
            drift = True
        if stale:
            print(
                f"ROUTING DRIFT: stale skill refs in {label}: {stale}",
                file=sys.stderr,
            )
            drift = True

    if drift:
        return 1

    print(
        f"ok: routing consistent across {len(expected)} skills (scripts/dispatcher.md + RESOLVER.md)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
