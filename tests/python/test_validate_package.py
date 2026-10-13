"""Unit tests for the Claude Desktop package entrypoint rewriter and validator."""

from pathlib import Path

import pytest

import validate_package as vp


NINJA = "Prefix your first line with 🥷 inline, not as its own paragraph."


def test_rewrite_skill_runtime_paths_qualifies_only_existing_skill_paths(tmp_path):
    skill_root = tmp_path / "demo"
    for relative in (
        "references/guide.md",
        "agents/reviewer.md",
        "scripts/run.py",
    ):
        target = skill_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fixture\n")

    text = """
[guide](references/guide.md#usage)
[angle](<references/guide.md>)
`references/guide.md`
`agents/reviewer.md`
`scripts/run.py`
[external](https://example.com/references/guide.md)
`scripts/build_metadata.py`
`references/...`
plain references/guide.md
`<skill-base-dir>/scripts/run.py`
[qualified](skills/demo/references/guide.md)
"""

    rewritten = vp.rewrite_skill_runtime_paths(
        text,
        "demo",
        skill_root=skill_root,
    )

    assert "[guide](skills/demo/references/guide.md#usage)" in rewritten
    assert "[angle](<skills/demo/references/guide.md>)" in rewritten
    assert "`skills/demo/references/guide.md`" in rewritten
    assert "`skills/demo/agents/reviewer.md`" in rewritten
    assert "`skills/demo/scripts/run.py`" in rewritten
    assert "[external](https://example.com/references/guide.md)" in rewritten
    assert "`scripts/build_metadata.py`" in rewritten
    assert "`references/...`" in rewritten
    assert "plain references/guide.md" in rewritten
    assert "`<skill-base-dir>/scripts/run.py`" in rewritten
    assert "[qualified](skills/demo/references/guide.md)" in rewritten


def test_validate_stage_accepts_closed_markdown_and_backtick_paths(tmp_path):
    stage = tmp_path / "stage"
    (stage / "skills/demo/references").mkdir(parents=True)
    (stage / "skills/demo/references/guide.md").write_text("# Usage\n\nfixture\n")
    (stage / "SKILL.md").write_text(
        f"{NINJA}\n"
        "# SKILL: demo\n"
        "[guide](skills/demo/references/guide.md#usage)\n"
        "`skills/demo/references/guide.md`\n"
    )

    assert vp.validate_stage(stage, ["demo"]) == []


def test_validate_stage_rejects_missing_markdown_and_backtick_paths(tmp_path):
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "SKILL.md").write_text(
        f"{NINJA}\n"
        "# SKILL: demo\n"
        "[guide](skills/demo/references/missing-link.md)\n"
        "`skills/demo/scripts/missing-backtick.py`\n"
    )

    errors = vp.validate_stage(stage, ["demo"])

    assert any(
        "missing Markdown link target: skills/demo/references/missing-link.md"
        in error
        for error in errors
    )
    assert any(
        "missing backtick path target: skills/demo/scripts/missing-backtick.py"
        in error
        for error in errors
    )


def test_validate_stage_rejects_unrewritten_skill_relative_path(tmp_path):
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "SKILL.md").write_text(
        f"{NINJA}\n"
        "# SKILL: demo\n"
        "`references/missing.md`\n"
    )

    errors = vp.validate_stage(stage, ["demo"])

    assert any(
        "missing backtick path target: references/missing.md" in error
        for error in errors
    )


def test_validate_stage_rejects_runtime_path_that_escapes_package(tmp_path):
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "SKILL.md").write_text(
        f"{NINJA}\n"
        "# SKILL: demo\n"
        "[escape](references/../../outside.md)\n"
    )

    errors = vp.validate_stage(stage, ["demo"])

    assert any(
        "Markdown link escapes package root: references/../../outside.md" in error
        for error in errors
    )


@pytest.mark.parametrize(
    "reference",
    (
        "../outside.md",
        "%2e%2e/outside.md",
        "/outside.md",
    ),
)
def test_validate_stage_rejects_leading_package_traversal(tmp_path, reference):
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "SKILL.md").write_text(
        f"{NINJA}\n"
        "# SKILL: demo\n"
        f"[escape]({reference})\n"
    )

    errors = vp.validate_stage(stage, ["demo"])

    assert any(
        f"Markdown link escapes package root: {reference}" in error
        for error in errors
    )


