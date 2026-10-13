"""Routing-table checks: RESOLVER.md and rules/waza-routing.md stay in sync with the skills.

Split from skill_checks.py; import through skill_checks (the facade) so the
check inventory stays visible in one place.
"""

from __future__ import annotations

import re
from pathlib import Path

from skill_frontmatter import fail, parse_frontmatter, skill_ref_diff


# Quoted user-utterance triggers in rules/waza-routing.md. Covers straight ("),
# curly (U+201C/D), and CJK corner brackets (「」 U+300C/D, 『』 U+300E/F) so a
# Chinese phrase in 「」 is checked just like one in straight quotes.
QUOTED_PHRASE_RE = re.compile(
    r'"([^"]+)"'
    r'|\u201c([^\u201d]+)\u201d'
    r'|\u300c([^\u300d]+)\u300d'
    r'|\u300e([^\u300f]+)\u300f'
)


def check_resolver(root: Path, skill_names: set[str]):
    """Every skill must be referenced from skills/RESOLVER.md.

    Keeps the human-readable index in lock-step with the SKILL.md descriptions
    the model actually sees.
    """
    resolver_path = root / "skills" / "RESOLVER.md"
    if not resolver_path.exists():
        fail(f"MISSING RESOLVER: expected {resolver_path}")
    resolver_text = resolver_path.read_text()
    missing, stale = skill_ref_diff(resolver_text, skill_names)
    if missing:
        skill = missing[0]
        token = f"skills/{skill}/SKILL.md"
        fail(
            f"RESOLVER GAP: {skill} has no entry in {resolver_path}\n"
            f"  Add a row to a triggers table that references {token!r}."
        )
    for skill in sorted(skill_names):
        print(f"ok: resolver entry for {skill}")

    if stale:
        fail(f"RESOLVER REFERENCES MISSING SKILL: {', '.join(stale)}")
    print("ok: resolver has no stale skill references")
    return resolver_path


def check_waza_routing_skills(root: Path, skill_names: set[str]):
    """rules/waza-routing.md routing table must enumerate exactly the skills
    under skills/. Structural drift only -- trigger phrases stay hand-tuned."""
    path = root / "rules" / "waza-routing.md"
    if not path.exists():
        return
    listed: set[str] = set()
    for line in path.read_text().splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 3:
            continue
        name = cells[1]
        # Skip table header (literal "skill") and separator rows ("---").
        if name == "skill" or set(name) <= {"-", ":"}:
            continue
        if re.fullmatch(r"[a-z][a-z0-9_-]*", name):
            listed.add(name)
    missing = skill_names - listed
    extra = listed - skill_names
    if missing:
        fail(
            "WAZA ROUTING MISSING SKILLS: rules/waza-routing.md table omits: "
            f"{', '.join(sorted(missing))}"
        )
    if extra:
        fail(
            "WAZA ROUTING STALE SKILLS: rules/waza-routing.md lists skills "
            f"not in skills/: {', '.join(sorted(extra))}"
        )
    print(f"ok: rules/waza-routing.md skills match ({len(listed)} skills)")


def check_waza_routing_triggers(root: Path):
    """Quoted user-utterance triggers in rules/waza-routing.md must be grounded.

    The routing table's prose stays hand-tuned, but any phrase in quotes is a
    claim about what a user literally types. Each quoted phrase (split on '/',
    whitespace-normalized) must appear in the matching skill's when_to_use, so
    the routing hint can never advertise a trigger no skill actually claims.
    Unquoted wording is intentionally free and is not checked here.
    """
    path = root / "rules" / "waza-routing.md"
    if not path.exists():
        return
    norm = lambda s: re.sub(r"\s+", "", s)  # noqa: E731
    for line in path.read_text().splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 3:
            continue
        skill = cells[1]
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", skill):
            continue
        skill_md = root / "skills" / skill / "SKILL.md"
        if not skill_md.exists():
            continue  # missing skill dir is check_waza_routing_skills' job
        when = norm(parse_frontmatter(skill_md)["when_to_use"])
        for match in QUOTED_PHRASE_RE.finditer(cells[2]):
            quoted = next(g for g in match.groups() if g is not None)
            for seg in quoted.split("/"):
                seg_norm = norm(seg)
                if seg_norm and seg_norm not in when:
                    fail(
                        f"WAZA ROUTING UNGROUNDED TRIGGER: rules/waza-routing.md "
                        f"row '{skill}' quotes {seg!r}, but it is absent from "
                        f"skills/{skill}/SKILL.md when_to_use.\n"
                        f"  Quote only phrases a user actually types; align the "
                        f"phrase with when_to_use or add it to when_to_use."
                    )
    print("ok: rules/waza-routing.md quoted triggers grounded")
