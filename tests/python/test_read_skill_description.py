import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "health" / "scripts" / "read_skill_description.py"
SPEC = importlib.util.spec_from_file_location("read_skill_description", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_inline_description() -> None:
    text = '---\nname: demo\ndescription: "One line description"\n---\nbody\n'

    assert MODULE.parse_description(text) == "One line description"


def test_folded_description_is_complete_and_single_line() -> None:
    text = (
        "---\n"
        "name: demo\n"
        "description: >-\n"
        "  First trigger sentence.\n"
        "  Not for unrelated work.\n"
        "---\n"
        "body\n"
    )

    assert MODULE.parse_description(text) == (
        "First trigger sentence. Not for unrelated work."
    )


def test_description_outside_frontmatter_is_ignored() -> None:
    text = "---\nname: demo\n---\ndescription: body text\n"

    assert MODULE.parse_description(text) == ""
