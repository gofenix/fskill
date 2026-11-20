"""Unit tests for skills/check/scripts/incident_ledger.py.

Each check gets a fixture that passes and one that fails on exactly that
check, so a broken matcher cannot pass by matching nothing.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "skills" / "check" / "scripts" / "incident_ledger.py"

spec = importlib.util.spec_from_file_location("waza_incident_ledger", SCRIPT)
ledger_mod = importlib.util.module_from_spec(spec)
sys.modules["waza_incident_ledger"] = ledger_mod
spec.loader.exec_module(ledger_mod)

HEADER = "| ID | Reported | Symptom | Introduced | Fixed | Layer | Caught by |\n|---|---|---|---|---|---|---|\n"


def git(repo: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=waza", "-c", "user.email=waza@test", *args],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def make_repo(tmp_path: Path, files: dict[str, str]) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    for rel, body in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, "utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "fix")
    return repo, git(repo, "rev-parse", "--short=8", "HEAD")


def write_ledger(repo: Path, rows: str, preamble: str = "") -> None:
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "incidents.md").write_text(
        f"# Incidents\n\n{preamble}\n## Incidents\n\n{HEADER}{rows}", "utf-8"
    )


def run(repo: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *extra],
        capture_output=True, text=True,
    )


TEST_FILES = {
    "tests/test_parser.py": "def test_parses_empty_input():\n    pass\n",
    "spec/cli.bats": '@test "rejects a missing flag" {\n  true\n}\n',
    "src/app.py": "def helper_only_in_source():\n    pass\n",
    "scripts/gate.sh": "exit 0\n",
}


def test_valid_ledger_passes_with_identifier_title_and_path_catchers(tmp_path):
    repo, sha = make_repo(tmp_path, TEST_FILES)
    write_ledger(
        repo,
        f"| I-01 | 2026-01-02 | Crash on empty input | unknown | {sha} | unit | `test_parses_empty_input`, `rejects a missing flag`, `scripts/gate.sh` |\n",
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 rows, 0 problems" in result.stderr


@pytest.mark.parametrize(
    "row, expected",
    [
        ("| I-01 | 2026-01-02 | s | unknown | {sha} | unit | `test_missing_everywhere` |", "catcher `test_missing_everywhere`"),
        ("| I-01 | 2026-01-02 | s | unknown | {sha} | unit | `helper_only_in_source` |", "catcher `helper_only_in_source`"),
        ("| I-01 | 2026-01-02 | s | unknown | {sha} | unit | no backticks |", "no catcher named"),
        ("| I-01 | 2026-01-02 | s | unknown | deadbeef | unit | `test_parses_empty_input` |", "Fixed deadbeef does not resolve"),
        ("| I-01 | 2026-01-02 | s | someone | {sha} | unit | `test_parses_empty_input` |", "Introduced is not a commit"),
        ("| I-01 | 2026-01-02 | s | unknown | {sha} | luck | `test_parses_empty_input` |", "layer luck is not one of"),
        ("| I-01 | yesterday | s | unknown | {sha} | unit | `test_parses_empty_input` |", "Reported is not a date"),
        ("| I-01 | 2026-01-02 | s | unknown | {sha} | unit |", "expected 7 cells"),
    ],
)
def test_each_check_fails_on_its_own_defect(tmp_path, row, expected):
    repo, sha = make_repo(tmp_path, TEST_FILES)
    write_ledger(repo, row.format(sha=sha) + "\n")
    result = run(repo)
    assert result.returncode == 1
    assert expected in result.stdout


def test_duplicate_id_fails(tmp_path):
    repo, sha = make_repo(tmp_path, TEST_FILES)
    row = f"| I-01 | 2026-01-02 | s | unknown | {sha} | unit | `test_parses_empty_input` |\n"
    write_ledger(repo, row + row)
    result = run(repo)
    assert result.returncode == 1
    assert "I-01 repeats" in result.stdout


def test_layers_come_from_the_declaration_comment_not_prose(tmp_path):
    repo, sha = make_repo(tmp_path, TEST_FILES)
    preamble = "Layers, earliest first: `write-time` then `vm`.\n<!-- layers: write-time, vm -->\n"
    write_ledger(repo, f"| I-01 | 2026-01-02 | s | unknown | {sha} | vm | `test_parses_empty_input` |\n", preamble)
    assert run(repo).returncode == 0
    write_ledger(repo, f"| I-01 | 2026-01-02 | s | unknown | {sha} | unit | `test_parses_empty_input` |\n", preamble)
    result = run(repo)
    assert result.returncode == 1
    assert "layer unit is not one of write-time, vm" in result.stdout


def test_layers_flag_overrides_declaration(tmp_path):
    repo, sha = make_repo(tmp_path, TEST_FILES)
    write_ledger(repo, f"| I-01 | 2026-01-02 | s | unknown | {sha} | native | `test_parses_empty_input` |\n")
    assert run(repo).returncode == 1
    assert run(repo, "--layers", "unit,native").returncode == 0


def test_shallow_clone_shape_checks_commits_and_says_so(tmp_path):
    repo, sha = make_repo(tmp_path, TEST_FILES)
    write_ledger(repo, f"| I-01 | 2026-01-02 | s | unknown | 1234567 | unit | `test_parses_empty_input` |\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "ledger")
    git(repo, "commit", "-q", "--allow-empty", "-m", "later")
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{repo}", str(clone)], check=True)
    result = run(clone)
    assert result.returncode == 0, result.stdout
    assert "shallow clone" in result.stderr
    assert run(repo).returncode == 1


def test_missing_ledger_is_a_usage_error(tmp_path):
    repo, _ = make_repo(tmp_path, TEST_FILES)
    result = run(repo)
    assert result.returncode == 2
    assert "not found" in result.stderr


def test_plan_names_the_pre_fix_revision_and_touched_files(tmp_path):
    repo, sha = make_repo(tmp_path, TEST_FILES)
    write_ledger(repo, f"| I-01 | 2026-01-02 | s | unknown | {sha} | unit | `test_parses_empty_input` |\n")
    result = run(repo, "--plan")
    assert result.returncode == 0
    assert f"I-01: review {sha}^ files:" in result.stdout
    assert "src/app.py" in result.stdout


@pytest.mark.parametrize(
    "path, expected",
    [
        ("tests/unit/foo.py", True),
        ("src/Foo.Tests/BarTests.cs", True),
        ("pkg/thing_test.go", True),
        ("web/button.spec.ts", True),
        ("test_cli.py", True),
        ("src/app.py", False),
        ("node_modules/x/test/y.js", False),
    ],
)
def test_test_file_detection(path, expected):
    assert ledger_mod.is_test_file(path) is expected

@pytest.mark.parametrize("body,catcher", [
    ('# def test_ghost():\npass\n', 'test_ghost'),
    ('"""def test_ghost():\n    pass\n"""\n', 'test_ghost'),
    ('test_ghost()\n', 'test_ghost'),
    ('const title = "missing flag";\n', 'missing flag'),
    ('// function test_ghost() {}\n', 'test_ghost'),
])
def test_mentions_are_not_definitions(tmp_path, body, catcher):
    ext = 'js' if body.startswith(('const', '//')) else 'py'
    repo, sha = make_repo(tmp_path, {f'tests/test_fake.{ext}': body})
    write_ledger(repo, f'| I-01 | 2026-01-02 | s | unknown | {sha} | unit | `{catcher}` |\n')
    assert run(repo).returncode == 1


def test_deleted_gate_is_not_a_catcher(tmp_path):
    repo, sha = make_repo(tmp_path, TEST_FILES)
    (repo / 'scripts/gate.sh').unlink()
    write_ledger(repo, f'| I-01 | 2026-01-02 | s | unknown | {sha} | unit | `scripts/gate.sh` |\n')
    assert run(repo).returncode == 1


def test_untracked_test_is_current_workspace_evidence(tmp_path):
    repo, sha = make_repo(tmp_path, TEST_FILES)
    (repo / 'tests/test_new.py').write_text('def test_new():\n    pass\n')
    write_ledger(repo, f'| I-01 | 2026-01-02 | s | unknown | {sha} | unit | `test_new` |\n')
    assert run(repo).returncode == 0


def test_escaped_parent_symlink_is_not_evidence(tmp_path):
    repo, sha = make_repo(tmp_path, TEST_FILES)
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'test_escape.py').write_text('def test_escape():\n    pass\n')
    (repo / 'tests/escape').symlink_to(outside, target_is_directory=True)
    git(repo, 'add', 'tests/escape')
    write_ledger(repo, f'| I-01 | 2026-01-02 | s | unknown | {sha} | unit | `tests/escape/test_escape.py` |\n')
    assert run(repo).returncode == 1


@pytest.mark.parametrize('path,body,catcher', [
    ('tests/test_async.py', 'async def test_async():\n    pass\n', 'test_async'),
    ('tests/test_js.js', 'it("rejects a missing flag", () => {});\n', 'rejects a missing flag'),
    ('tests/test_js.ts', 'function test_named() {}\n', 'test_named'),
    ('tests/test_js.ts', 'const test_arrow = () => {};\n', 'test_arrow'),
    ('tests/test_shell.sh', 'test_shell() {\n true\n}\n', 'test_shell'),
])
def test_supported_declarations(tmp_path, path, body, catcher):
    repo, sha = make_repo(tmp_path, {path: body})
    write_ledger(repo, f'| I-01 | 2026-01-02 | s | unknown | {sha} | unit | `{catcher}` |\n')
    result = run(repo)
    assert result.returncode == 0, result.stdout

@pytest.mark.parametrize('path,body,catcher', [
    ('tests/test_js.js', '/*\nit("fake title", () => {});\n*/\n', 'fake title'),
    ('tests/test_js.js', 'const text = `\nfunction test_fake() {}\n`;\n', 'test_fake'),
    ('tests/test_shell.sh', '# test_fake() {\ntrue\n', 'test_fake'),
    ('tests/test_shell.sh', 'cat <<EOF\ntest_fake() { true; }\nEOF\n', 'test_fake'),
    ('tests/other.rs', '// fn test_fake() {}\n', 'test_fake'),
    ('tests/test_shell.sh', "'test_fake() {'\n", 'test_fake'),
    ('tests/test_shell.sh', '"test_fake"() { true; }\n', 'test_fake'),
    ('tests/test_js.js', 'test.skip("fake title", () => {});\n', 'fake title'),
    ('tests/test_js.js', 'test.todo("fake title", () => {});\n', 'fake title'),
])
def test_other_language_data_is_not_a_definition(tmp_path, path, body, catcher):
    repo, sha = make_repo(tmp_path, {path: body})
    write_ledger(repo, f'| I-01 | 2026-01-02 | s | unknown | {sha} | unit | `{catcher}` |\n')
    assert run(repo).returncode == 1
    write_ledger(repo, f'| I-01 | 2026-01-02 | s | unknown | {sha} | unit | `{path}` |\n')
    assert run(repo).returncode == 0


def test_gate_symlink_outside_root_is_rejected(tmp_path):
    repo, sha = make_repo(tmp_path, TEST_FILES)
    outside = tmp_path / 'gate.sh'
    outside.write_text('exit 0\n')
    (repo / 'scripts/escape.sh').symlink_to(outside)
    git(repo, 'add', 'scripts/escape.sh')
    write_ledger(repo, f'| I-01 | 2026-01-02 | s | unknown | {sha} | unit | `scripts/escape.sh` |\n')
    assert run(repo).returncode == 1