def test_nested_reference_rewrites_reference_agent_and_script_paths(tmp_path):
    stage = tmp_path / "stage"
    skill_root = stage / "skills/demo"
    targets = (
        "references/next.md",
        "agents/reviewer.md",
        "scripts/run.py",
    )
    for relative in targets:
        target = skill_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fixture\n")

    nested = skill_root / "references/mode.md"
    nested.write_text(
        "`references/next.md`\n"
        "`agents/reviewer.md`\n"
        "`scripts/run.py`\n"
    )
    nested.write_text(
        vp.rewrite_skill_runtime_paths(
            nested.read_text(),
            "demo",
            skill_root=skill_root,
        )
    )
    (stage / "SKILL.md").write_text(f"{NINJA}\n# SKILL: demo\n")

    rewritten = nested.read_text()
    assert "`skills/demo/references/next.md`" in rewritten
    assert "`skills/demo/agents/reviewer.md`" in rewritten
    assert "`skills/demo/scripts/run.py`" in rewritten
    assert vp.validate_stage(stage, ["demo"]) == []


def test_validate_stage_rejects_missing_path_in_nested_markdown(tmp_path):
    stage = tmp_path / "stage"
    nested = stage / "skills/demo/references/mode.md"
    nested.parent.mkdir(parents=True)
    nested.write_text("`skills/demo/agents/missing.md`\n")
    (stage / "SKILL.md").write_text(f"{NINJA}\n# SKILL: demo\n")

    errors = vp.validate_stage(stage, ["demo"])

    assert any(
        "skills/demo/references/mode.md:1: missing backtick path target: "
        "skills/demo/agents/missing.md" in error
        for error in errors
    )


def test_rewrite_resolves_unique_basename_inside_skill_runtime_tree(tmp_path):
    skill_root = tmp_path / "demo"
    references = skill_root / "references"
    references.mkdir(parents=True)
    (references / "project-context.md").write_text("fixture\n")

    rewritten = vp.rewrite_skill_runtime_paths(
        "`project-context.md`\n",
        "demo",
        skill_root=skill_root,
    )

    assert rewritten == "`skills/demo/references/project-context.md`\n"


def test_validate_stage_rejects_unqualified_unique_nested_basename(tmp_path):
    stage = tmp_path / "stage"
    references = stage / "skills/demo/references"
    references.mkdir(parents=True)
    (references / "project-context.md").write_text("fixture\n")
    (references / "release-surfaces.md").write_text("`project-context.md`\n")
    (stage / "SKILL.md").write_text(f"{NINJA}\n# SKILL: demo\n")

    errors = vp.validate_stage(stage, ["demo"])

    assert any(
        "skills/demo/references/release-surfaces.md:1: "
        "unqualified backtick path: project-context.md "
        "(expected skills/demo/references/project-context.md)" in error
        for error in errors
    )


def test_rewrite_preserves_percent_encoding_in_qualified_output(tmp_path):
    skill_root = tmp_path / "demo"
    references = skill_root / "references"
    references.mkdir(parents=True)
    for name in ("guide name.md", "topic#one.md", "query?one.md"):
        (references / name).write_text("fixture\n")

    text = (
        "`references/guide%20name.md`\n"
        "`guide%20name.md`\n"
        "`references/topic%23one.md`\n"
        "`references/query%3Fone.md`\n"
    )
    rewritten = vp.rewrite_skill_runtime_paths(
        text,
        "demo",
        skill_root=skill_root,
    )

    assert rewritten == (
        "`skills/demo/references/guide%20name.md`\n"
        "`skills/demo/references/guide%20name.md`\n"
        "`skills/demo/references/topic%23one.md`\n"
        "`skills/demo/references/query%3Fone.md`\n"
    )


def test_validate_stage_decodes_percent_only_for_disk_lookup(tmp_path):
    stage = tmp_path / "stage"
    references = stage / "skills/demo/references"
    references.mkdir(parents=True)
    for name in ("guide name.md", "topic#one.md", "query?one.md"):
        (references / name).write_text("fixture\n")
    (stage / "SKILL.md").write_text(
        f"{NINJA}\n"
        "# SKILL: demo\n"
        "`skills/demo/references/guide%20name.md`\n"
        "`skills/demo/references/topic%23one.md`\n"
        "`skills/demo/references/query%3Fone.md`\n"
    )

    assert vp.validate_stage(stage, ["demo"]) == []


