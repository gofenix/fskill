<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/logo.svg" width="120" />
  <h1>fskill</h1>
  <p><b>gofenixs Entwicklergewohnheiten, als Skills für deine Agenten</b></p>
  <p><a href="README.md">English</a> · <a href="README_CN.md">中文</a> · <a href="README_TW.md">繁體</a> · <a href="README_JA.md">日本語</a> · <a href="README_KR.md">한국어</a> · Deutsch · <a href="README_FR.md">Français</a></p>
  <a href="https://github.com/gofenix/fskill/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/gofenix/fskill/test.yml?branch=main&style=flat-square&label=tests" alt="Tests"></a>
  <a href="https://github.com/gofenix/fskill/stargazers"><img src="https://img.shields.io/github/stars/gofenix/fskill?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/gofenix/fskill/releases"><img src="https://img.shields.io/github/v/tag/gofenix/fskill?label=version&style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://twitter.com/Higofenix"><img src="https://img.shields.io/badge/follow-gofenix-red?style=flat-square&logo=Twitter" alt="Twitter"></a>
</div>

<br/>

## Skills

Jeder Skill ist ein Ordner mit Referenzen, Skripten und echten Fehlern. Standardmäßig startet er bei `/name` oder `$name`. Ein ähnliches Wort schaltet nicht um. Die Form stammt von [tw93/Waza](https://github.com/tw93/Waza); Name und Text gehören gofenix.

| Skill | Gruppe | Was er tut |
| :--- | :--- | :--- |
| [`/mode`](skills/mode/SKILL.md) | Route | Erst ausdrücklich eintreten, dann eine Fähigkeit unten wählen. Einzelbefehle bleiben direkt nutzbar. |
| [`/think`](skills/think/SKILL.md) [`/ui`](skills/ui/SKILL.md) [`/domain`](skills/domain/SKILL.md) [`/map`](skills/map/SKILL.md) [`/slice`](skills/slice/SKILL.md) [`/prototype`](skills/prototype/SKILL.md) [`/architect`](skills/architect/SKILL.md) | Entscheiden | Plan, Oberfläche, Begriffe, sitzungsübergreifende Karte, Schnitte, Versuche, Grenzen. |
| [`/implement`](skills/implement/SKILL.md) [`/hunt`](skills/hunt/SKILL.md) [`/optimize`](skills/optimize/SKILL.md) | Bauen | Freigegebene Aufgaben, Ursache, eine Metrik auf einmal. |
| [`/check`](skills/check/SKILL.md) [`/triage`](skills/triage/SKILL.md) [`/verify`](skills/verify/SKILL.md) | Abgeben | Prüfung vor Merge, Push und Release, Issue-Warteschlange, Nachweis. |
| [`/read`](skills/read/SKILL.md) [`/learn`](skills/learn/SKILL.md) [`/write`](skills/write/SKILL.md) | Lesen und schreiben | Eine URL oder ein PDF, Recherche aus mehreren Quellen, Text glätten. |
| [`/handoff`](skills/handoff/SKILL.md) [`/retro`](skills/retro/SKILL.md) [`/health`](skills/health/SKILL.md) [`/wizard`](skills/wizard/SKILL.md) | Wiederverwenden | Sitzungsübergabe, geprüfte Lehren, Agent-Konfiguration, manuelles Setup. |

Mit `/mode` (Codex: `$mode`, Plugin: `/fskill:mode`) starten und Aufgaben normal beschreiben. Die Auswahl bleibt in dieser Sitzung bis `/mode off` aktiv. `/mode status` zeigt den Zustand. Direkte Befehle haben Vorrang und lassen mode aktiv. Neue Sitzungen starten ohne mode. Aktionsberechtigungen bleiben unverändert.

## Installation

**Claude Code, Codex, Cursor und andere Agenten**

```bash
npx skills add gofenix/fskill -a claude-code codex cursor -g -y
```

Skills landen zentral in `~/.agents/skills`. Claude Code bindet sie per Symlink ein; Codex, Cursor, Gemini CLI, Copilot, Amp, Kimi Code CLI und alle Agenten, die dieses Verzeichnis nutzen, laden die 21 Skills. Der Ablauf eines Skills startet nur bei `/name` oder `$name`. Agenten mit eigenem Skill-Verzeichnis gibst du nach `-a` mit ihrer ID an (zum Beispiel `antigravity-cli` oder `qwen-code`). Aktualisierung über `npx skills update -g -y`. Du kannst deinen Agenten auch direkt mit der Installation beauftragen:
> Lies https://github.com/gofenix/fskill/blob/main/llms.txt und installiere fskill für mich

**Host-Plugin-Methode** (Skills erhalten ein Namespace-Präfix, z. B. `/fskill:check`):

```bash
# Claude Code (Update: claude plugin update fskill)
/plugin marketplace add gofenix/fskill
/plugin install fskill@fskill

# Codex (Update: codex plugin marketplace upgrade fskill, dann codex plugin add fskill@fskill)
codex plugin marketplace add gofenix/fskill
codex plugin add fskill@fskill
```

**Claude Desktop**: Lade [fskill.zip](https://github.com/gofenix/fskill/releases/latest/download/fskill.zip) herunter, öffne Customize > Skills > "+" > Create skill und lade die ZIP-Datei hoch. Zum Aktualisieren klickst du auf der Skill-Karte auf "...", wählst Replace und lädst die neueste ZIP-Datei hoch.

**Pi**: `pi install npm:@gofenix/fskill`, Update über `pi update npm:@gofenix/fskill`.

## Skill-Kombinationen

Außerhalb von mode bestimmst du die Reihenfolge. Jeder Skill stoppt, wenn sein Ergebnis da ist. Den nächsten rufst du mit `/name` oder `$name` auf.

**Typische Workflows:**

- **Neues Feature**: `/think` prüft den Plan, nach Freigabe implementieren, dann mit `/check` prüfen und mergen
- **Bugfix**: `/hunt` findet die Ursache, dann beheben, dann mit `/check` die Diffs prüfen und bei Bedarf releasen
- **Recherche**: `/read` holt das Material, `/learn` strukturiert es, `/write` formuliert aus

## Projekt-Kontext

fskill liefert universelle Entwicklergewohnheiten. `/check` liest zur Laufzeit nur öffentliche Projektdateien (README, Paketdefinitionen, Makefile, CI-Workflows) und deine Vorgaben, niemals private Pfade, Zugangsdaten oder Tokens. Die Vorlage für den Review-Kontext findest du in [`skills/check/references/project-context.md`](skills/check/references/project-context.md).

## Extras

Die curl-URLs verwenden das neueste GitHub-Release-Asset. Für die neuesten Skripte von main setzt du `FSKILL_REF=main` vor den Befehl.

### Statusleiste

Minimale Statusleiste für Claude Code: Kontext-Window, 5-Stunden- und 7-Tage-Kontingente farbcodiert, ohne Fortschrittsbalken und ohne Ablenkung.

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/statusline.png" width="1000" />
</div>

```bash
(
  set -e
  FSKILL_STATUSLINE_SCRIPT="$(mktemp -t fskill-statusline.XXXXXX)"
  trap 'rm -f "$FSKILL_STATUSLINE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-statusline.sh -o "$FSKILL_STATUSLINE_SCRIPT"
  # vorher prüfen: less "$FSKILL_STATUSLINE_SCRIPT"
  bash "$FSKILL_STATUSLINE_SCRIPT"
)
```

**Codex**-Statuszeile in `~/.codex/config.toml`:

```toml
[tui]
status_line = ["model-with-reasoning", "current-dir", "context-used", "five-hour-limit", "weekly-limit"]
status_line_use_colors = true
```

Codex zeigt das verbleibende Kontingent, die Claude-Code-Statusleiste oben den verbrauchten Anteil (upstream gibt es `five-hour-used` / `weekly-used` noch nicht).

### Optionale Regeln

Optionale Regeln wirken auch außerhalb von Skill-Aufrufen, sobald sie in den dauerhaften Anweisungen deines Agenten installiert sind. Die Installation der fskill-Skills allein aktiviert sie nicht. Kopiere die gewünschten Befehle (bei Codex oder Antigravity ersetzt du `claude-code` durch `codex` bzw. `antigravity-cli`):

```bash
(
  set -e
  FSKILL_RULE_SCRIPT="$(mktemp -t fskill-rule.XXXXXX)"
  trap 'rm -f "$FSKILL_RULE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-rule.sh -o "$FSKILL_RULE_SCRIPT"
  # vorher prüfen: less "$FSKILL_RULE_SCRIPT"

  # Englisch-Coaching: hängt eine kurze 😇-Korrektur an, wenn dein Prompt einen Englischfehler enthält
  bash "$FSKILL_RULE_SCRIPT" english claude-code

  # Anti-Patterns: stets aktive, skillübergreifende Leitplanken (erst lesen, dann handeln; kein Scope Creep; keine ungefragten Zusammenfassungen)
  bash "$FSKILL_RULE_SCRIPT" anti-patterns claude-code

  # Routing-Hinweis: Skill-Namen, und dass der Aufruf explizit ist, /name oder $name
  bash "$FSKILL_RULE_SCRIPT" fskill-routing claude-code

  # Klare Alltagsantworten: einheitliche Begriffe, explizite Bedingungen, Unsicherheit bleibt erhalten
  # Clarity ist auf main verfügbar, aber noch nicht im aktuellen Release
  FSKILL_REF=main bash "$FSKILL_RULE_SCRIPT" clarity claude-code
)
```

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/english-coaching.png" width="1000" />
</div>

[Clarity](rules/clarity.md) übernimmt Prinzipien für klares Schreiben aus ASD-STE100, ohne die Grammatik von kontrolliertem Englisch vorzuschreiben oder deinen Stil zu ändern. Führe den Befehl erneut aus, um die installierte Regel zu aktualisieren, und starte danach eine neue Sitzung. Codex installiert einen markierten Block in `~/.codex/AGENTS.md`; Claude Code und Antigravity installieren eine Regeldatei. Bei anderen Tools kopierst du die Regel in deren dauerhafte benutzerdefinierte Anweisungen.

## Warum fskill

fskill ist gofenix' eigenes Skill-Set. Die Arbeitsweise kommt von [tw93/Waza](https://github.com/tw93/Waza), der Name nicht, denn Waza gehört jemand anderem. Es sind zwanzig Skills in fünf Gruppen: entscheiden, bauen, abgeben, lesen und schreiben, wiederverwenden. Darüber liegt der ausdrückliche Einstieg `/mode`. Jeder Skill nennt das Ergebnis, die Grenze und woran man Fertig erkennt.

Der Aufruf ist explizit: `/name` oder `$name`. Ein ähnliches Wort startet den Ablauf nicht.

## Deinstallation

```bash
npx skills remove gofenix/fskill -g
rm -f ~/.claude/statusline.sh
rm -f ~/.claude/rules/english.md
rm -f ~/.claude/rules/anti-patterns.md
rm -f ~/.claude/rules/fskill-routing.md
rm -f ~/.claude/rules/clarity.md
```

Für die Statusleiste entfernst du außerdem den Eintrag `statusLine` aus `~/.claude/settings.json`. In Claude Desktop löschst du fskill unter Customize > Skills. Bei Codex-Regelinstallationen entfernst du die markierten fskill-Blöcke aus `~/.codex/AGENTS.md`. Bei Antigravity entfernst du die gewählte Regeldatei aus `~/.gemini/antigravity-cli/rules/`. In anderen Tools entfernst du kopierte Regeln aus den benutzerdefinierten Anweisungen. Starte nach dem Entfernen einer Regel eine neue Sitzung.

## Unterstützung

Wenn fskill geholfen hat, gib dem Repo einen Star oder öffne ein Issue.

## Lizenz

MIT License. Please feel free to use and contribute to the development.
