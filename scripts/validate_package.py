#!/usr/bin/env python3
"""Build and validate the Claude Desktop dispatcher ZIP entrypoint.

Invoked by scripts/package-skill.sh after the ZIP is unpacked into a temp
directory. Verifies the generated root SKILL.md exists, carries the ninja
marker, inlines every skill section, and closes every packaged runtime path.

Lives in scripts/ (build-time only); never shipped to end users, so it stays
a real file rather than a heredoc.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

from markdown_fragments import github_heading_inventory, github_heading_records

# Derived from the repo's skills/ tree so a renamed or added skill is expected
# automatically; validate_package runs from the repo checkout at build time.
REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_SKILLS = sorted(p.parent.name for p in (REPO_ROOT / "skills").glob("*/SKILL.md"))
SKILL_NAME_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
MARKDOWN_LINK_RE = re.compile(
    r"(?P<prefix>\[[^\]\n]*\]\(\s*)"
    r"(?P<destination><[^>\n]+>|[^)\s]+)"
    r"(?P<suffix>[^)\n]*\))"
)
INLINE_CODE_RE = re.compile(r"(?<!`)`(?P<content>[^`\n]+)`(?!`)")
RUNTIME_ROOTS = frozenset({"references", "agents", "scripts"})
EXTERNAL_REFERENCE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def _split_reference_suffix(reference: str) -> tuple[str, str]:
    positions = [index for marker in "?#" if (index := reference.find(marker)) >= 0]
    if not positions:
        return reference, ""
    split_at = min(positions)
    return reference[:split_at], reference[split_at:]


def _reference_fragment(reference: str) -> str:
    _, suffix = _split_reference_suffix(reference)
    if "#" not in suffix:
        return ""
    return unquote(suffix.split("#", 1)[1])


def _reference_parts(reference: str) -> tuple[str, tuple[str, ...]] | None:
    encoded_path, _ = _split_reference_suffix(reference)
    decoded_path = unquote(encoded_path)
    if any(marker in decoded_path for marker in ("<", ">", "*", "{", "}")):
        return None
    parts = tuple(
        part for part in PurePosixPath(decoded_path).parts if part not in ("", ".")
    )
    if not parts:
        return None
    if "..." in parts:
        return None
    return encoded_path, parts


def _unsafe_local_reference(reference: str) -> bool:
    encoded_path, _ = _split_reference_suffix(reference)
    decoded_path = unquote(encoded_path)
    if (
        not decoded_path
        or decoded_path.startswith("//")
        or EXTERNAL_REFERENCE_RE.match(decoded_path)
        or any(marker in decoded_path for marker in ("<", ">", "*", "{", "}"))
    ):
        return False
    path = PurePosixPath(decoded_path)
    return path.is_absolute() or ".." in path.parts


def _parent_traversal_reference(reference: str) -> bool:
    encoded_path, _ = _split_reference_suffix(reference)
    decoded_path = unquote(encoded_path)
    if EXTERNAL_REFERENCE_RE.match(decoded_path):
        return False
    return ".." in PurePosixPath(decoded_path).parts


def _reference_kind(reference: str) -> str | None:
    parsed = _reference_parts(reference)
    if not parsed:
        return None
    _, parts = parsed
    if (
        len(parts) > 3
        and parts[0] == "skills"
        and SKILL_NAME_RE.fullmatch(parts[1])
        and parts[2] in RUNTIME_ROOTS
    ):
        return "qualified"
    if parts[0] in RUNTIME_ROOTS and len(parts) > 1:
        return "runtime-relative"
    if len(parts) == 1 and PurePosixPath(parts[0]).suffix:
        return "basename"
    return None


def _safe_skill_relative(target: Path, skill_root: Path) -> Path | None:
    try:
        target.resolve().relative_to(skill_root.resolve())
        return target.relative_to(skill_root)
    except ValueError:
        return None


def _resolve_skill_targets(
    reference: str,
    skill_root: Path,
    source_relative: Path,
) -> tuple[Path, ...]:
    parsed = _reference_parts(reference)
    kind = _reference_kind(reference)
    if not parsed or kind not in {"runtime-relative", "basename"}:
        return ()
    _, parts = parsed
    if ".." in parts:
        return ()

    if kind == "runtime-relative":
        target = skill_root.joinpath(*parts)
        if target.is_file() and _safe_skill_relative(target, skill_root):
            return (target,)
        return ()

    basename = parts[0]
    direct = skill_root / source_relative.parent / basename
    direct_relative = _safe_skill_relative(direct, skill_root)
    if (
        direct.is_file()
        and direct_relative
        and direct_relative.parts
        and direct_relative.parts[0] in RUNTIME_ROOTS
    ):
        return (direct,)

    matches: dict[Path, Path] = {}
    for runtime_root in sorted(RUNTIME_ROOTS):
        root = skill_root / runtime_root
        if not root.is_dir():
            continue
        for candidate in root.rglob("*"):
            if candidate.name != basename or not candidate.is_file():
                continue
            relative = _safe_skill_relative(candidate, skill_root)
            if relative:
                matches[candidate.resolve()] = candidate
    return tuple(
        sorted(
            matches.values(),
            key=lambda candidate: candidate.relative_to(skill_root).as_posix(),
        )
    )


def _resolve_skill_target(
    reference: str,
    skill_root: Path,
    source_relative: Path,
) -> Path | None:
    targets = _resolve_skill_targets(reference, skill_root, source_relative)
    return targets[0] if len(targets) == 1 else None


def _encoded_package_reference(
    reference: str,
    skill: str,
    skill_root: Path,
    target: Path,
) -> str:
    encoded_path, suffix = _split_reference_suffix(reference)
    while encoded_path.startswith("./"):
        encoded_path = encoded_path[2:]
    kind = _reference_kind(reference)
    if kind == "basename":
        relative = target.relative_to(skill_root)
        parent = relative.parent.as_posix()
        encoded_path = (
            f"{parent}/{encoded_path}" if parent != "." else encoded_path
        )
    return f"skills/{skill}/{encoded_path}{suffix}"


def _rewrite_reference(
    reference: str,
    skill: str,
    skill_root: Path,
    source_relative: Path,
) -> str:
    if _reference_kind(reference) == "qualified":
        return reference
    target = _resolve_skill_target(reference, skill_root, source_relative)
    if not target:
        return reference
    return _encoded_package_reference(reference, skill, skill_root, target)


def rewrite_skill_runtime_paths(
    text: str,
    skill: str,
    *,
    skill_root: Path | None = None,
    source_relative: Path = Path("SKILL.md"),
) -> str:
    """Qualify runtime paths that were relative to one skill before packaging."""

    if not SKILL_NAME_RE.fullmatch(skill):
        raise ValueError(f"invalid skill name: {skill!r}")
    root = skill_root or REPO_ROOT / "skills" / skill

    def rewrite_link(match: re.Match[str]) -> str:
        destination = match.group("destination")
        angled = destination.startswith("<") and destination.endswith(">")
        reference = destination[1:-1] if angled else destination
        rewritten = _rewrite_reference(reference, skill, root, source_relative)
        if angled:
            rewritten = f"<{rewritten}>"
        return f"{match.group('prefix')}{rewritten}{match.group('suffix')}"

    def rewrite_inline_code(match: re.Match[str]) -> str:
        content = match.group("content")
        rewritten = _rewrite_reference(content, skill, root, source_relative)
        return f"`{rewritten}`"

    return INLINE_CODE_RE.sub(rewrite_inline_code, MARKDOWN_LINK_RE.sub(rewrite_link, text))


def iter_runtime_references(text: str):
    """Yield (path, syntax, line) for packaged local runtime references."""

    for match in MARKDOWN_LINK_RE.finditer(text):
        destination = match.group("destination")
        if destination.startswith("<") and destination.endswith(">"):
            destination = destination[1:-1]
        if _reference_kind(destination) or _unsafe_local_reference(destination):
            yield destination, "Markdown link", text.count("\n", 0, match.start()) + 1

    for match in INLINE_CODE_RE.finditer(text):
        content = match.group("content")
        if _reference_kind(content) or _parent_traversal_reference(content):
            yield content, "backtick path", text.count("\n", 0, match.start()) + 1


def _root_skill_contexts(text: str, expected: list[str]) -> dict[int, str]:
    contexts: dict[int, str] = {}
    current = ""
    expected_set = set(expected)
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("# SKILL: "):
            candidate = line.removeprefix("# SKILL: ").strip()
            current = candidate if candidate in expected_set else ""
        if current:
            contexts[line_number] = current
    return contexts


def validate_stage(stage: Path, expected_skills: list[str] | None = None) -> list[str]:
    expected = EXPECTED_SKILLS if expected_skills is None else expected_skills
    errors: list[str] = []

    if not expected:
        return [
            "no skills found under repo skills/*/SKILL.md; "
            "cannot validate inlined sections"
        ]

    root_skill = stage / "SKILL.md"
    if not root_skill.exists():
        return ["SKILL.md missing from extracted ZIP"]

    text = root_skill.read_text()

    if "Prefix your first line with 🥷 inline" not in text:
        errors.append("root SKILL.md missing ninja prefix instruction")

    for skill in expected:
        if f"# SKILL: {skill}" not in text:
            errors.append(f"SKILL section '{skill}' not inlined in root SKILL.md")

    # The packager rewrites `skills/<name>/SKILL.md` references to the inlined
    # section name. Any stragglers indicate a regex bug in the rewriter.
    for skill in expected:
        if f"skills/{skill}/SKILL.md" in text:
            errors.append(
                "root SKILL.md still contains nested SKILL.md path references "
                f"(e.g. skills/{skill}/SKILL.md)"
            )

    stage_root = stage.resolve()
    for markdown in sorted(stage.rglob("*.md")):
        source = markdown.relative_to(stage).as_posix()
        source_text = markdown.read_text()
        source_fragments, _ = github_heading_inventory(source_text)
        source_fragment_lines = dict(github_heading_records(source_text))
        source_parts = PurePosixPath(source).parts
        source_skill = ""
        source_relative = Path(source)
        if (
            len(source_parts) > 2
            and source_parts[0] == "skills"
            and source_parts[1] in expected
        ):
            source_skill = source_parts[1]
            source_relative = Path(*source_parts[2:])
        root_contexts = (
            _root_skill_contexts(source_text, expected)
            if source == "SKILL.md"
            else {}
        )
        for match in MARKDOWN_LINK_RE.finditer(source_text):
            destination = match.group("destination")
            if destination.startswith("<") and destination.endswith(">"):
                destination = destination[1:-1]
            if not destination.startswith("#"):
                continue
            fragment = unquote(destination[1:])
            line = source_text.count("\n", 0, match.start()) + 1
            if fragment not in source_fragments:
                errors.append(
                    f"{source}:{line}: missing same-document Markdown fragment: "
                    f"{destination}"
                )
            elif source == "SKILL.md":
                link_skill = root_contexts.get(line, "")
                target_skill = root_contexts.get(source_fragment_lines[fragment], "")
                if link_skill != target_skill:
                    errors.append(
                        f"{source}:{line}: cross-skill same-document Markdown "
                        f"fragment: {destination} targets {target_skill or 'dispatcher'}"
                    )
        for reference, syntax, line in iter_runtime_references(source_text):
            kind = _reference_kind(reference)
            skill = source_skill or root_contexts.get(line, "")
            if kind in {"runtime-relative", "basename"} and skill:
                skill_root = stage / "skills" / skill
                targets = _resolve_skill_targets(
                    reference,
                    skill_root,
                    source_relative,
                )
                if len(targets) == 1:
                    target = targets[0]
                    expected_reference = _encoded_package_reference(
                        reference,
                        skill,
                        skill_root,
                        target,
                    )
                    errors.append(
                        f"{source}:{line}: unqualified {syntax}: {reference} "
                        f"(expected {expected_reference})"
                    )
                    continue
                if len(targets) > 1:
                    matches = ", ".join(
                        f"skills/{skill}/"
                        f"{target.relative_to(skill_root).as_posix()}"
                        for target in targets
                    )
                    errors.append(
                        f"{source}:{line}: ambiguous {syntax}: {reference} "
                        f"(matches {matches})"
                    )
                    continue
            if kind == "basename" and syntax == "backtick path":
                continue

            encoded_path, _ = _split_reference_suffix(reference)
            decoded_path = unquote(encoded_path)
            target = (stage_root / decoded_path).resolve()
            try:
                target.relative_to(stage_root)
            except ValueError:
                errors.append(
                    f"{source}:{line}: {syntax} escapes package root: {reference}"
                )
                continue
            if not target.exists():
                errors.append(
                    f"{source}:{line}: missing {syntax} target: {reference}"
                )
                continue
            fragment = _reference_fragment(reference)
            if (
                syntax == "Markdown link"
                and fragment
                and target.is_file()
                and target.suffix.lower() == ".md"
            ):
                target_fragments, _ = github_heading_inventory(target.read_text())
                if fragment not in target_fragments:
                    errors.append(
                        f"{source}:{line}: missing Markdown fragment: {reference}"
                    )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", nargs="?", type=Path, help="Extracted ZIP root")
    parser.add_argument(
        "--rewrite-skill-paths",
        metavar="SKILL",
        help="Rewrite one skill's runtime paths from stdin or --rewrite-file",
    )
    parser.add_argument(
        "--rewrite-file",
        type=Path,
        help="Rewrite this Markdown file in place",
    )
    parser.add_argument(
        "--skill-root",
        type=Path,
        help="Skill root used to confirm relative runtime targets",
    )
    parser.add_argument(
        "--source-relative",
        type=Path,
        default=Path("SKILL.md"),
        help="Markdown path relative to the skill root",
    )
    args = parser.parse_args()

    if args.rewrite_skill_paths:
        if args.stage is not None:
            parser.error("stage cannot be used with --rewrite-skill-paths")
        if args.rewrite_file:
            source = args.rewrite_file.read_text()
        else:
            source = sys.stdin.read()
        try:
            rewritten = rewrite_skill_runtime_paths(
                source,
                args.rewrite_skill_paths,
                skill_root=args.skill_root,
                source_relative=args.source_relative,
            )
        except ValueError as error:
            parser.error(str(error))
        if args.rewrite_file:
            args.rewrite_file.write_text(rewritten)
        else:
            sys.stdout.write(rewritten)
        return 0

    if args.stage is None:
        parser.error("stage is required unless --rewrite-skill-paths is used")
    if args.rewrite_file or args.skill_root or args.source_relative != Path("SKILL.md"):
        parser.error(
            "--rewrite-file, --skill-root, and --source-relative "
            "require --rewrite-skill-paths"
        )

    errors = validate_stage(args.stage)
    if errors:
        for error in errors:
            print(f"POST-PACKAGE ERROR: {error}", file=sys.stderr)
        return 1

    print("ok: post-package validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
