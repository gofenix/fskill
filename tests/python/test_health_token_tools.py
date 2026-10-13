"""Health reports rtk and codegraph without trusting project-local copies."""

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "health" / "scripts" / "check-token-tools.sh"


def write_executable(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def run_check(tmp_path: Path, path: str, home: Path) -> str:
    project = tmp_path / "project"
    project.mkdir()
    env = os.environ.copy()
    env["PATH"] = path
    env["HOME"] = str(home)
    result = subprocess.run(
        ["/bin/bash", str(SCRIPT), str(project)],
        cwd=project,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_path_tools_report_presence_and_missing_index(tmp_path: Path):
    bindir = tmp_path / "bin"
    write_executable(bindir / "rtk", "#!/bin/sh\nexit 0\n")
    write_executable(
        bindir / "codegraph",
        "#!/bin/sh\nprintf 'Not initialized\\n'\nexit 0\n",
    )

    out = run_check(tmp_path, f"{bindir}:/usr/bin:/bin", tmp_path / "home")

    assert "rtk_present: yes" in out
    assert "codegraph_present: yes" in out
    assert "codegraph_index: missing" in out
    assert "rtk_off_path:" not in out


def test_home_install_is_off_path_when_path_misses_it(tmp_path: Path):
    home = tmp_path / "home"
    write_executable(home / ".local" / "bin" / "rtk", "#!/bin/sh\nexit 0\n")

    out = run_check(tmp_path, "/usr/bin:/bin", home)

    assert "rtk_present: no" in out
    assert "rtk_off_path: ~/.local/bin/rtk" in out


def test_project_local_executable_is_not_treated_as_installed(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    write_executable(project / "bin" / "rtk", "#!/bin/sh\nexit 0\n")
    write_executable(project / "bin" / "codegraph", "#!/bin/sh\nexit 0\n")
    env = os.environ.copy()
    env["PATH"] = f"{project / 'bin'}:/usr/bin:/bin"
    env["HOME"] = str(tmp_path / "empty-home")
    result = subprocess.run(
        ["/bin/bash", str(SCRIPT), str(project)],
        cwd=project,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "rtk_present: no" in result.stdout
    assert "codegraph_present: no" in result.stdout
    assert str(project) not in result.stdout
    assert "codegraph_index: unavailable" in result.stdout
