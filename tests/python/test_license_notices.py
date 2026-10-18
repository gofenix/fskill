from pathlib import Path

import pytest

from checks_distribution import check_root_license


CANONICAL = (Path(__file__).resolve().parents[2] / "LICENSE").read_bytes()


def root_license_fixture(tmp_path):
    license_file = tmp_path / "LICENSE"
    license_file.write_bytes(CANONICAL)
    return license_file


def test_root_license_needs_no_per_skill_copies(tmp_path):
    root_license_fixture(tmp_path)
    check_root_license(tmp_path)


def test_missing_root_license_is_rejected(tmp_path, capsys):
    with pytest.raises(SystemExit):
        check_root_license(tmp_path)
    assert "MISSING LICENSE" in capsys.readouterr().err


@pytest.mark.parametrize("holder", [b"gofenix", b"Tw93", b"Matt Pocock", b"Lauren Tan"])
def test_lost_copyright_holder_is_rejected(tmp_path, holder, capsys):
    license_file = root_license_fixture(tmp_path)
    license_file.write_bytes(CANONICAL.replace(b"Copyright (c) 2026 " + holder, b""))
    # A name in acknowledgements does not replace the copyright line.
    with pytest.raises(SystemExit):
        check_root_license(tmp_path)
    assert "MISSING COPYRIGHT NOTICE" in capsys.readouterr().err


def test_incomplete_root_license_is_rejected(tmp_path, capsys):
    license_file = root_license_fixture(tmp_path)
    license_file.write_bytes(CANONICAL.replace(b"Permission is hereby granted", b""))
    with pytest.raises(SystemExit):
        check_root_license(tmp_path)
    assert "INCOMPLETE LICENSE NOTICE" in capsys.readouterr().err
