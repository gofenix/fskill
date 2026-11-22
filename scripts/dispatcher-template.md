---
name: fskill
description: 'Dispatch explicit fskill commands, or route engineering requests within the current session after the user explicitly enters /f-mode. Direct skill commands remain available; /f-mode off stops automatic routing.'
---

# fskill: Engineering Skills Dispatcher

Prefix your first line with 🥷 inline, not as its own paragraph.

Every skill takes `/name`, `$name`, `/fskill:name`, or `/fskill name`; `think`, `hunt`, and `check` may also be selected by the model when the task itself is theirs, and the other nine start only on an explicit call. Discussing a command or matching a topic does not invoke a skill that is explicit-only. `/f-mode` explicitly enables session routing; `/f-mode off` disables it, and `/f-mode status` only reports state. New sessions start with f-mode off. Read the f-mode section for its session rules; direct commands take priority without changing f-mode state. `/catchup` reports progress. Calibration and an approved task graph are modes inside `/think`, not separate commands.

## Routing Table

<!-- routing-table:start -->
<!-- routing-table:end -->

## How This Works

1. Process explicit f-mode control or skill commands first. Outside f-mode, only tasks matching `think`, `hunt`, or `check` may auto-enter those skills; all other requests stay ordinary requests.
   `/f-help` answers usage questions without changing f-mode state or starting the recommended workflow; a separate explicit work request keeps its existing authorization.
2. Inside active f-mode, match the user's goal to a working skill from the table (or `f-help` for fskill usage questions), then read its section in full. Do not route f-mode back into itself.
3. Execute within the requested scope and existing authorization. Routing does not authorize extra actions.

If the message could match multiple skills, use these disambiguation rules:

1. Most specific wins (when both are eligible, e.g. inside f-mode or explicit call): `/ui` owns deliverable UI design and polish; `/think` (prototype UI mode) owns throwaway layout/structure experiments.
2. One URL or PDF, and a multi-source investigation, both use `/learn`. One source reads that skill's single-source mode. The goal determines the mode, not a separate command.
3. Code already done vs. code broken: done/PR -> `/check`; error/broken -> `/hunt`.
4. Config/maintainability vs. code: Codex/Claude misbehaving, hooks/MCP, `/health` token usage, AI coding code rot, unclear context, missing verification, stale verifier output, rule/skill pruning, or human-only setup/migration wizard -> `/health`; user code errors -> `/hunt`.
5. Release action vs. release prose: commit/tag/publish/push/release reactions/close issue -> `/check`; write release notes/changelog text -> `/write`.
6. Screenshot taste vs. screenshot regression: visual taste complaint -> `/ui`; broken render/state/generated output or used-to-work evidence -> `/hunt`.
7. From scratch vs. editing: multi-source research or new long-form synthesis -> `/learn`; drafting from user-supplied notes or polishing an existing draft -> `/write`.
8. "Judge this" + error -> `/hunt`; "judge this" + should we keep it -> `/think`; "judge this" + worth a release -> `/check`.
9. Still ambiguous: read both skills' "Not for" sections; use exclusion. If still unclear, ask the user.

## Path Resolution

In this distribution, sub-skill assets live under `skills/{name}/{scripts,references,agents}/`. Resolve all relative paths from this file's directory, not from a personal home-directory skill cache.

## Chaining

Each skill stops at the requested outcome. Inside active f-mode, select the next skill only when needed for that outcome; outside f-mode, do not chain into another skill automatically. Complete an already authorized workflow without approval at every transition. Do not infer authorization to implement a planning-only request, publish a fix, or write durable lessons.

Common chains: `/think` -> the current agent does ordinary work, or `/think` coordinates an approved task graph -> `/check` | `/hunt` -> fix -> `/check` -> release/push/issue follow-through | `/learn` -> `/write`
