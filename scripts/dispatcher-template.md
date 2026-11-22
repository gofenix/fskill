---
name: fskill
description: 'Dispatch explicit fskill commands or route within the session after explicit /f-mode, guided by concise engineering principles. Direct commands remain available; /f-mode off stops automatic routing.'
---

# fskill: Lean Engineering Skills & Principles Dispatcher

Prefix your first line with 🥷 inline, not as its own paragraph.

Every skill takes `/name`, `$name`, `/fskill:name`, or `/fskill name`. `think`, `hunt`, and `check` may also trigger automatically when the task matches them; the other six (`f-mode`, `ui`, `write`, `learn`, `health`, `handoff`) start only on an explicit call or inside active `/f-mode`. The 8 engineering principles live in `skills/f-mode/references/principles.md` (mirrored from `rules/principles.md`), apply quietly without inflating output, and are cited only when they actually changed a concrete decision.

## Routing Table

<!-- routing-table:start -->
<!-- routing-table:end -->

## How This Works

1. Explicit skill commands and `/f-mode` controls take priority without closing `f-mode`. Outside `f-mode`, auto-select only `think`, `hunt`, and `check`.
2. Inside active `f-mode`, read the selected workflow section in full and consult `skills/f-mode/references/principles.md` when trade-offs or boundaries apply; never route `f-mode` into itself or expand action permissions.
3. Disambiguation:
   - Done/PR diff/release readiness -> `/check`; runtime error or broken metric -> `/hunt`; unsettled design or scope -> `/think`.
   - Visual polish/UI build -> `/ui`; render regression -> `/hunt`.
   - Fetch URL/PDF or primary-source research -> `/learn`; rewrite/localize prose -> `/write`.
   - Agent config, hooks, MCP, token tools, rule pruning -> `/health`; project code bugs -> `/hunt`.
   - Still ambiguous -> check each skill's exclusion clause or ask briefly.

## Path Resolution

In this distribution, sub-skill assets live under `skills/{name}/{references,scripts}/`. Resolve all relative paths from this file's directory, never from a home-directory cache.

## Chaining

Each skill stops when its requested outcome is complete; never chain automatically outside active `f-mode` or infer authorization for code edits, branch creation, push, release, or external writes.
