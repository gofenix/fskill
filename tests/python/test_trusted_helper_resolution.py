"""Shipped skills run bundled helpers from the installed skill directory."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_write_and_read_helpers_stay_inside_the_skill_directory():
    write = (ROOT / "skills" / "write" / "SKILL.md").read_text(encoding="utf-8")
    methods = (ROOT / "skills" / "read" / "references" / "read-methods.md").read_text(
        encoding="utf-8"
    )

    assert 'bash "$SKILL_DIR/scripts/check-punctuation.sh"' in write
    assert "不要在目标项目里寻找同名脚本" in methods
    assert 'bash "$SKILL_DIR/scripts/fetch.sh"' in methods
    for text in (write, methods):
        assert "npx skills path" not in text
        assert "./skills/" not in text
