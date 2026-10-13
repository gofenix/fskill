import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "health" / "scripts" / "conversation_audit.py"


def record(role: str, content: object) -> str:
    return json.dumps(
        {"type": role, "message": {"role": role, "content": content}},
        ensure_ascii=False,
    )


def write_session(path: Path, lines: list[str], mtime: int) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.utime(path, (mtime, mtime))


def run_audit(
    directory: Path,
    mode: str,
    codex_root: Path | None = None,
    project_root: Path | None = None,
    all_projects: bool = False,
) -> str:
    command = [sys.executable, "-I", str(SCRIPT), str(directory), mode]
    if codex_root is not None and project_root is not None:
        command.extend(
            ["--codex-root", str(codex_root), "--project-root", str(project_root)]
        )
    if all_projects:
        assert codex_root is not None
        command.extend(["--codex-root", str(codex_root), "--all-projects"])
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def build_scope_fixture(tmp_path: Path) -> Path:
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(
        sessions / "live.jsonl",
        [record("user", "继续"), record("assistant", "live-only-secret sk-live0123456789")],
        int(time.time()),
    )
    write_session(
        sessions / "recent-1.jsonl",
        [record("user", "继续")],
        400,
    )
    write_session(
        sessions / "recent-2.jsonl",
        [record("user", "都提交了吗")],
        300,
    )
    write_session(
        sessions / "recent-3.jsonl",
        [
            record(
                "assistant",
                [
                    {"type": "tool_use", "name": "Bash", "id": "tool-1", "input": {}},
                    {"type": "text", "text": "ran verifier"},
                ],
            ),
            record(
                "user",
                [
                    {"type": "tool_result", "tool_use_id": "tool-1", "content": "ok"},
                    {"type": "text", "text": "还是不对, contact owner@example.com"},
                ],
            ),
        ],
        200,
    )
    write_session(
        sessions / "old.jsonl",
        [
            record("assistant", "x" * 600_000),
            record("user", "肯定不是这个, see https://example.com and sk-old0123456789"),
        ],
        100,
    )
    return sessions


def test_deep_streams_all_previous_files_and_reports_coverage(tmp_path: Path):
    sessions = build_scope_fixture(tmp_path)

    output = run_audit(sessions, "deep")

    assert "files_discovered: 5" in output
    assert "previous_files_available: 4" in output
    assert "signal_scope: all_previous" in output
    assert "signal_files_scanned: 4" in output
    assert "previous_bytes_scanned_percent: 100.0" in output
    assert "all_previous_files_scanned: yes" in output
    assert "PERSISTENCE SIGNAL:" in output
    assert "DELIVERY REMINDER:" in output
    assert "USER CORRECTION:" in output
    assert "肯定不是这个" in output
    assert "tool_calls_seen: 1" in output
    assert "tool_results_seen: 1" in output
    assert "tool_call_names: Bash=1" in output
    assert "owner@example.com" not in output
    assert "https://example.com" not in output
    assert "sk-old0123456789" not in output
    assert "live-only-secret" not in output
    assert "=== SIGNAL THEME SUMMARY ===" in output
    assert "unfinished_persistence: 1" in output
    assert "authorization_delivery: 1" in output


def test_summary_scans_three_previous_files_without_claiming_full_history(tmp_path: Path):
    sessions = build_scope_fixture(tmp_path)

    output = run_audit(sessions, "summary")

    assert "signal_scope: recent_previous" in output
    assert "signal_files_scanned: 3" in output
    assert "all_previous_files_scanned: no" in output
    assert "肯定不是这个" not in output
    assert "skipped: summary mode" in output


