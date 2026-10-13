---
name: fskill
description: 'Dispatcher for fskill engineering skills: think (architecture/handoff), ui (artifact-grounded interface design), check (review/release gates), hunt (runtime debugging/regression), write (prose/release copy), learn (research), read (URL/PDF fetch), health (agent config and AI maintainability audit).'
---

# fskill: Engineering Skills Dispatcher

Prefix your first line with 🥷 inline, not as its own paragraph.

Match the user's intent to a skill in the table, read that skill, and execute it. Invocation is explicit: /name or $name.

## Routing Table

<!-- routing-table:start -->
<!-- routing-table:end -->

## How This Works

1. Read the user's message and match it to a skill from the table above.
2. Read the matched skill section in full.
3. Execute that skill's instructions exactly.

If the message could match multiple skills, use these disambiguation rules:

1. Most specific wins: `/ui` is more specific than `/think` for UI decisions.
2. URL in message: start with `/read`. If the content is research material, chain to `/learn`.
3. Code already done vs. code broken: done/PR -> `/check`; error/broken -> `/hunt`.
4. Config/maintainability vs. code: Codex/Claude misbehaving, hooks/MCP, `/health` token usage, AI coding code rot, unclear context, missing verification, or stale verifier output -> `/health`; user code errors -> `/hunt`.
5. Release action vs. release prose: commit/tag/publish/push/release reactions/close issue -> `/check`; write release notes/changelog text -> `/write`.
6. Screenshot taste vs. screenshot regression: visual taste complaint -> `/ui`; broken render/state/generated output or used-to-work evidence -> `/hunt`.
7. From scratch vs. editing: new long-form output -> `/learn`; existing draft to polish -> `/write`.
8. "Judge this" + error -> `/hunt`; "judge this" + should we keep it -> `/think`.
9. Still ambiguous: read both skills' "Not for" sections; use exclusion. If still unclear, ask the user.

## Path Resolution

In this distribution, sub-skill scripts live at `skills/{name}/scripts/`. Resolve all relative paths from this file's directory, not from a personal home-directory skill cache.

## Chaining

Each skill stops at the requested outcome. If the user explicitly authorizes a workflow across skills, complete that workflow without asking for approval at every transition; do not infer authorization for further actions.

Common chains: `/think` -> implement approved plan -> `/check` | `/hunt` -> fix -> `/check` -> release/push/issue follow-through | `/read` -> `/learn` -> `/write`
