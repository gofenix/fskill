"""Behavior contracts for release-note writing and shipping guidance."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_release_note_mode_is_artifact_bounded_and_outcome_sized() -> None:
    mode = read("skills/write/references/mode-release-notes.md")

    assert "exact candidate users will receive" in mode
    assert "Use `HEAD` only when the candidate is built from `HEAD`" in mode
    assert "git log <last-published>..<candidate>" in mode
    assert "smallest set of distinct user outcomes" in mode
    assert "whether the reader can see the result or must act" in mode


def test_release_note_mode_keeps_only_audience_useful_technical_terms() -> None:
    mode = read("skills/write/references/mode-release-notes.md")

    assert "Keep technical terms only when the intended reader uses them" in mode
    assert "Settle structure before localization" in mode
    assert "same item count and order" in mode


def test_release_guidance_does_not_turn_previous_item_count_into_a_quota() -> None:
    surfaces = {
        "write mode": read("skills/write/references/mode-release-notes.md"),
        "Chinese release notes": read(
            "skills/write/references/write-zh-release-notes.md"
        ),
        "shipping mode": read("skills/check/references/mode-ship.md"),
        "Waza guide": read("AGENTS.md"),
    }
    stale_contracts = (
        "Match the reference release's item count",
        "建议 5 到 8 条",
        "item count, per-item length, and language layout as the hard template",
        "5 to 8 items total",
    )

    for name, text in surfaces.items():
        assert any(
            marker in text
            for marker in ("fixed count", "quota", "not a target", "配额")
        ), name
        for stale in stale_contracts:
            assert stale not in text, f"{name}: {stale}"