def test_project_scope_excludes_every_recent_file_per_runtime(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    now = int(time.time())
    write_session(
        sessions / "active-one.jsonl",
        [record("user", "active-one-must-not-leak")],
        now,
    )
    write_session(
        sessions / "active-two.jsonl",
        [record("user", "active-two-must-not-leak")],
        now - 1,
    )
    write_session(
        sessions / "previous.jsonl",
        [record("assistant", "我来处理"), record("user", "还是不对")],
        now - 600,
    )

    output = run_audit(sessions, "deep")

    assert "live_files_skipped: 2" in output
    assert "previous_files_available: 1" in output
    assert "signal_files_scanned: 1" in output
    assert "active-one-must-not-leak" not in output
    assert "active-two-must-not-leak" not in output
    assert "USER CORRECTION:" in output


def test_stale_newest_file_is_scanned_in_current_project_mode(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(
        sessions / "stale-newest.jsonl",
        [record("assistant", "initial answer"), record("user", "还是不对")],
        100,
    )

    output = run_audit(sessions, "deep")

    assert "live_files_skipped: 0" in output
    assert "previous_files_available: 1" in output
    assert "signal_files_scanned: 1" in output
    assert "all_previous_files_scanned: yes" in output
    assert "USER CORRECTION:" in output


def test_deep_extract_samples_filtered_message_head_and_tail(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(sessions / "live.jsonl", [record("user", "live")], int(time.time()))
    messages = [record("user", f"message-{index:03d}") for index in range(200)]
    write_session(sessions / "previous.jsonl", messages, 100)

    output = run_audit(sessions, "deep")

    assert "messages=200 extract_truncated=yes" in output
    assert "message-000" in output
    assert "message-029" in output
    assert "message-050" not in output
    assert "message-080" in output
    assert "message-199" in output


def test_malformed_records_are_counted_without_hiding_valid_signals(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(sessions / "live.jsonl", [record("user", "live")], int(time.time()))
    write_session(
        sessions / "previous.jsonl",
        ["{not-json", record("assistant", "我已经修了"), record("user", "还是有问题")],
        100,
    )

    output = run_audit(sessions, "deep")

    assert "parse_errors: 1" in output
    assert "USER CORRECTION:" in output
    assert "coverage_status: incomplete" in output
    assert "all_previous_files_scanned: no" in output


def test_emitted_signals_and_extracts_redact_credentials_and_windows_paths(
    tmp_path: Path,
):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(sessions / "live.jsonl", [record("user", "live")], int(time.time()))
    fake_slack_token = f"xox{'b'}-1234567890-abcdefghijklmnop"
    sensitive = (
        "还是有问题 github_pat_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456 "
        f"{fake_slack_token} "
        "Authorization: Bearer supersecrettokenvalue "
        "password=hunter2 C:\\Users\\name\\project\\secret.txt "
        "\\\\server\\share\\private.txt ~/private/config "
        "/Volumes/Backup/private.txt "
        "PROVIDER_API_KEY=provider-namespaced-value "
        "\"DATABASE_PASSWORD\": \"database-json-value\" "
        "CLOUD_SECRET_ACCESS_KEY='cloud-namespaced-value' "
        "SSH_PRIVATE_KEY=ssh-private-value "
        "--password=conversation-flag-value "
        "\"SERVICE_API_KEY\": \"escaped-head\\\"escaped-tail\" "
        "token_count=42 api_key_status=missing secret_scan_status=ok "
        "secret=\"QUOTED-SECRET-HEAD QUOTED-SECRET-TAIL\\\n"
        "-----BEGIN OPENSSH PRIVATE KEY-----\n"
        "openssh-private-material\n"
        "-----END OPENSSH PRIVATE KEY-----\n"
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "pem-private-material\n"
        "-----END RSA PRIVATE KEY-----"
    )
    write_session(sessions / "previous.jsonl", [record("user", sensitive)], 100)

    output = run_audit(sessions, "deep")

    for leaked in (
        "github_pat_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456",
        fake_slack_token,
        "supersecrettokenvalue",
        "hunter2",
        "provider-namespaced-value",
        "database-json-value",
        "cloud-namespaced-value",
        "ssh-private-value",
        "conversation-flag-value",
        "escaped-head",
        "escaped-tail",
        "QUOTED-SECRET-HEAD",
        "QUOTED-SECRET-TAIL",
        "C:\\Users\\name\\project\\secret.txt",
        "\\\\server\\share\\private.txt",
        "~/private/config",
        "/Volumes/Backup/private.txt",
        "BEGIN OPENSSH PRIVATE KEY",
        "openssh-private-material",
        "BEGIN RSA PRIVATE KEY",
        "pem-private-material",
    ):
        assert leaked not in output
    assert "Authorization: <secret>" in output
    assert "password=<secret>" in output
    assert "PROVIDER_API_KEY=<secret>" in output
    assert '"DATABASE_PASSWORD": <secret>' in output
    assert "CLOUD_SECRET_ACCESS_KEY=<secret>" in output
    assert "SSH_PRIVATE_KEY=<secret>" in output
    assert "--password=<secret>" in output
    assert '"SERVICE_API_KEY": <secret>' in output
    assert "token_count=42 api_key_status=missing secret_scan_status=ok" in output
    assert "<path>" in output
    assert "<private-key>" in output


def test_correction_classifier_rejects_release_note_and_injected_text(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(sessions / "live.jsonl", [record("user", "live")], int(time.time()))
    write_session(
        sessions / "previous.jsonl",
        [
            record("assistant", "我先给出一版"),
            record("user", "shows a clear error instead of exiting silently"),
            record("user", "<task-notification>不要再做了</task-notification>"),
            record("user", "少一点破折号，内容短一点，简单清晰"),
        ],
        100,
    )

    output = run_audit(sessions, "deep")

    assert "USER CORRECTION:" in output
    assert "少一点破折号" in output
    assert not any(
        line.startswith("USER CORRECTION:") and "instead of exiting silently" in line
        for line in output.splitlines()
    )
    assert "task-notification" not in output


def test_user_correction_requires_an_earlier_assistant_reply_in_same_session(
    tmp_path: Path,
):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(
        sessions / "live.jsonl",
        [record("user", "live")],
        int(time.time()),
    )
    write_session(
        sessions / "previous.jsonl",
        [
            record("user", "不要过度设计"),
            record("assistant", "understood"),
            record("user", "还是不对，不要再加配置"),
        ],
        100,
    )

    output = run_audit(sessions, "deep")
    corrections = [
        line for line in output.splitlines() if line.startswith("USER CORRECTION:")
    ]

    assert len(corrections) == 1
    assert "还是不对" in corrections[0]
    assert "不要过度设计" not in corrections[0]


def test_unstructured_assistant_error_text_is_not_a_platform_event(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(sessions / "live.jsonl", [record("user", "live")], int(time.time()))
    write_session(
        sessions / "previous.jsonl",
        [record("assistant", "API Error: response failed"), record("user", "继续")],
        100,
    )

    output = run_audit(sessions, "deep")

    assert "PLATFORM INTERRUPTION:" not in output
    assert "PLATFORM CONTINUATION:" not in output
    assert "PERSISTENCE SIGNAL:" in output


def test_system_error_text_remains_a_platform_event(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(sessions / "live.jsonl", [record("user", "live")], int(time.time()))
    write_session(
        sessions / "system-error.jsonl",
        [record("system", "API Error: response failed"), record("user", "继续")],
        100,
    )

    output = run_audit(sessions, mode="deep")

    assert "PLATFORM INTERRUPTION:" in output
    assert "PLATFORM CONTINUATION:" in output


def test_structured_codex_interruptions_are_not_agent_persistence(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(
        sessions / "live.jsonl",
        [record("user", "live")],
        int(time.time()),
    )
    write_session(
        sessions / "aborted.jsonl",
        [
            codex_record(
                "event_msg",
                {
                    "type": "turn_aborted",
                    "reason": "interrupted",
                    "turn_id": "turn-1",
                },
            ),
            codex_record(
                "response_item",
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "继续"}],
                },
            ),
        ],
        200,
    )
    write_session(
        sessions / "error.jsonl",
        [
            codex_record(
                "event_msg",
                {"type": "error", "message": "stream disconnected"},
            ),
            record("user", "continue"),
        ],
        100,
    )

    output = run_audit(sessions, "deep")

    assert output.count("PLATFORM INTERRUPTION:") == 2
    assert output.count("PLATFORM CONTINUATION:") == 2
    assert "PERSISTENCE SIGNAL:" not in output


def test_nearby_cross_file_clones_count_as_one_independent_signal(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(sessions / "live.jsonl", [record("user", "live")], int(time.time()))
    cloned_turn = [
        record("user", "please inspect the current state"),
        record("assistant", "I found the relevant path"),
        record("user", "please keep the change narrow"),
        record("assistant", "understood"),
        record("user", "还是不对，请不要增加配置"),
    ]
    write_session(sessions / "clone-a.jsonl", cloned_turn, 200)
    write_session(sessions / "clone-b.jsonl", cloned_turn, 100)

    output = run_audit(sessions, "deep")

    assert "raw_signals_found: 2" in output
    assert "independent_signals: 1" in output
    assert "duplicate_signals_collapsed: 1" in output
    assert output.count("USER CORRECTION:") == 1


def test_same_short_correction_in_independent_files_is_preserved(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(sessions / "live.jsonl", [record("user", "live")], int(time.time()))
    repeated_turn = [
        record("assistant", "understood"),
        record("user", "还是不对，请不要增加配置"),
    ]
    write_session(sessions / "task-a.jsonl", repeated_turn, 200)
    write_session(sessions / "task-b.jsonl", repeated_turn, 100)

    output = run_audit(sessions, "deep")

    assert "raw_signals_found: 2" in output
    assert "independent_signals: 2" in output
    assert "duplicate_signals_collapsed: 0" in output
    assert output.count("USER CORRECTION:") == 2


def test_unrequested_japanese_assistant_text_is_a_language_signal(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(sessions / "live.jsonl", [record("user", "live")], int(time.time()))
    write_session(
        sessions / "previous.jsonl",
        [record("user", "帮我看看"), record("assistant", "これ実機で確認します。")],
        100,
    )

    output = run_audit(sessions, "deep")

    assert "LANGUAGE SIGNAL assistant=ja:" in output
    assert "これ実機で確認します" in output


def test_multilingual_review_does_not_authorize_a_japanese_reply(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(sessions / "live.jsonl", [record("user", "live")], int(time.time()))
    write_session(
        sessions / "examples.jsonl",
        [
            record("user", "帮我检查九种语言的文案"),
            record("assistant", "中文说明里引用 Mac 2台、CLIは，不代表回复切成日语。"),
            record("assistant", "日本語の出力です。確認してください。"),
        ],
        200,
    )
    write_session(
        sessions / "chinese.jsonl",
        [
            record("user", "帮我看看"),
            record("assistant", "中文说明只引用 Mac 2台 和 CLIは 两个片段。"),
        ],
        100,
    )

    output = run_audit(sessions, "deep")

    assert "LANGUAGE SIGNAL assistant=ja:" in output
    assert "日本語の出力です" in output


def test_explicit_japanese_reply_request_allows_japanese_output(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(
        sessions / "live.jsonl",
        [record("user", "live")],
        int(time.time()),
    )
    write_session(
        sessions / "previous.jsonl",
        [
            record("user", "请用日语回复"),
            record("assistant", "日本語で回答します。ご確認ください。"),
        ],
        100,
    )

    output = run_audit(sessions, "deep")

    assert "LANGUAGE SIGNAL assistant=ja:" not in output


def codex_record(record_type: str, payload: dict[str, object]) -> str:
    return json.dumps({"type": record_type, "payload": payload}, ensure_ascii=False)


def test_deep_scans_project_scoped_codex_history_with_runtime_receipt(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    claude = tmp_path / "claude"
    claude.mkdir()
    now = int(time.time())
    write_session(claude / "live.jsonl", [record("user", "live")], now)
    write_session(
        claude / "previous.jsonl",
        [record("assistant", "我已处理"), record("user", "还是不对")],
        100,
    )

    codex = tmp_path / "codex" / "2026" / "08" / "01"
    codex.mkdir(parents=True)
    session_meta = codex_record(
        "session_meta",
        {"cwd": str(project), "id": "session"},
    )
    write_session(
        codex / "live.jsonl",
        [
            session_meta,
            codex_record(
                "response_item",
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "live"}],
                },
            ),
        ],
        now,
    )
    write_session(
        codex / "previous.jsonl",
        [
            session_meta,
            codex_record(
                "response_item",
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "都提交了吗"}],
                },
            ),
            codex_record(
                "response_item",
                {"type": "custom_tool_call", "name": "exec_command"},
            ),
            codex_record(
                "response_item",
                {"type": "custom_tool_call_output", "output": "ok"},
            ),
        ],
        200,
    )
    write_session(
        codex / "other-project.jsonl",
        [
            codex_record("session_meta", {"cwd": str(tmp_path / "other")}),
            codex_record(
                "response_item",
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "不要再泄漏这个"}],
                },
            ),
        ],
        300,
    )

    output = run_audit(claude, "deep", codex.parent.parent.parent, project)

    assert "conversation_runtime: claude_project_logs,codex_project_logs" in output
    assert "coverage_status: live_sessions_excluded" in output
    assert "cross_runtime_full_history: no" in output
    assert "runtime_coverage: runtime=claude_project_logs files=2 previous=1" in output
    assert "runtime_coverage: runtime=codex_project_logs files=2 previous=1" in output
    assert "DELIVERY REMINDER: runtime=codex_project_logs" in output
    assert "tool_call_names: exec_command=1" in output
    assert "other-project.jsonl" not in output
    assert "不要再泄漏这个" not in output


def test_stale_newest_files_from_both_runtimes_are_scanned(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    claude = tmp_path / "claude"
    claude.mkdir()
    write_session(
        claude / "stale.jsonl",
        [record("assistant", "initial"), record("user", "还是不对")],
        200,
    )
    codex = tmp_path / "codex" / "2026" / "08" / "01"
    codex.mkdir(parents=True)
    write_session(
        codex / "stale.jsonl",
        [
            codex_record("session_meta", {"cwd": str(project)}),
            codex_record(
                "response_item",
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "都提交了吗"}],
                },
            ),
        ],
        100,
    )

    output = run_audit(claude, "deep", codex.parent.parent.parent, project)

    assert "live_files_skipped: 0" in output
    assert "signal_files_scanned: 2" in output
    assert "cross_runtime_full_history: yes" in output
    assert "USER CORRECTION: runtime=claude_project_logs" in output
    assert "DELIVERY REMINDER: runtime=codex_project_logs" in output


