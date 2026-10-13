"""Release-note guidance stays artifact-bounded and does not impose a quota."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_write_release_copy_is_explicit_and_artifact_bounded() -> None:
    skill = read("skills/write/SKILL.md")
    notes = read("skills/write/references/write-zh-release-notes.md")

    assert "/write" in skill
    assert "显式调用" in skill
    assert "事实主张基于产物" in skill
    assert "发布说明要工程师可读" in skill
    assert "5 到 8 条足够，除非发布规模很小或很大" in notes
    assert "全面优化体验" in notes


def test_release_guidance_does_not_turn_previous_item_count_into_a_quota() -> None:
    surfaces = {
        "write skill": read("skills/write/SKILL.md"),
        "Chinese release notes": read(
            "skills/write/references/write-zh-release-notes.md"
        ),
    }
    stale_contracts = (
        "Match the reference release's item count",
        "建议 5 到 8 条",
        "item count, per-item length, and language layout as the hard template",
        "5 to 8 items total",
    )

    for name, text in surfaces.items():
        for stale in stale_contracts:
            assert stale not in text, f"{name}: {stale}"
