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

Chaque compétence est un dossier de références, de scripts et d'échecs réels. Par défaut, elle démarre avec `/name` ou `$name`. Un mot proche ne la lance pas. Les procédures viennent de Waza, Matt Pocock skills et pstack ; voir les sources dans la section licence.

| Compétence | Groupe | Ce qu'elle fait |
| :--- | :--- | :--- |
| [`/f-mode`](skills/f-mode/SKILL.md) | Route | Entrer explicitement, puis choisir une compétence ci-dessous. Les commandes seules restent directes. |
| [`/think`](skills/think/SKILL.md) [`/ui`](skills/ui/SKILL.md) [`/domain`](skills/domain/SKILL.md) [`/map`](skills/map/SKILL.md) [`/slice`](skills/slice/SKILL.md) [`/prototype`](skills/prototype/SKILL.md) [`/architect`](skills/architect/SKILL.md) | Décider | Plan, interface, termes, carte entre sessions, découpes, essais, limites. |
| [`/implement`](skills/implement/SKILL.md) [`/hunt`](skills/hunt/SKILL.md) [`/optimize`](skills/optimize/SKILL.md) | Faire | Tâches approuvées, cause racine, une mesure à la fois. |
| [`/check`](skills/check/SKILL.md) [`/triage`](skills/triage/SKILL.md) [`/verify`](skills/verify/SKILL.md) | Livrer | Revue avant merge, push et release, file d'issues, preuve. |
| [`/read`](skills/read/SKILL.md) [`/learn`](skills/learn/SKILL.md) [`/write`](skills/write/SKILL.md) | Lire et écrire | Une URL ou un PDF, recherche multi-sources, prose. |
| [`/handoff`](skills/handoff/SKILL.md) [`/retro`](skills/retro/SKILL.md) [`/health`](skills/health/SKILL.md) [`/wizard`](skills/wizard/SKILL.md) | Réutiliser | Passation de session, leçons vérifiées, config d'agent, installation manuelle. |

Entrez `/f-mode` (Codex : `$f-mode`, plugin : `/fskill:f-mode`), puis décrivez vos tâches normalement. Le routage reste actif dans cette session jusqu'à `/f-mode off`. `/f-mode status` affiche l'état. Les commandes directes sont prioritaires sans fermer f-mode. Une nouvelle session démarre sans f-mode. Les autorisations d'action ne changent pas.

## Installation

**Claude Code, Codex, Cursor et autres agents**

```bash
npx skills add gofenix/fskill -a claude-code codex cursor -g -y
```

Les compétences sont installées dans `~/.agents/skills`. Claude Code y accède via un lien symbolique ; Codex, Cursor, Gemini CLI, Copilot, Amp, Kimi Code CLI et tout autre agent lisant ce dossier lisent les 21 compétences. Le parcours d'une compétence ne démarre qu'avec `/name` ou `$name`. Les agents dotés d'un dossier de compétences privé prennent leur identifiant après `-a` (par exemple `antigravity-cli` ou `qwen-code`). Mise à jour via `npx skills update -g -y`. Vous pouvez aussi demander directement à votre agent de l'installer :
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

- **Nouvelle fonctionnalité** : `/think` pour cadrer, puis implémentation, puis `/check` pour valider et fusionner
- **Correction de bogue** : `/hunt` pour trouver la cause, puis correction, puis `/check` pour revoir les diffs et publier si besoin
- **Recherche et rédaction** : `/read` pour collecter, `/learn` pour structurer, `/write` pour polir

## Contexte du projet

fskill n'embarque que des méthodes d'ingénierie universelles. `/check` lit au moment de l'exécution les fichiers publics du dépôt cible (README, manifestes, Makefile, CI) et vos contraintes, sans jamais accéder à des chemins privés, identifiants ou tokens. Le modèle de contexte de revue se trouve dans [`skills/check/references/project-context.md`](skills/check/references/project-context.md).

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

  # Indice de routage : les noms des compétences, et l'appel explicite, /name ou $name
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

fskill est le jeu de compétences de gofenix. La méthode vient de [tw93/Waza](https://github.com/tw93/Waza), pas le nom : Waza appartient à quelqu'un d'autre. Vingt compétences, cinq groupes : décider, faire, livrer, lire et écrire, réutiliser. `/f-mode` est l'entrée explicite au-dessus. Chacune nomme le résultat, la limite, et ce qui compte comme terminé.

L'appel est explicite : `/name` ou `$name`. Un mot proche ne lance pas le parcours.

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

MIT. Merci à [Waza](https://github.com/tw93/Waza), [Matt Pocock skills](https://github.com/mattpocock/skills) et [pstack](https://github.com/cursor/plugins/tree/main/pstack). fskill combine, traduit et adapte leurs procédures. [LICENSE](LICENSE) est la source unique ; `make regenerate` copie la déclaration complète dans chaque `NOTICE.md` pour les installations individuelles et Multica. La mention de gofenix couvre les ajouts et modifications originaux ; les mentions en amont couvrent leurs contenus respectifs réutilisés.