def test_codex_session_in_project_subdirectory_is_in_scope(tmp_path: Path):
    project = tmp_path / "project"
    subdirectory = project / "skills" / "health"
    subdirectory.mkdir(parents=True)
    claude = tmp_path / "claude"
    claude.mkdir()
    now = int(time.time())
    write_session(claude / "live.jsonl", [record("user", "live")], now)
    write_session(claude / "previous.jsonl", [record("user", "继续")], 100)

    codex = tmp_path / "codex" / "2026" / "08" / "01"
    codex.mkdir(parents=True)
    write_session(
        codex / "live.jsonl",
        [codex_record("session_meta", {"cwd": str(project)})],
        now,
    )
    write_session(
        codex / "subdirectory.jsonl",
        [
            codex_record("session_meta", {"cwd": str(subdirectory)}),
            codex_record(
                "response_item",
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "都提交了吗"}],
                },
            ),
        ],
        300,
    )
    write_session(
        codex / "sibling.jsonl",
        [
            codex_record("session_meta", {"cwd": str(tmp_path / "project-copy")}),
            codex_record(
                "response_item",
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "不要再泄漏这个"}],
                },
            ),
        ],
        200,
    )

    output = run_audit(claude, "deep", codex.parent.parent.parent, project)

    assert "DELIVERY REMINDER: runtime=codex_project_logs" in output
    assert "subdirectory.jsonl" in output
    assert "sibling.jsonl" not in output
    assert "不要再泄漏这个" not in output


