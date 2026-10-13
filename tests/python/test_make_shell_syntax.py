"""Exercise the real Make recipe with syntax errors beyond the first file."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("broken", [None, "source-b.sh", "tests/test_b.sh", "tests/test_helpers.sh"])
def test_verify_scripts_checks_each_shell_file(tmp_path, broken):
    shutil.copyfile(ROOT / "Makefile", tmp_path / "Makefile")
    for name in ("source-a.sh", "source-b.sh", "tests/test_a.sh", "tests/test_b.sh", "tests/test_helpers.sh"):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("if then\n" if name == broken else "true\n")

    # Isolate unrelated checks; Bash and Make remain the real executables.
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("git", "python3", "shellcheck"):
        path = bin_dir / name
        path.write_text("#!/bin/sh\nexit 0\n")
        path.chmod(0o755)
    collector = tmp_path / "skills/health/scripts/collect-data.sh"
    collector.parent.mkdir(parents=True)
    collector.write_text(
        "printf '%s\\n' "
        "'=== CONVERSATION SIGNALS ===' '=== AGENT CONFIG SUMMARY ===' "
        "'=== AI MAINTAINABILITY SUMMARY ==='\n"
    )
    result = subprocess.run(
        ["make", "-s", "verify-scripts", f"PROJECT_KEY={tmp_path.name}-{os.getpid()}",
         "SHELL_SOURCES=source-a.sh source-b.sh", "TEST_FILES=tests/test_a.sh tests/test_b.sh",
         "PY_SOURCES="],
        cwd=tmp_path,
        env={**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"},
        capture_output=True,
        text=True,
    )
    if broken is None:
        assert result.returncode == 0, result.stdout + result.stderr
    else:
        assert result.returncode != 0, result.stdout + result.stderr
        assert broken in result.stderr
