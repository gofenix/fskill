"""Unit tests for build_metadata codegen helpers.

These are the pure functions inside the codegen pipeline. Full drift detection
is covered by the shell smoke (tests/test_codegen.sh); here we test the small
transforms.
"""

import pytest

import build_metadata as bm


def test_notices_follow_license_updates_for_every_standalone_skill(tmp_path):
    for name in ("read", "f-mode"):
        directory = tmp_path / "skills" / name
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text("skill body")
    license_file = tmp_path / "LICENSE"
    license_file.write_text("original notice\n")
    assets = bm.collect_skill_shared_assets(tmp_path)
    assert assets["skills/read/NOTICE.md"] == assets["skills/f-mode/NOTICE.md"] == b"original notice\n"
    license_file.write_text("updated notice\n")
    assets = bm.collect_skill_shared_assets(tmp_path)
    assert assets["skills/read/NOTICE.md"] == assets["skills/f-mode/NOTICE.md"] == b"updated notice\n"
    assert bm.shared_asset_source("skills/read/NOTICE.md") == "LICENSE"


def test_standalone_mode_carries_current_routing_without_repo_paths(tmp_path):
    mode = tmp_path / "skills/f-mode"
    mode.mkdir(parents=True)
    (mode / "SKILL.md").write_text("Read references/routing.md")
    resolver = tmp_path / "skills/RESOLVER.md"
    resolver.write_text("| broken | `skills/hunt/SKILL.md` |\n")
    assets = bm.collect_skill_shared_assets(tmp_path)
    assert assets["skills/f-mode/references/routing.md"] == b"| broken | `hunt` |\n"
    # A scope update must reach standalone installs as well as plugin mirrors.
    resolver.write_text("| prose | `skills/write/SKILL.md` |\n")
    assets = bm.collect_skill_shared_assets(tmp_path)
    assert assets["skills/f-mode/references/routing.md"] == b"| prose | `write` |\n"
    assert bm.shared_asset_source("skills/f-mode/references/routing.md") == "skills/RESOLVER.md"


def test_render_readme_rewrites_main_to_latest_asset():
    body = "curl https://raw.githubusercontent.com/gofenix/fskill/main/scripts/setup-rule.sh"
    out = bm.render_readme(body)
    assert "https://github.com/gofenix/fskill/releases/latest/download/setup-rule.sh" in out
    assert "raw.githubusercontent.com" not in out


def test_render_readme_rewrites_pinned_version_to_latest_asset():
    body = "curl https://raw.githubusercontent.com/gofenix/fskill/v1.2.3/scripts/setup-rule.sh"
    out = bm.render_readme(body)
    assert "https://github.com/gofenix/fskill/releases/latest/download/setup-rule.sh" in out
    assert "v1.2.3" not in out


def test_render_readme_no_change_when_already_latest_asset():
    body = "curl https://github.com/gofenix/fskill/releases/latest/download/setup-rule.sh"
    assert bm.render_readme(body) == body


def test_render_script_ref_pins_main():
    body = 'FSKILL_REF="${FSKILL_REF:-main}"'
    out = bm.render_script_ref(body, "9.9.9")
    assert out == 'FSKILL_REF="${FSKILL_REF:-v9.9.9}"'


def test_render_script_ref_repins_old_version():
    body = 'FSKILL_REF="${FSKILL_REF:-v1.2.3}"'
    out = bm.render_script_ref(body, "9.9.9")
    assert out == 'FSKILL_REF="${FSKILL_REF:-v9.9.9}"'


def test_render_dispatcher_injects_table():
    template = """# Header

## Routing

<!-- routing-table:start -->
<!-- routing-table:end -->

## Footer
"""
    skills = [
        {"name": "alpha", "dispatch_intent": "first thing"},
        {"name": "beta", "dispatch_intent": "second thing"},
    ]
    out = bm.render_dispatcher(template, skills)
    assert "| first thing | alpha | `skills/alpha/SKILL.md` |" in out
    assert "| second thing | beta | `skills/beta/SKILL.md` |" in out
    assert "<!-- routing-table:start -->" in out
    assert "<!-- routing-table:end -->" in out
    # Original Header and Footer preserved.
    assert "# Header" in out
    assert "## Footer" in out


def test_render_dispatcher_alphabetical():
    template = "<!-- routing-table:start -->\n<!-- routing-table:end -->"
    skills = [
        {"name": "zebra", "dispatch_intent": "z"},
        {"name": "apple", "dispatch_intent": "a"},
    ]
    out = bm.render_dispatcher(template, skills)
    apple_idx = out.index("apple")
    zebra_idx = out.index("zebra")
    assert apple_idx < zebra_idx


def test_build_codex_plugin_manifest_shape():
    manifest = bm.build_codex_plugin("9.9.9")
    assert manifest["name"] == "fskill"
    assert manifest["version"] == "9.9.9"
    assert manifest["skills"] == "./skills/"
    assert manifest["interface"]["displayName"] == "fskill"
    assert manifest["interface"]["category"] == "Developer Tools"
    assert len(manifest["interface"]["defaultPrompt"]) <= 3


def test_build_codex_marketplace_points_at_plugin_root():
    marketplace = bm.build_codex_marketplace()
    assert marketplace["name"] == "fskill"
    entry = marketplace["plugins"][0]
    assert entry["name"] == "fskill"
    assert entry["source"] == {"source": "local", "path": "./"}
    assert entry["policy"] == {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }
    assert entry["category"] == "Developer Tools"


def test_collect_codex_plugin_tree_ignores_local_cache_files(tmp_path):
    skill_script_dir = tmp_path / "skills" / "check" / "scripts"
    skill_script_dir.mkdir(parents=True)
    (skill_script_dir / "run.py").write_text("print('ok')\n")
    cache_dir = skill_script_dir / "__pycache__"
    cache_dir.mkdir()
    (cache_dir / "run.cpython-314.pyc").write_bytes(b"cache")

    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    (rules_dir / "fskill-routing.md").write_text("routing\n")
    (rules_dir / ".DS_Store").write_bytes(b"noise")

    tree = bm.collect_codex_plugin_tree(tmp_path, "{}\n", "{}\n", {})

    assert ".codex-plugin/plugin.json" in tree
    assert "plugin.json" in tree
    assert "plugins/fskill/skills/check/scripts/run.py" not in tree
    assert "plugins/fskill/rules/fskill-routing.md" not in tree
    assert all("__pycache__" not in path for path in tree)
    assert all(not path.endswith((".pyc", ".DS_Store")) for path in tree)


def test_collect_skill_shared_assets_copies_durable_context_when_linked(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    (rules_dir / "durable-context.md").write_text("preamble\n")
    linked = tmp_path / "skills" / "check"
    linked.mkdir(parents=True)
    (linked / "SKILL.md").write_text(
        "---\nname: x\n---\nSee [references/durable-context.md](references/durable-context.md).\n"
    )
    unlinked = tmp_path / "skills" / "read"
    unlinked.mkdir(parents=True)
    (unlinked / "SKILL.md").write_text("---\nname: x\n---\n")

    tree = bm.collect_skill_shared_assets(tmp_path)

    assert tree["skills/check/references/durable-context.md"] == b"preamble\n"
    assert "skills/read/references/durable-context.md" not in tree


def test_collect_skill_shared_assets_fails_when_link_has_no_source(tmp_path):
    skill_dir = tmp_path / "skills" / "check"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: x\n---\nSee [references/durable-context.md](references/durable-context.md).\n"
    )

    with pytest.raises(SystemExit):
        bm.collect_skill_shared_assets(tmp_path)
