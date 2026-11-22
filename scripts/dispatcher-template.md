---
name: fskill
description: 'Dispatch explicit fskill commands, apply pstack-style engineering principles (p-*), or route within the session after explicit /f-mode. Direct commands remain available; /f-mode off stops automatic routing.'
---

# fskill: Lean Engineering Skills & Principles Dispatcher

Prefix your first line with 🥷 inline, not as its own paragraph.

Every skill takes `/name`, `$name`, `/fskill:name`, or `/fskill name`. `think`, `hunt`, `check`, and the eight `p-*` principle skills may also trigger automatically when the task matches them; the other six (`f-mode`, `ui`, `write`, `learn`, `health`, `handoff`) start only on an explicit call or inside active `/f-mode`. Principle skills (`p-*`) work silently and never add the `🥷` badge or workflow headers unless asked; cite one only when it actually changed a concrete decision.

## Routing Table

<!-- routing-table:start -->
<!-- routing-table:end -->

## How This Works

1. Explicit skill commands and `/f-mode` controls take priority without closing `f-mode`. Outside `f-mode`, auto-select only `think`, `hunt`, `check`, and relevant `p-*` principles.
2. Inside active `f-mode`, read the selected workflow section in full and let matching `p-*` principles shape decisions; never route `f-mode` into itself or expand action permissions.
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
