from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "skills" / "ui"


def read(relative: str) -> str:
    return (UI / relative).read_text(encoding="utf-8")


def test_ui_is_explicit_and_keeps_design_references() -> None:
    skill = read("SKILL.md")
    assert "name: ui" in skill
    assert "/ui" in skill
    assert "显式调用" in skill
    assert "不自动切换技能" in skill
    for reference in (
        "references/design-reference.md",
        "references/design-traps.md",
        "references/design-tokens.md",
        "references/design-data-viz.md",
        "references/design-aesthetic-quality.md",
    ):
        assert reference in skill
        assert (UI / reference).is_file()
    for field in ("目标:", "完成条件:", "依据:", "交付形式:"):
        assert field in skill


def test_ui_skill_docs_contain_no_em_dash() -> None:
    paths = [UI / "SKILL.md", *sorted((UI / "references").glob("*.md"))]
    offenders = [
        str(path.relative_to(ROOT))
        for path in paths
        if "\u2014" in path.read_text(encoding="utf-8")
    ]
    assert offenders == []