def test_basename_prefers_current_directory_but_skips_ambiguous_skill_match(
    tmp_path,
):
    skill_root = tmp_path / "demo"
    for relative in ("references/shared.md", "agents/shared.md"):
        target = skill_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fixture\n")

    nested = vp.rewrite_skill_runtime_paths(
        "`shared.md`\n",
        "demo",
        skill_root=skill_root,
        source_relative=Path("references/mode.md"),
    )
    root = vp.rewrite_skill_runtime_paths(
        "`shared.md`\n",
        "demo",
        skill_root=skill_root,
        source_relative=Path("SKILL.md"),
    )

    assert nested == "`skills/demo/references/shared.md`\n"
    assert root == "`shared.md`\n"


def test_validate_stage_uses_inlined_root_skill_context_for_basename(tmp_path):
    stage = tmp_path / "stage"
    references = stage / "skills/demo/references"
    references.mkdir(parents=True)
    (references / "guide.md").write_text("fixture\n")
    (stage / "SKILL.md").write_text(
        f"{NINJA}\n"
        "# SKILL: demo\n"
        "`guide.md`\n"
    )

    errors = vp.validate_stage(stage, ["demo"])

    assert any(
        "SKILL.md:3: unqualified backtick path: guide.md "
        "(expected skills/demo/references/guide.md)" in error
        for error in errors
    )


def test_validate_stage_rejects_ambiguous_inlined_root_basename(tmp_path):
    stage = tmp_path / "stage"
    for relative in (
        "skills/demo/agents/shared.md",
        "skills/demo/references/shared.md",
    ):
        target = stage / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fixture\n")
    (stage / "SKILL.md").write_text(
        f"{NINJA}\n"
        "# SKILL: demo\n"
        "Load `shared.md`.\n"
        "[shared](shared.md)\n"
    )

    errors = vp.validate_stage(stage, ["demo"])

    assert any(
        "SKILL.md:3: ambiguous backtick path: shared.md "
        "(matches skills/demo/agents/shared.md, "
        "skills/demo/references/shared.md)" in error
        for error in errors
    )
    assert any(
        "SKILL.md:4: ambiguous Markdown link: shared.md "
        "(matches skills/demo/agents/shared.md, "
        "skills/demo/references/shared.md)" in error
        for error in errors
    )


def test_validate_stage_rejects_missing_basename_markdown_link(tmp_path):
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "SKILL.md").write_text(
        f"{NINJA}\n"
        "# SKILL: demo\n"
        "[typo](missing.md)\n"
    )

    errors = vp.validate_stage(stage, ["demo"])

    assert any(
        "SKILL.md:3: missing Markdown link target: missing.md" in error
        for error in errors
    )


def test_validate_stage_rejects_missing_markdown_fragment(tmp_path):
    stage = tmp_path / "stage"
    reference = stage / "skills/demo/references/guide.md"
    reference.parent.mkdir(parents=True)
    reference.write_text("# Existing heading\n")
    (stage / "SKILL.md").write_text(
        f"{NINJA}\n"
        "# SKILL: demo\n"
        "[guide](skills/demo/references/guide.md#missing-heading)\n"
    )

    errors = vp.validate_stage(stage, ["demo"])

    assert any(
        "SKILL.md:3: missing Markdown fragment: "
        "skills/demo/references/guide.md#missing-heading" in error
        for error in errors
    )


def test_validate_stage_rejects_cross_skill_inlined_fragment(tmp_path):
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "SKILL.md").write_text(
        f"{NINJA}\n"
        "# SKILL: alpha\n"
        "## Hard Rules\n"
        "# SKILL: beta\n"
        "[own rules](#hard-rules)\n"
        "## Hard Rules\n"
    )

    errors = vp.validate_stage(stage, ["alpha", "beta"])

    assert any(
        "SKILL.md:5: cross-skill same-document Markdown fragment: "
        "#hard-rules targets alpha"
        in error
        for error in errors
    )


def test_validate_stage_allows_project_doc_names_in_backticks(tmp_path):
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "SKILL.md").write_text(
        f"{NINJA}\n"
        "# SKILL: demo\n"
        "Read `AGENTS.md` and `CLAUDE.md` from the target project.\n"
    )

    assert vp.validate_stage(stage, ["demo"]) == []


def test_validate_stage_allows_commands_and_target_paths_in_backticks(tmp_path):
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "SKILL.md").write_text(
        f"{NINJA}\n"
        "# SKILL: demo\n"
        "Run `/health` and inspect `/tmp/output`.\n"
    )

    assert vp.validate_stage(stage, ["demo"]) == []
