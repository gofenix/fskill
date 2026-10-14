from pathlib import Path

import pytest

from checks_distribution import check_license_notices


CANONICAL = (Path(__file__).resolve().parents[2] / "LICENSE").read_bytes()


def installed_fixture(tmp_path):
    directory = tmp_path / "skills" / "read"
    directory.mkdir(parents=True)
    skill = directory / "SKILL.md"
    skill.write_text("skill body")
    notice = directory / "NOTICE.md"
    notice.write_bytes(CANONICAL)
    return skill, notice


def test_installed_notice_needs_no_repository_root_license(tmp_path):
    skill, _ = installed_fixture(tmp_path)
    check_license_notices(tmp_path, [skill])


def test_missing_notice_in_a_standalone_install_is_rejected(tmp_path):
    skill, notice = installed_fixture(tmp_path)
    notice.unlink()
    with pytest.raises(SystemExit):
        check_license_notices(tmp_path, [skill])


def test_lost_upstream_holder_is_rejected_even_without_root_license(tmp_path):
    skill, notice = installed_fixture(tmp_path)
    notice.write_bytes(CANONICAL.replace(b"Copyright (c) 2026 Lauren Tan", b""))
    # Her name still appears in the acknowledgements; that does not replace
    # the missing copyright line.
    with pytest.raises(SystemExit):
        check_license_notices(tmp_path, [skill])


def test_stale_notice_is_rejected_against_canonical_license(tmp_path):
    skill, _ = installed_fixture(tmp_path)
    (tmp_path / "LICENSE").write_bytes(CANONICAL + b"\nUpdated scope\n")
    with pytest.raises(SystemExit):
        check_license_notices(tmp_path, [skill])
