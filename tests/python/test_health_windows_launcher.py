"""Windows runtime tests for the Health-owned launcher."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "health" / "SKILL.md"
LAUNCHER = ROOT / "skills" / "health" / "scripts" / "run-health.ps1"
GITATTRIBUTES = ROOT / ".gitattributes"
POWERSHELL = shutil.which("powershell.exe") or shutil.which("pwsh")
WINDOWS_ONLY = pytest.mark.skipif(os.name != "nt", reason="Windows launcher test")

ACTION_SCRIPTS = {
    "collect": "collect-data.sh",
    "agent-context": "check-agent-context.sh",
    "maintainability": "check-maintainability.sh",
    "doc-refs": "check-doc-refs.sh",
    "verifier-output": "check-verifier-output.sh",
}


def run_launcher(
    launcher: Path,
    action: str,
    *script_args: str,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    assert POWERSHELL
    return subprocess.run(
        [
            POWERSHELL,
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(launcher),
            action,
            *script_args,
        ],
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )


def copy_launcher_fixture(tmp_path: Path) -> Path:
    scripts = tmp_path / "skill with spaces" / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy2(LAUNCHER, scripts / LAUNCHER.name)
    for action, script_name in ACTION_SCRIPTS.items():
        (scripts / script_name).write_text(
            f"printf '{action}:%s\\n' \"$*\"\n",
            encoding="utf-8",
        )
    return scripts / LAUNCHER.name


def clean_windows_env(tmp_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = os.pathsep.join(
        [
            str(Path(sys.executable).parent),
            str(Path(POWERSHELL).parent),
            str(Path(os.environ["SystemRoot"]) / "System32"),
            str(Path(shutil.which("git")).parent),
        ]
    )
    env["XDG_CACHE_HOME"] = str(tmp_path / "cache")
    return env


def git_install_root() -> Path:
    current = Path(shutil.which("git")).resolve().parent
    while current != current.parent:
        if (current / "bin" / "bash.exe").is_file() and (current / "usr" / "bin").is_dir():
            return current
        current = current.parent
    raise AssertionError("Git for Windows root not found")


def create_junction(link: Path, target: Path) -> None:
    result = subprocess.run(
        ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


@WINDOWS_ONLY
def test_derives_git_root_and_builds_child_path_without_mutating_parent(tmp_path: Path):
    launcher = copy_launcher_fixture(tmp_path)
    env = clean_windows_env(tmp_path)
    parent_path = os.environ["PATH"]

    result = run_launcher(launcher, "collect", cwd=tmp_path, env=env)

    assert result.returncode == 0, result.stderr
    assert result.stdout == "collect:\n"
    assert os.environ["PATH"] == parent_path


@WINDOWS_ONLY
def test_ignores_ambient_git_install_root(tmp_path: Path):
    launcher = copy_launcher_fixture(tmp_path)
    env = clean_windows_env(tmp_path)
    startup_marker = tmp_path / "bash-startup.executed"
    startup_hook = tmp_path / "startup-hook.sh"
    startup_hook.write_text(
        "printf executed > bash-startup.executed\n",
        encoding="utf-8",
    )
    env["BASH_ENV"] = startup_hook.name
    env["ENV"] = startup_hook.name
    fake_root = tmp_path / "project-selected-git"
    (fake_root / "bin").mkdir(parents=True)
    (fake_root / "usr" / "bin").mkdir(parents=True)
    (fake_root / "bin" / "bash.exe").write_text("not an executable", encoding="utf-8")
    env["GIT_INSTALL_ROOT"] = str(fake_root)

    result = run_launcher(launcher, "collect", cwd=tmp_path, env=env)

    assert result.returncode == 0, result.stderr
    assert result.stdout == "collect:\n"
    assert not startup_marker.exists()


@WINDOWS_ONLY
def test_supports_path_only_portable_git_after_sanitization(tmp_path: Path):
    launcher = copy_launcher_fixture(tmp_path)
    text = launcher.read_text(encoding="utf-8")
    launcher.write_text(
        text.replace(
            "$gitRoot = Find-InstalledGitRoot $targetRoot",
            "$gitRoot = $null",
            1,
        ),
        encoding="utf-8",
    )
    env = clean_windows_env(tmp_path)

    result = run_launcher(launcher, "collect", cwd=tmp_path, env=env)

    assert result.returncode == 0, result.stderr
    assert result.stdout == "collect:\n"


@WINDOWS_ONLY
@pytest.mark.parametrize(("action", "script_name"), ACTION_SCRIPTS.items())
def test_routes_every_health_action_through_git_bash(
    tmp_path: Path, action: str, script_name: str
):
    launcher = copy_launcher_fixture(tmp_path)
    env = clean_windows_env(tmp_path)

    result = run_launcher(
        launcher,
        action,
        "target project",
        "deep",
        cwd=tmp_path,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == f"{action}:target project deep\n"
    assert script_name in LAUNCHER.read_text(encoding="utf-8")
    assert "not found" not in result.stderr.lower()


@WINDOWS_ONLY
def test_real_collector_runs_deep_from_clean_windows_path(tmp_path: Path):
    env = clean_windows_env(tmp_path)
    target = tmp_path / "target project"
    target.mkdir()

    result = run_launcher(
        LAUNCHER,
        "collect",
        "auto",
        "deep",
        cwd=target,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert "=== AI MAINTAINABILITY DETAIL ===" in result.stdout
    assert "=== AGENT CONFIG DETAIL ===\n(unavailable" not in result.stdout
    assert "=== AI MAINTAINABILITY DETAIL ===\n(unavailable" not in result.stdout
    assert "(unavailable: conversation_audit.py or trusted Python missing)" not in result.stdout
    assert "(unavailable: scan_skill_security.py or trusted Python missing)" not in result.stdout
    assert "not found" not in result.stderr.lower()


@WINDOWS_ONLY
def test_broken_app_aliases_do_not_win_python_discovery(tmp_path: Path):
    target = tmp_path / "target project"
    target.mkdir()
    aliases = tmp_path / "broken app aliases"
    aliases.mkdir()
    inert_executable = Path(os.environ["SystemRoot"]) / "System32" / "where.exe"
    shutil.copy2(inert_executable, aliases / "python3.exe")
    shutil.copy2(inert_executable, aliases / "python.exe")
    env = clean_windows_env(tmp_path)
    env["PATH"] = os.pathsep.join([str(aliases), env["PATH"]])

    result = run_launcher(
        LAUNCHER,
        "collect",
        "auto",
        "deep",
        cwd=target,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert "=== AGENT CONFIG DETAIL ===" in result.stdout
    assert "=== AI MAINTAINABILITY DETAIL ===" in result.stdout
    assert "=== AGENT CONFIG DETAIL ===\n(unavailable" not in result.stdout
    assert "=== AI MAINTAINABILITY DETAIL ===\n(unavailable" not in result.stdout


@WINDOWS_ONLY
@pytest.mark.parametrize(
    ("action", "extra_args", "receipt"),
    [
        ("agent-context", ("summary",), "=== AGENT INSTRUCTION SURFACE ==="),
        ("maintainability", ("summary",), "maintainability_status:"),
        ("doc-refs", (), "doc references: ok"),
    ],
)
def test_real_python_backed_actions_run_through_git_bash(
    tmp_path: Path,
    action: str,
    extra_args: tuple[str, ...],
    receipt: str,
):
    target = tmp_path / "target project"
    target.mkdir()
    env = clean_windows_env(tmp_path)

    result = run_launcher(
        LAUNCHER,
        action,
        str(target),
        *extra_args,
        cwd=target,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert receipt in result.stdout, result.stderr


@WINDOWS_ONLY
def test_missing_git_bash_has_one_actionable_diagnostic(tmp_path: Path):
    launcher = copy_launcher_fixture(tmp_path)
    launcher.write_text(
        launcher.read_text(encoding="utf-8").replace(
            "$gitRoot = Find-InstalledGitRoot $targetRoot",
            "$gitRoot = $null",
            1,
        ),
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")

    result = run_launcher(launcher, "collect", cwd=tmp_path, env=env)

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.strip() == (
        "Health requires Git for Windows with bin\\bash.exe "
        "in a standard install or safe PATH."
    )


@WINDOWS_ONLY
def test_broken_standard_git_falls_back_to_portable_path(tmp_path: Path):
    target = tmp_path / "target project"
    target.mkdir()
    broken_root = tmp_path / "broken standard git"
    (broken_root / "bin").mkdir(parents=True)
    (broken_root / "usr" / "bin").mkdir(parents=True)
    (broken_root / "bin" / "bash.exe").write_text(
        "not an executable",
        encoding="utf-8",
    )
    launcher = copy_launcher_fixture(tmp_path)
    powershell_root = str(broken_root).replace("'", "''")
    launcher.write_text(
        launcher.read_text(encoding="utf-8").replace(
            "$gitRoot = Find-InstalledGitRoot $targetRoot",
            f"$gitRoot = '{powershell_root}'",
            1,
        ),
        encoding="utf-8",
    )
    env = clean_windows_env(tmp_path)

    result = run_launcher(launcher, "collect", cwd=target, env=env)

    assert result.returncode == 0, result.stderr
    assert result.stdout == "collect:\n"


@WINDOWS_ONLY
def test_project_local_git_candidate_is_rejected_before_execution(tmp_path: Path):
    target = tmp_path / "target project"
    target.mkdir()
    project_git = target / "project git"
    create_junction(project_git, git_install_root())
    launcher = copy_launcher_fixture(tmp_path)
    (launcher.parent / "collect-data.sh").write_text(
        "printf 'child-path=%s\\n' \"$PATH\"\n",
        encoding="utf-8",
    )
    candidate = str(project_git).replace("'", "''")
    launcher.write_text(
        launcher.read_text(encoding="utf-8").replace(
            "$gitRoot = Find-InstalledGitRoot $targetRoot",
            f"$gitRoot = '{candidate}'",
            1,
        ),
        encoding="utf-8",
    )
    env = clean_windows_env(tmp_path)

    result = run_launcher(launcher, "collect", cwd=target, env=env)

    assert result.returncode == 0, result.stderr
    assert "child-path=" in result.stdout
    assert "project git" not in result.stdout.lower()


@WINDOWS_ONLY
def test_project_local_python_candidate_is_rejected_before_execution(tmp_path: Path):
    target = tmp_path / "target project"
    target.mkdir()
    project_python = target / "project python"
    create_junction(project_python, Path(sys.executable).parent)
    candidate = project_python / Path(sys.executable).name
    launcher = copy_launcher_fixture(tmp_path)
    candidate_text = str(candidate).replace("'", "''")
    launcher.write_text(
        launcher.read_text(encoding="utf-8").replace(
            "$pythonPath = Find-Python $targetRoot",
            (
                f"$pythonPath = Resolve-WorkingPython '{candidate_text}' $targetRoot\n"
                'Write-Output "selected-project-python=$pythonPath"'
            ),
            1,
        ),
        encoding="utf-8",
    )
    env = clean_windows_env(tmp_path)

    result = run_launcher(launcher, "collect", cwd=target, env=env)

    assert result.returncode == 0, result.stderr
    assert "selected-project-python=\n" in result.stdout


@WINDOWS_ONLY
def test_python_wildcard_probes_past_first_broken_match(tmp_path: Path):
    target = tmp_path / "target project"
    target.mkdir()
    python_root = tmp_path / "python candidates"
    bad = python_root / "Python000Bad" / "python.exe"
    bad.parent.mkdir(parents=True)
    git_executable = shutil.which("git")
    assert git_executable
    shutil.copy2(git_executable, bad)
    good = Path(sys.executable)
    launcher = copy_launcher_fixture(tmp_path)
    (launcher.parent / "collect-data.sh").write_text(
        "python.exe -I -c 'print(\"selected-python-runtime-ok\")'\n",
        encoding="utf-8",
    )
    pattern = str(python_root / "Python*" / "python.exe").replace("'", "''")
    good_path = str(good).replace("'", "''")
    text = launcher.read_text(encoding="utf-8")
    python_candidates_anchor = (
        "    $candidates = @()\n"
        "    $userProfile = [Environment]::GetFolderPath("
    )
    assert text.count(python_candidates_anchor) == 1
    assert text.count('foreach ($name in @("python3.exe", "python.exe")) {') == 1
    assert text.count('$launcher = Resolve-Executable "py.exe" $TargetRoot') == 1
    assert text.count("$pythonPath = Find-Python $targetRoot") == 1
    text = text.replace(
        'foreach ($name in @("python3.exe", "python.exe")) {',
        "foreach ($name in @()) {",
        1,
    )
    text = text.replace(
        '$launcher = Resolve-Executable "py.exe" $TargetRoot',
        "$launcher = $null",
        1,
    )
    text = text.replace(
        python_candidates_anchor,
        (
            f"    $candidates = @('{pattern}', '{good_path}')\n"
            "    $userProfile = [Environment]::GetFolderPath("
        ),
        1,
    )
    text = text.replace(
        "$pythonPath = Find-Python $targetRoot",
        "$pythonPath = Find-Python $targetRoot\n"
        'Write-Output "selected-python=$pythonPath"',
        1,
    )
    find_python_body = text.split("function Find-Python([string]$TargetRoot) {", 1)[1].split(
        "$scriptNames = @{",
        1,
    )[0]
    assert pattern in find_python_body
    assert good_path in find_python_body
    assert pattern not in text.split("function Find-Python([string]$TargetRoot) {", 1)[0]
    launcher.write_text(text, encoding="utf-8")
    env = clean_windows_env(tmp_path)

    result = run_launcher(launcher, "collect", cwd=target, env=env)

    assert result.returncode == 0, result.stderr
    selected = next(
        line for line in result.stdout.splitlines() if line.startswith("selected-python=")
    )
    assert str(bad).lower() not in selected.lower()
    assert result.stdout.endswith("selected-python-runtime-ok\n")


def test_skill_routes_windows_commands_through_launcher():
    """Every documented Health action must reach Windows through the launcher.

    The surface is the skill entrypoint plus the reference files it loads, since
    a conditional block moved into references/ still runs on the user's machine.
    Scanning the union keeps the guarantee attached to the command, not to the
    file that happens to carry it.
    """
    surface = [SKILL, *sorted((SKILL.parent / "references").glob("*.md"))]
    texts = {path: path.read_text(encoding="utf-8") for path in surface}
    joined = "\n".join(texts.values())

    for path, text in texts.items():
        assert "pwsh " not in text, f"{path.name} invokes pwsh directly"
        for line in text.splitlines():
            if "/bin/bash " in line:
                assert "BASH_ENV= ENV= /bin/bash -p " in line, (
                    f"{path.name} does not clear Bash startup hooks"
                )
            if ' -File "$HEALTH_LAUNCHER"' in line:
                assert '& "$POWERSHELL"' in line, (
                    f"{path.name} resolves PowerShell through inherited PATH"
                )
                assert "-ExecutionPolicy Bypass -File" in line, (
                    f"{path.name} has a Windows launcher invocation without "
                    "process-scoped execution policy"
                )
    assert "([Environment]::SystemDirectory)" in texts[SKILL]
    assert "\nbash " not in joined
    assert "`bash " not in joined
    assert "<skill-base-dir>/scripts/run-health.ps1" in texts[SKILL]
    assert "<skill-base-dir>/skills/health/scripts/run-health.ps1" in texts[SKILL]
    for action in ACTION_SCRIPTS:
        assert f'"$HEALTH_LAUNCHER" {action}' in joined, f"{action} has no launcher route"
    assert '/bin/bash -p "$HEALTH_SCRIPT"' in texts[SKILL]


def test_launcher_does_not_trust_runtime_selection_environment():
    text = LAUNCHER.read_text(encoding="utf-8")

    assert "$env:GIT_INSTALL_ROOT" not in text
    assert "Resolve-Executable $env:WAZA_PYTHON" not in text
    assert 'StartsWith("\\\\")' in text
    for name in (
        "WAZA_PYTHON",
        "DOC_REF_CHECKER",
        "GIT_INSTALL_ROOT",
        "BASH_ENV",
        "ENV",
    ):
        assert f'Remove-Item "Env:{name}"' in text
    assert 'waza-health-python-ok' in text
    assert "function Resolve-FinalPath" in text
    assert "function Resolve-SafePath" in text
    assert "function ConvertTo-GitBashPath" in text
    assert "& $bashPath -p $bashScriptPath @ScriptArgs" in text
    assert "& $bashPath -p $scriptPath @ScriptArgs" not in text
    assert "function Test-GitBashRoot([string]$Root, [string]$TargetRoot)" in text
    assert "if ($gitRoot -and -not (Test-GitBashRoot $gitRoot $targetRoot))" in text
    assert "function Resolve-WorkingPython([string]$Candidate, [string]$TargetRoot)" in text
    assert "Resolve-Executable $Candidate $TargetRoot" in text
    assert "$env:PATH.Split([IO.Path]::PathSeparator)" in text
    assert "$matches = @(" in text
    assert "foreach ($match in $matches)" in text


def test_health_shell_scripts_are_pinned_to_lf():
    result = subprocess.run(
        ["git", "check-attr", "eol", "--", "skills/health/scripts/collect-data.sh"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    )

    assert result.stdout.rstrip().endswith("eol: lf")
    assert "*.sh text eol=lf" in GITATTRIBUTES.read_text(encoding="utf-8")
