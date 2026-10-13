import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "health" / "scripts" / "check_doc_refs.py"


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlink support required")
def test_external_global_instruction_symlink_is_unverifiable_not_missing(tmp_path: Path):
    project = tmp_path / "project"
    home = tmp_path / "home"
    outside = tmp_path / "outside"
    project.mkdir()
    (home / ".claude").mkdir(parents=True)
    outside.mkdir()
    (project / "AGENTS.md").write_text(
        "Global rules: `~/.claude/CLAUDE.md`.\n", encoding="utf-8"
    )
    (outside / "CLAUDE.md").write_text("PRIVATE_EXTERNAL_CONTENT\n", encoding="utf-8")
    (home / ".claude" / "CLAUDE.md").symlink_to(outside / "CLAUDE.md")

    result = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), str(project)],
        env={**os.environ, "HOME": str(home)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0
    assert "UNVERIFIED_EXTERNAL: AGENTS.md:1 -> ~/.claude/CLAUDE.md" in result.stdout
    assert "MISSING:" not in result.stdout
    assert "PRIVATE_EXTERNAL_CONTENT" not in result.stdout
