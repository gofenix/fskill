# fskill Routing

fskill ships twenty workflow skills plus an f-mode entrypoint. Outside f-mode, call a skill with `/name` or `$name`. Explicit `/f-mode` enables routing for the current session; `/f-mode off` disables it, `/f-mode status` reports it. Direct commands take priority without closing f-mode. New sessions start off. A similar word or quoted command does not enter f-mode. Read f-mode before routing, and load only the selected skill. Routing never expands action authorization.

| skill      | use when                                                                 |
|------------|--------------------------------------------------------------------------|
| f-mode    | the user already entered `/f-mode` or `$f-mode`; pick one other skill       |
| think      | turn an idea into an executable plan                                     |
| ui         | pages, components, and screenshot polish                                 |
| domain     | a term or behavior boundary is blocking a decision                       |
| map        | the goal spans sessions and the route is still unclear                   |
| slice      | the spec is settled and needs vertical slices                            |
| prototype  | a throwaway experiment for one hypothesis                                |
| architect  | decide whether a code boundary should split, merge, or deepen            |
| implement  | carry out an approved task graph                                         |
| hunt       | something is already broken; prove the cause before fixing               |
| optimize   | one metric is fixed; try one hypothesis at a time                        |
| check      | review a diff, a spec, or the state before merge, push, or release       |
| triage     | sort an issue or external PR queue                                       |
| verify     | maintain the project's verification guide and harness                    |
| read       | fetch one URL or PDF                                                     |
| learn      | research an unfamiliar domain, codebase, or decision history             |
| write      | rewrite prose and remove AI tone                                         |
| handoff    | hand off or resume the current session                                   |
| retro      | write down a verified lesson that would change the next run              |
| health     | audit agent config, instruction drift, and hooks                         |
| wizard     | guide a setup or migration a person must perform                         |

When two skills both match, read both SKILL.md exclusion lines. Still ambiguous, ask the user.

Full routing table: <https://github.com/gofenix/fskill/blob/main/skills/RESOLVER.md>
