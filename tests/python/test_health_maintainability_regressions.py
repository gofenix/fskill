import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "health" / "scripts" / "check_maintainability.py"
SPEC = importlib.util.spec_from_file_location("health_maintainability_regressions", SCRIPT)
maint = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = maint
SPEC.loader.exec_module(maint)


def test_command_labels_redact_credentials_without_hiding_status_fields():
    label = (
        "workflow.yml: PROVIDER_API_KEY=provider-namespaced-value "
        '\"DATABASE_PASSWORD\": \"database-json-value\" '
        "CLOUD_SECRET_ACCESS_KEY='cloud-namespaced-value' "
        "SSH_PRIVATE_KEY=ssh-private-value "
        "--token=maintainability-flag-value "
        "token_count=42 api_key_status=missing secret_scan_status=ok "
        "foo-token_count=7 "
        "password_hash=sha256 notsecret=value secretary=value "
        "CLOUD_ACCESS_KEY_ID=identifier"
    )

    redacted = maint.redact_command_label(label)

    for leaked in (
        "provider-namespaced-value",
        "database-json-value",
        "cloud-namespaced-value",
        "ssh-private-value",
        "maintainability-flag-value",
    ):
        assert leaked not in redacted
    assert "PROVIDER_API_KEY=[REDACTED]" in redacted
    assert '\"DATABASE_PASSWORD\": [REDACTED]' in redacted
    assert "CLOUD_SECRET_ACCESS_KEY=[REDACTED]" in redacted
    assert "SSH_PRIVATE_KEY=[REDACTED]" in redacted
    assert "--token=[REDACTED]" in redacted
    assert "token_count=42 api_key_status=missing secret_scan_status=ok" in redacted
    assert "foo-token_count=7" in redacted
    assert "password_hash=sha256 notsecret=value secretary=value" in redacted
    assert "CLOUD_ACCESS_KEY_ID=identifier" in redacted


def test_markdown_links_ignore_fenced_and_inline_code(tmp_path: Path):
    readme = tmp_path / "README.md"
    readme.write_text(
        "```markdown\n"
        "[Template]({{URL}})\n"
        "```\n"
        "Example: `[Overview](generated/overview.md)`\n"
        "Real: [Missing](missing.md)\n",
        encoding="utf-8",
    )

    assert maint.scan_markdown_links([readme], tmp_path) == [
        "README.md:5 -> missing.md"
    ]


def test_explanatory_command_examples_are_not_missing_targets(tmp_path: Path):
    agents = tmp_path / "AGENTS.md"
    agents.write_text(
        "Shell history may contribute command examples (`brew install`, "
        "`make verify`, `phased.sh`).\n"
        "Run `make test` before handoff.\n",
        encoding="utf-8",
    )
    (tmp_path / "Makefile").write_text("test:\n\t@test -s AGENTS.md\n", encoding="utf-8")

    *_, missing, _make_targets, _package_scripts = maint.verification_surface(
        tmp_path, [agents], [agents, tmp_path / "Makefile"]
    )

    assert missing == []


def test_actionable_missing_command_remains_a_finding(tmp_path: Path):
    agents = tmp_path / "AGENTS.md"
    agents.write_text("Run `make verify` before handoff.\n", encoding="utf-8")
    (tmp_path / "Makefile").write_text("test:\n\t@test -s AGENTS.md\n", encoding="utf-8")

    *_, missing, _make_targets, _package_scripts = maint.verification_surface(
        tmp_path, [agents], [agents, tmp_path / "Makefile"]
    )

    assert missing == ["AGENTS.md references missing make target: verify"]


def test_rustdoc_generated_links_are_not_local_markdown_debt(tmp_path: Path):
    crate = tmp_path / "term"
    crate.mkdir()
    (crate / "Cargo.toml").write_text("[package]\nname = 'term'\n", encoding="utf-8")
    readme = crate / "README.md"
    readme.write_text(
        "[Terminal](terminal/struct.Terminal.html)\n"
        "[Guide](guide.html)\n",
        encoding="utf-8",
    )

    assert maint.scan_markdown_links([readme], tmp_path) == [
        "term/README.md:2 -> guide.html"
    ]


def test_swift_package_has_native_verifier_surface(tmp_path: Path):
    package = tmp_path / "Package.swift"
    package.write_text("// swift-tools-version: 6.0\n", encoding="utf-8")
    test = tmp_path / "Tests" / "DemoTests.swift"
    test.parent.mkdir()
    test.write_text("import Testing\n", encoding="utf-8")

    commands, evidence, *_ = maint.verification_surface(
        tmp_path, [], [package, test]
    )

    assert "swift test" in commands
    assert "swift test" in evidence


@pytest.mark.parametrize("default", ["check", "test", "verify"])
def test_package_default_avoids_make_wrapper_warning(tmp_path: Path, default: str):
    (tmp_path / "Makefile").write_text("build:\n\t@test -s package.json\n")
    (tmp_path / "package.json").write_text(json.dumps({"scripts": {
        default: "npm run lint && npm run typecheck",
        "lint": "eslint .",
        "typecheck": "tsc --noEmit",
    }}))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path)], capture_output=True, text=True,
        check=True,
    )
    assert f"npm run {default}" in result.stdout
    assert "wrapper_status: PASS" in result.stdout


def test_hollow_package_default_does_not_clear_wrapper_gap(tmp_path: Path):
    (tmp_path / "Makefile").write_text("build:\n\t@test -s package.json\n")
    (tmp_path / "package.json").write_text(json.dumps({"scripts": {
        "check": "echo passed", "lint": "eslint .",
    }}))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path)], capture_output=True, text=True,
        check=True,
    )
    assert "wrapper_status: WARN" in result.stdout
    assert "hollow_verifiers:" in result.stdout
