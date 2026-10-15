---
name: fskill
description: 'Dispatch explicit fskill commands, or route engineering requests within the current session after the user explicitly enters /f-mode. Direct skill commands remain available; /f-mode off stops automatic routing.'
---

# fskill: Engineering Skills Dispatcher

Prefix your first line with 🥷 inline, not as its own paragraph.

Default invocation is explicit: `/name`, `$name`, or `/fskill name`. Discussing a command or matching a topic does not invoke it. `/f-mode` explicitly enables session routing; `/f-mode off` disables it, and `/f-mode status` only reports state. New sessions start with f-mode off. Read the f-mode section for its session rules; direct commands take priority without disabling f-mode.

## Routing Table

<!-- routing-table:start -->
<!-- routing-table:end -->

## How This Works

1. Process explicit f-mode control or skill commands first. Outside f-mode, ordinary requests stay ordinary requests.
   `/f-help` answers usage questions without changing f-mode state or starting the recommended workflow; a separate explicit work request keeps its existing authorization.
2. Inside active f-mode, match the user's goal to a working skill from the table, then read its section in full. Do not route f-mode back into itself.
3. Execute within the requested scope and existing authorization. Routing does not authorize extra actions.

If the message could match multiple skills, use these disambiguation rules:

1. Most specific wins: `/ui` is more specific than `/think` for UI decisions.
2. One URL or PDF to fetch or summarize -> `/read`; multi-source investigation -> `/learn`. The goal determines the skill, not the presence of a URL.
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

Each skill stops at the requested outcome. Inside active f-mode, select the next skill only when needed for that outcome; otherwise switching requires a direct command. Complete an already authorized workflow without approval at every transition. Do not infer authorization to implement a planning-only request, publish a fix, or write durable lessons.

Common chains: `/think` -> implement approved plan -> `/check` | `/hunt` -> fix -> `/check` -> release/push/issue follow-through | `/read` -> `/learn` -> `/write`