def test_explicit_all_projects_scans_nested_claude_and_codex_histories(tmp_path: Path):
    claude_root = tmp_path / "claude-projects"
    claude_one = claude_root / "project-one"
    claude_two = claude_root / "project-two"
    claude_one.mkdir(parents=True)
    claude_two.mkdir(parents=True)
    write_session(claude_one / "one.jsonl", [record("user", "还是不对")], 100)
    write_session(claude_two / "two.jsonl", [record("user", "都提交了吗")], 200)
    write_session(claude_two / "live.jsonl", [record("user", "live")], 500)

    codex_root = tmp_path / "codex-sessions" / "2026" / "08" / "01"
    codex_root.mkdir(parents=True)
    write_session(
        codex_root / "three.jsonl",
        [
            codex_record("session_meta", {"cwd": str(tmp_path / "three")}),
            codex_record(
                "response_item",
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "proposed design"}],
                },
            ),
            codex_record(
                "response_item",
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "不要过度设计"}],
                },
            ),
        ],
        300,
    )
    write_session(
        codex_root / "live.jsonl",
        [codex_record("session_meta", {"cwd": str(tmp_path / "live")})],
        600,
    )
    command = [
        sys.executable,
        "-I",
        str(SCRIPT),
        str(claude_root),
        "deep",
        "--codex-root",
        str(codex_root.parent.parent.parent),
        "--all-projects",
    ]
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "conversation_scope: all_projects" in result.stdout
    assert "files_discovered: 5" in result.stdout
    assert "cross_runtime_full_history: yes" in result.stdout
    assert "cross_project_full_history: yes" in result.stdout
    assert "live_files_skipped: 0" in result.stdout
    assert "coverage_status: complete" in result.stdout
    assert "signal_files_scanned: 5" in result.stdout
    assert "simplicity_scope: 1" in result.stdout


