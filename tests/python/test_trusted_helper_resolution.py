"""Shipped skills resolve executable helpers only below their install base."""

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


def section(path: Path, heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index(f"## {heading}") + len(f"## {heading}")
    end = text.find("\n## ", start)
    return text[start:] if end == -1 else text[start:end]


@pytest.mark.parametrize(
    ("path", "heading", "direct_path", "bundled_path"),
    [
        (
            ROOT / "skills" / "write" / "SKILL.md",
            "Punctuation Gate",
            "<skill-base-dir>/scripts/check-punctuation.sh",
            "<skill-base-dir>/skills/write/scripts/check-punctuation.sh",
        ),
        (
            ROOT / "skills" / "read" / "references" / "read-methods.md",
            "Helper Directory",
            "<skill-base-dir>/scripts",
            "<skill-base-dir>/skills/read/scripts",
        ),
    ],
)
def test_helper_resolution_has_no_project_or_package_execution_fallback(
    path: Path,
    heading: str,
    direct_path: str,
    bundled_path: str,
):
    body = section(path, heading)

    assert direct_path in body
    assert bundled_path in body
    assert "./skills/" not in body
    assert "npx skills path" not in body
