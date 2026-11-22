<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/logo.svg" width="120" />
  <h1>fskill</h1>
  <p><b>Les réflexes d'ingénierie de gofenix, transformés en vos compétences</b></p>
  <p><a href="README.md">English</a> · <a href="README_CN.md">中文</a> · <a href="README_TW.md">繁體</a> · <a href="README_JA.md">日本語</a> · <a href="README_KR.md">한국어</a> · <a href="README_DE.md">Deutsch</a> · Français</p>
  <a href="https://github.com/gofenix/fskill/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/gofenix/fskill/test.yml?branch=main&style=flat-square&label=tests" alt="Tests"></a>
  <a href="https://github.com/gofenix/fskill/stargazers"><img src="https://img.shields.io/github/stars/gofenix/fskill?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/gofenix/fskill/releases"><img src="https://img.shields.io/github/v/tag/gofenix/fskill?label=version&style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://twitter.com/Higofenix"><img src="https://img.shields.io/badge/follow-gofenix-red?style=flat-square&logo=Twitter" alt="Twitter"></a>
</div>

<br/>

## Compétences (Skills)

fskill associe **9 workflows épurés**, **8 principes d'ingénierie inspirés de `pstack` (`p-*`)** et des scripts déterministes. Chaque compétence s'appelle via `/name` ou `$name` ; `think`, `hunt`, `check` et les 8 principes `p-*` se déclenchent aussi selon la tâche, tandis que les six autres restent sur appel explicite ou via `/f-mode`. Inspiré de [Waza](https://github.com/tw93/Waza), [Matt Pocock skills](https://github.com/mattpocock/skills) et [pstack](https://github.com/cursor/plugins/tree/main/pstack).

| Compétence | Groupe | Ce qu'elle fait |
| :--- | :--- | :--- |
| [`/f-mode`](skills/f-mode/SKILL.md) | Route | Entrer explicitement pour choisir le workflow et les principes `p-*` adaptés à la tâche. |
| [`/think`](skills/think/SKILL.md) | Décider | Cadrage avant action, jugement de valeur (`Drop/Keep/Pivot`), tri de périmètre et `grill me`. |
| [`/hunt`](skills/hunt/SKILL.md) | Trouver le problème | Diagnostic de cause racine par preuve d'exécution et optimisation à une hypothèse par mesure. |
| [`/check`](skills/check/SKILL.md) | Vérifier | Revue de diff/PR fondée sur les preuves, verdict de release, audit de projet et rejeu d'incidents. |
| [`/ui`](skills/ui/SKILL.md) | Interface | UI soignée sans AI slop, mouvement et contrôle sur rendu réel (appel explicite). |
| [`/learn`](skills/learn/SKILL.md) [`/write`](skills/write/SKILL.md) | Lire et écrire | Extraction URL/PDF et synthèse multi-sources ; réécriture sans style IA et notes de version (appel explicite). |
| [`/handoff`](skills/handoff/SKILL.md) [`/health`](skills/health/SKILL.md) | Réutiliser | Passation compacte et audit déterministe de config agent, hooks/MCP et élagage de règles (appel explicite). |

**8 principes `pstack` (`p-*`, déclenchement automatique) :** [`p-subtract-before-add`](skills/p-subtract-before-add/SKILL.md) · [`p-attack-the-premise`](skills/p-attack-the-premise/SKILL.md) · [`p-fix-root-causes`](skills/p-fix-root-causes/SKILL.md) · [`p-prove-it-works`](skills/p-prove-it-works/SKILL.md) · [`p-test-behavior`](skills/p-test-behavior/SKILL.md) · [`p-explain-the-number`](skills/p-explain-the-number/SKILL.md) · [`p-encode-in-structure`](skills/p-encode-in-structure/SKILL.md) · [`p-respect-boundaries`](skills/p-respect-boundaries/SKILL.md)

Entrez `/f-mode` (Codex : `$f-mode`, plugin : `/fskill:f-mode`), puis décrivez vos tâches normalement. Le routage reste actif dans cette session jusqu'à `/f-mode off`. `/f-mode status` affiche l'état. Les commandes directes sont prioritaires sans fermer f-mode. Une nouvelle session démarre sans f-mode. Les autorisations d'action ne changent pas. Table complète : [skills/RESOLVER.md](skills/RESOLVER.md).

## Installation

**Claude Code, Codex, Cursor et autres agents**

```bash
npx skills add gofenix/fskill -a claude-code codex cursor -g -y
```

Les compétences sont installées dans `~/.agents/skills`. Claude Code y accède via un lien symbolique ; Codex, Cursor, Gemini CLI, Copilot, Amp, Kimi Code CLI et tout autre agent lisant ce dossier lisent les 9 workflows et 8 principes. Les workflows explicites ne démarrent que via `/ui`, `$ui` ou dans `/f-mode`. Les agents dotés d'un dossier privé prennent leur identifiant après `-a` (ex. `antigravity-cli` ou `qwen-code`). Mise à jour via `npx skills update -g -y`. Vous pouvez aussi demander directement à votre agent de l'installer :
> Lis https://github.com/gofenix/fskill/blob/main/llms.txt et installe fskill pour moi

**En tant que plugin hôte** (les compétences sont préfixées, ex. `/fskill:check`) :

```bash
# Claude Code (mise à jour : claude plugin update fskill)
/plugin marketplace add gofenix/fskill
/plugin install fskill@fskill

# Codex (mise à jour : codex plugin marketplace upgrade fskill, puis codex plugin add fskill@fskill)
codex plugin marketplace add gofenix/fskill
codex plugin add fskill@fskill
```

**Claude Desktop** : téléchargez [fskill.zip](https://github.com/gofenix/fskill/releases/latest/download/fskill.zip), allez dans Customize > Skills > "+" > Create skill et chargez l'archive. Pour mettre à jour, cliquez sur "..." sur la carte de la compétence, choisissez Replace et chargez la dernière archive ZIP.

**Pi** : `pi install npm:@gofenix/fskill`, mise à jour via `pi update npm:@gofenix/fskill`.

## Enchaîner les compétences

Vous choisissez l'ordre. Chaque compétence s'arrête quand son résultat est là. La suivante se lance avec `/name` ou `$name`.

**Flux courants :**

- **Nouvelle fonctionnalité** : `/think` cadre avec `p-subtract-before-add`. Après accord, l'agent en cours réalise le travail, puis `/check` valide.
- **Correction de bogue** : `/hunt` prouve la cause via `p-fix-root-causes`, correction, puis `/check` revoit les diffs et preuves de release.
- **Recherche et rédaction** : `/learn` lit une URL/PDF ou des sources primaires, `/write` polit le texte.

## Contexte du projet

fskill n'embarque que des principes universels et des scripts déterministes. `/check` lit à l'exécution les fichiers publics du dépôt cible (README, manifestes, Makefile, CI) et vos contraintes, sans jamais accéder à des chemins privés, identifiants ou tokens. Voir [`skills/check/references/review-patterns.md`](skills/check/references/review-patterns.md) et [`skills/check/references/release-artifacts.md`](skills/check/references/release-artifacts.md).

## Outils additionnels

Les URL curl utilisent le dernier asset de release GitHub. Ajoutez `FSKILL_REF=main` avant la commande pour utiliser les scripts les plus récents de main.

### Barre d'état (Statusline)

Une barre d'état minimale pour Claude Code : fenêtre de contexte, quotas 5 heures et 7 jours avec code couleur, sans barre de progression ni encombrement.

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/statusline.png" width="1000" />
</div>

```bash
(
  set -e
  FSKILL_STATUSLINE_SCRIPT="$(mktemp -t fskill-statusline.XXXXXX)"
  trap 'rm -f "$FSKILL_STATUSLINE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-statusline.sh -o "$FSKILL_STATUSLINE_SCRIPT"
  # à vérifier d'abord : less "$FSKILL_STATUSLINE_SCRIPT"
  bash "$FSKILL_STATUSLINE_SCRIPT"
)
```

**Codex** propose nativement ces indicateurs de barre d'état. Ajoutez-les à `~/.codex/config.toml` :

```toml
[tui]
status_line = ["model-with-reasoning", "current-dir", "context-used", "five-hour-limit", "weekly-limit"]
status_line_use_colors = true
```

Codex affiche le quota restant ; la barre d'état Claude Code ci-dessus affiche le pourcentage utilisé (l'amont n'expose pas encore `five-hour-used` / `weekly-used`).

### Règles optionnelles

Les règles optionnelles s'appliquent au-delà des appels de compétences une fois installées dans les instructions persistantes de votre agent. Installer les compétences fskill ne suffit pas à les activer. Copiez celles qui vous intéressent (sur Codex ou Antigravity, remplacez `claude-code` par `codex` ou `antigravity-cli`) :

```bash
(
  set -e
  FSKILL_RULE_SCRIPT="$(mktemp -t fskill-rule.XXXXXX)"
  trap 'rm -f "$FSKILL_RULE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-rule.sh -o "$FSKILL_RULE_SCRIPT"
  # à vérifier d'abord : less "$FSKILL_RULE_SCRIPT"

  # Coaching d'anglais : ajoute une courte correction 😇 quand votre prompt contient une faute d'anglais
  bash "$FSKILL_RULE_SCRIPT" english claude-code

  # Anti-patterns : garde-fous permanents communs à toutes les compétences (lire avant d'agir, ne pas élargir le périmètre, pas de résumé non demandé)
  bash "$FSKILL_RULE_SCRIPT" anti-patterns claude-code

  # Indice de routage : think/hunt/check se lancent seuls sur une tâche qui les concerne, les autres sur appel explicite
  bash "$FSKILL_RULE_SCRIPT" fskill-routing claude-code

  # Réponses claires au quotidien : termes cohérents, conditions explicites, incertitude préservée
  # Clarity est disponible sur main, mais pas encore dans la version publiée
  FSKILL_REF=main bash "$FSKILL_RULE_SCRIPT" clarity claude-code
)
```

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/english-coaching.png" width="1000" />
</div>

[Clarity](rules/clarity.md) reprend les principes d'écriture claire d'ASD-STE100 sans imposer la grammaire de l'anglais contrôlé ni changer votre style. Relancez sa commande pour mettre à jour la règle installée, puis ouvrez une nouvelle session. Codex installe un bloc balisé dans `~/.codex/AGENTS.md` ; Claude Code et Antigravity installent un fichier de règle. Pour les autres outils, copiez la règle dans leurs instructions personnalisées persistantes.

## Pourquoi fskill

fskill associe les scripts déterministes de [tw93/Waza](https://github.com/tw93/Waza) à l'approche par principes de [pstack](https://github.com/cursor/plugins/tree/main/pstack) : **9 workflows légers** (`f-mode`, `think`, `hunt`, `check`, `ui`, `learn`, `write`, `handoff`, `health`) et **8 principes courts** (`p-*`), sans procédures redondantes que les modèles actuels savent déjà faire.

Chaque compétence s'appelle par `/name` ou `$name` ; `think`, `hunt`, `check` et `p-*` se lancent aussi d'eux-mêmes quand la tâche correspond, les six autres seulement sur appel explicite.

## Désinstallation

```bash
npx skills remove gofenix/fskill -g
rm -f ~/.claude/statusline.sh
rm -f ~/.claude/rules/english.md
rm -f ~/.claude/rules/anti-patterns.md
rm -f ~/.claude/rules/fskill-routing.md
rm -f ~/.claude/rules/clarity.md
```

Pour la barre d'état, supprimez aussi l'entrée `statusLine` de `~/.claude/settings.json`. Pour Claude Desktop, supprimez fskill dans Customize > Skills. Pour les règles installées sur Codex, retirez les blocs fskill balisés de `~/.codex/AGENTS.md`. Pour Antigravity, supprimez le fichier de règle choisi dans `~/.gemini/antigravity-cli/rules/`. Retirez les règles copiées des instructions personnalisées des autres outils. Ouvrez une nouvelle session après avoir retiré une règle.

## Soutenir le projet

Si fskill vous a aidé, mettez une étoile au dépôt ou ouvrez une issue.

## Licence

MIT, avec du contenu Apache-2.0 dans les références UI. Merci à [Waza](https://github.com/tw93/Waza), [Matt Pocock skills](https://github.com/mattpocock/skills) et [pstack](https://github.com/cursor/plugins/tree/main/pstack). Les méthodes UI adaptent aussi [Impeccable](https://github.com/pbakaus/impeccable), [taste-skill](https://github.com/Leonxlnx/taste-skill) et [apple-design](https://github.com/emilkowalski/skills). [LICENSE](LICENSE) conserve les versions sources, les modifications et les licences complètes. La mention de gofenix couvre les ajouts et modifications originaux ; les mentions en amont couvrent leurs contenus respectifs réutilisés.