def test_all_projects_does_not_claim_full_history_when_recent_files_are_skipped(
    tmp_path: Path,
):
    claude_root = tmp_path / "claude-projects"
    claude_root.mkdir()
    write_session(
        claude_root / "previous.jsonl",
        [record("user", "还是不对")],
        100,
    )
    write_session(
        claude_root / "live.jsonl",
        [record("user", "live")],
        int(time.time()),
    )
    codex_root = tmp_path / "codex-sessions"
    codex_root.mkdir()

    output = run_audit(
        claude_root,
        "deep",
        codex_root=codex_root,
        all_projects=True,
    )

    assert "live_files_skipped: 1" in output
    assert "coverage_status: live_sessions_excluded" in output
    assert "all_previous_files_scanned: yes" in output
    assert "cross_project_full_history: no" in output


def test_empty_or_missing_roots_never_claim_complete_coverage(tmp_path: Path):
    empty_claude = tmp_path / "empty-claude"
    empty_codex = tmp_path / "empty-codex"
    empty_claude.mkdir()
    empty_codex.mkdir()

    empty_output = run_audit(
        empty_claude,
        "deep",
        codex_root=empty_codex,
        all_projects=True,
    )
    missing_output = run_audit(
        tmp_path / "missing-claude",
        "deep",
        codex_root=tmp_path / "missing-codex",
        all_projects=True,
    )

    assert "coverage_status: no_data" in empty_output
    assert "all_previous_files_scanned: no" in empty_output
    assert "cross_project_full_history: no" in empty_output
    assert "coverage_status: unavailable" in missing_output
    assert "all_previous_files_scanned: no" in missing_output
    assert "cross_project_full_history: no" in missing_output


def test_all_projects_requires_both_runtime_roots(tmp_path: Path):
    claude_root = tmp_path / "claude-projects"
    claude_root.mkdir()
    result = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), str(claude_root), "deep", "--all-projects"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 2
    assert "--all-projects requires --codex-root" in result.stderr


def test_requested_missing_codex_root_is_reported_as_unavailable(tmp_path: Path):
    claude_root = tmp_path / "claude-project"
    claude_root.mkdir()
    write_session(
        claude_root / "previous.jsonl",
        [record("user", "continue")],
        100,
    )
    project_root = tmp_path / "project"
    project_root.mkdir()

    output = run_audit(
        claude_root,
        "deep",
        codex_root=tmp_path / "missing-codex",
        project_root=project_root,
    )

    assert "conversation_runtime: claude_project_logs,codex_project_logs" in output
    assert "coverage_status: unavailable" in output
    assert "runtime_coverage: runtime=codex_project_logs files=0 previous=0" in output
    assert "root_available=no" in output
    assert "cross_runtime_full_history: no" in output


def test_summary_bounds_codex_candidate_metadata_reads(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    claude = tmp_path / "claude"
    claude.mkdir()
    write_session(
        claude / "live.jsonl",
        [record("user", "live")],
        int(time.time()),
    )
    write_session(claude / "previous.jsonl", [record("user", "继续")], 100)

    codex_root = tmp_path / "codex"
    recent = codex_root / "2026" / "08" / "01"
    old = codex_root / "2025" / "01" / "01"
    recent.mkdir(parents=True)
    old.mkdir(parents=True)
    for index in range(201):
        write_session(
            recent / f"session-{index:03d}.jsonl",
            [codex_record("session_meta", {"cwd": str(tmp_path / "other")})],
            1000 + index,
        )
    write_session(
        old / "matching.jsonl",
        [
            codex_record("session_meta", {"cwd": str(project)}),
            codex_record(
                "response_item",
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "还是有问题"}],
                },
            ),
        ],
        10,
    )

    output = run_audit(claude, "summary", codex_root, project)

    assert "discovery_limited: yes" in output
    assert "discovery_candidate_limit: 200" in output
    assert "matching.jsonl" not in output
    assert "还是有问题" not in output


def test_oversized_jsonl_record_is_skipped_without_hiding_later_records(
    tmp_path: Path,
):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(
        sessions / "live.jsonl",
        [record("user", "live")],
        int(time.time()),
    )
    oversized = record("assistant", "x" * 1_100_000)
    write_session(
        sessions / "previous.jsonl",
        [
            oversized,
            record("assistant", "bounded answer"),
            record("user", "还是不对"),
        ],
        100,
    )

    output = run_audit(sessions, "deep")

    assert "oversized_records: 1" in output
    assert "coverage_status: incomplete" in output
    assert "USER CORRECTION:" in output


def test_large_tool_output_is_counted_without_rendering_its_payload(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(
        sessions / "live.jsonl",
        [record("user", "live")],
        int(time.time()),
    )
    marker = "tool-payload-must-not-be-rendered"
    write_session(
        sessions / "previous.jsonl",
        [
            codex_record(
                "response_item",
                {"type": "custom_tool_call", "name": "exec_command"},
            ),
            codex_record(
                "response_item",
                {
                    "type": "custom_tool_call_output",
                    "status": "error",
                    "output": marker + ("x" * 500_000),
                },
            ),
        ],
        100,
    )

    output = run_audit(sessions, "deep")

    assert "tool_calls_seen: 1" in output
    assert "tool_results_seen: 1" in output
    assert "tool_errors_seen: 1" in output
    assert marker not in output
    assert "json.dumps(payload" not in SCRIPT.read_text(encoding="utf-8")


def test_conversation_discovery_rejects_file_and_directory_symlinks(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    write_session(
        sessions / "safe.jsonl",
        [record("assistant", "safe answer"), record("user", "还是不对")],
        100,
    )

    outside = tmp_path / "outside"
    outside.mkdir()
    write_session(
        outside / "escaped.jsonl",
        [record("assistant", "answer"), record("user", "ESCAPED-CONVERSATION")],
        50,
    )
    (sessions / "escaped.jsonl").symlink_to(outside / "escaped.jsonl")
    (sessions / "escaped-dir").symlink_to(outside, target_is_directory=True)

    output = run_audit(sessions, "deep")

    assert "files_discovered: 1" in output
    assert "ESCAPED-CONVERSATION" not in output
    assert "USER CORRECTION:" in output


def test_control_characters_in_filenames_cannot_forge_report_sections(tmp_path: Path):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    forged_name = "session\n=== FORGED CONVERSATION SECTION ===.jsonl"
    write_session(
        sessions / forged_name,
        [record("assistant", "answer"), record("user", "还是不对")],
        100,
    )

    output = run_audit(sessions, "deep")

    assert "=== FORGED CONVERSATION SECTION ===" not in output.splitlines()
    assert "files_discovered: 1" in output
    assert "USER CORRECTION:" in output
