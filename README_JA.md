<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/logo.svg" width="120" />
  <h1>fskill</h1>
  <p><b>gofenix のエンジニアリング習慣を、あなたのスキルに</b></p>
  <p><a href="README.md">English</a> · <a href="README_CN.md">中文</a> · <a href="README_TW.md">繁體</a> · 日本語 · <a href="README_KR.md">한국어</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a></p>
  <a href="https://github.com/gofenix/fskill/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/gofenix/fskill/test.yml?branch=main&style=flat-square&label=tests" alt="Tests"></a>
  <a href="https://github.com/gofenix/fskill/stargazers"><img src="https://img.shields.io/github/stars/gofenix/fskill?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/gofenix/fskill/releases"><img src="https://img.shields.io/github/v/tag/gofenix/fskill?label=version&style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://twitter.com/Higofenix"><img src="https://img.shields.io/badge/follow-gofenix-red?style=flat-square&logo=Twitter" alt="Twitter"></a>
</div>

<br/>

## スキル一覧

各スキルは参照、スクリプト、実際に踏んだ失敗をまとめたディレクトリです。通常は `/name` または `$name` で開始します。近い言葉では切り替わりません。Waza、Matt Pocock skills、pstack を基にしています。詳細はライセンス欄を参照してください。

| スキル | グループ | 役割 |
| :--- | :--- | :--- |
| [`/f-mode`](skills/f-mode/SKILL.md) | 経路 | 明示的に入ってから、下のスキルを一つ選ぶ。単体のコマンドもそのまま使える。 |
| [`/f-help`](skills/f-help/SKILL.md) | ヘルプ | fskill の使い方、スキル選び、設定やカスタマイズを質問する。 |
| [`/catchup`](skills/catchup/SKILL.md) | 報告 | 進捗、変化、あなたの判断が必要な事項を読み取り専用で確認。 |
| [`/sharpen`](skills/sharpen/SKILL.md) | 考える | 方法、目的、制約を確認し、許可された作業を実行。 |
| [`/think`](skills/think/SKILL.md) [`/ui`](skills/ui/SKILL.md) [`/domain`](skills/domain/SKILL.md) [`/map`](skills/map/SKILL.md) [`/slice`](skills/slice/SKILL.md) [`/prototype`](skills/prototype/SKILL.md) [`/architect`](skills/architect/SKILL.md) | 決める | 計画、画面、用語、セッションをまたぐ地図、切り分け、試作、境界。 |
| [`/implement`](skills/implement/SKILL.md) [`/hunt`](skills/hunt/SKILL.md) [`/optimize`](skills/optimize/SKILL.md) | 作る | 承認済みの作業、根本原因、指標は一度に一つ。 |
| [`/check`](skills/check/SKILL.md) [`/triage`](skills/triage/SKILL.md) [`/verify`](skills/verify/SKILL.md) | 渡す | マージ、push、リリース前の確認、課題の整理、検証の説明。 |
| [`/read`](skills/read/SKILL.md) [`/learn`](skills/learn/SKILL.md) [`/write`](skills/write/SKILL.md) | 読む・書く | 一つの URL か PDF、複数資料の調査、文章を整える。 |
| [`/handoff`](skills/handoff/SKILL.md) [`/retro`](skills/retro/SKILL.md) [`/health`](skills/health/SKILL.md) [`/wizard`](skills/wizard/SKILL.md) | 次も使える | セッションの引き継ぎ、確認済みの教訓、エージェント設定、手動セットアップ。 |

迷ったら `/f-help この作業にはどのスキルが合う？`（Codex: `$f-help`、プラグイン: `/fskill:f-help`）。

`/f-mode`（Codex: `$f-mode`、プラグイン: `/fskill:f-mode`）で開始し、通常の言葉で依頼できます。現在の会話で `/f-mode off` まで自動選択が続きます。`/f-mode status` で状態を確認。直接コマンドを優先し、f-mode は維持します。新しい会話では無効です。操作の権限は変わりません。

## インストール

**Claude Code、Codex、Cursor、その他のエージェント**

```bash
npx skills add gofenix/fskill -a claude-code codex cursor -g -y
```

スキルは共通の `~/.agents/skills` ディレクトリに保存されます。Claude Code はシンボリックリンク経由で連携し、Codex、Cursor、Gemini CLI、Copilot、Amp、Kimi Code CLI など、このディレクトリを読み込む各エージェントは 24 個のスキルを読み込みます。各スキルの手順は `/name` または `$name` のときだけ始まります。専用ディレクトリを持つエージェントは `-a` の後にID（例：`antigravity-cli`、`qwen-code`）を指定してください。更新は `npx skills update -g -y` で行います。AIエージェントに直接インストールを依頼することも可能です：
> https://github.com/gofenix/fskill/blob/main/llms.txt を読んで fskill をインストールして

**ホストのプラグイン機能を利用する場合**（スキル名に名前空間が付きます：`/fskill:check`）：

```bash
# Claude Code（更新：claude plugin update fskill）
/plugin marketplace add gofenix/fskill
/plugin install fskill@fskill

# Codex（更新：codex plugin marketplace upgrade fskill、その後 codex plugin add fskill@fskill）
codex plugin marketplace add gofenix/fskill
codex plugin add fskill@fskill
```

**Claude Desktop**：[fskill.zip](https://github.com/gofenix/fskill/releases/latest/download/fskill.zip) をダウンロードし、Customize > Skills > "+" > Create skill からZIPをアップロードします。更新時はカードの "..." から Replace を選択し、最新のZIPを再度アップロードしてください。

**Pi**：`pi install npm:@gofenix/fskill`、更新は `pi update npm:@gofenix/fskill` で行います。

## スキルの連携

順番は自分で決めます。各スキルは自分の結果を出したら止まります。次は `/name` または `$name` で呼び出します。

**一般的なワークフロー：**

- **新機能の開発**：`/think` で設計を固め、承認後に実装し、`/check` でレビューしてマージ
- **不具合の修正**：`/hunt` で原因を特定し、修正してから `/check` で変更差分をレビューし、必要に応じてリリース
- **調査と執筆**：`/read` で資料を集め、`/learn` で体系化し、`/write` で文章を磨く

## プロジェクトコンテキスト

fskill は汎用的なエンジニアリングの型のみを提供します。`/check` は実行時に対象リポジトリの公開情報（README、パッケージ定義、Makefile、CI設定）とタスク要件を読み取り、非公開のパスや認証情報、トークンは読みません。レビュー用コンテキストのテンプレートは [`skills/check/references/project-context.md`](skills/check/references/project-context.md) を参照してください。

## 追加ツールとルール

curl の URL は最新の GitHub リリースアセットを使います。main の最新スクリプトを使いたい場合は、コマンドの前に `FSKILL_REF=main` を指定してください。

### ステータスライン

Claude Code 向けのミニマルなステータスライン：コンテキストウィンドウ、5時間制限、7日間制限の使用率を色分け表示し、プログレスバーや余計なノイズはありません。

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/statusline.png" width="1000" />
</div>

```bash
(
  set -e
  FSKILL_STATUSLINE_SCRIPT="$(mktemp -t fskill-statusline.XXXXXX)"
  trap 'rm -f "$FSKILL_STATUSLINE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-statusline.sh -o "$FSKILL_STATUSLINE_SCRIPT"
  # 実行前に内容を確認：less "$FSKILL_STATUSLINE_SCRIPT"
  bash "$FSKILL_STATUSLINE_SCRIPT"
)
```

**Codex** は標準でステータスライン表示に対応しています。`~/.codex/config.toml` に追加してください：

```toml
[tui]
status_line = ["model-with-reasoning", "current-dir", "context-used", "five-hour-limit", "weekly-limit"]
status_line_use_colors = true
```

Codex は残りの枠を、上の Claude Code ステータスラインは使用済みの割合を表示します（上流がまだ `five-hour-used` / `weekly-used` を提供していないため）。

### オプションルール

オプションルールは、エージェントの永続的な指示にインストールすると、スキルを呼び出していないときにも適用されます。fskill のスキルをインストールするだけでは有効になりません。必要なものをコピーして実行してください（Codex や Antigravity では `claude-code` を `codex` または `antigravity-cli` に置き換えます）：

```bash
(
  set -e
  FSKILL_RULE_SCRIPT="$(mktemp -t fskill-rule.XXXXXX)"
  trap 'rm -f "$FSKILL_RULE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-rule.sh -o "$FSKILL_RULE_SCRIPT"
  # 実行前に内容を確認：less "$FSKILL_RULE_SCRIPT"

  # 英語コーチング：プロンプトに英語の誤りがあると、末尾に短い 😇 の訂正を追加
  bash "$FSKILL_RULE_SCRIPT" english claude-code

  # アンチパターン：スキル横断で常に効くガードレール（読んでから動く、範囲を広げない、頼まれていない要約をしない）
  bash "$FSKILL_RULE_SCRIPT" anti-patterns claude-code

  # ルーティングヒント：スキル名と、/name または $name のときだけ入るという規則
  bash "$FSKILL_RULE_SCRIPT" fskill-routing claude-code

  # 明快な日常回答：用語の統一、条件の明示、不確かさの保持
  # Clarity は main ブランチで利用でき、現行リリースにはまだ含まれていません
  FSKILL_REF=main bash "$FSKILL_RULE_SCRIPT" clarity claude-code
)
```

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/english-coaching.png" width="1000" />
</div>

[Clarity](rules/clarity.md) は ASD-STE100 のわかりやすい文章の原則を取り入れていますが、制限英語の文法を押し付けたり、あなたの文体を変えたりはしません。更新するにはコマンドを再実行し、新しいセッションを開始してください。Codex は `~/.codex/AGENTS.md` にマーク付きブロックを追加し、Claude Code と Antigravity はルールファイルをインストールします。ほかのツールでは、ルールを各ツールの永続的なカスタム指示にコピーしてください。

## 開発の背景

fskill は gofenix 自身のスキル集です。進め方は [tw93/Waza](https://github.com/tw93/Waza) から取り、名前は取りません。Waza は他人の名前だからです。作業スキルは 21 個で、決める、作る、渡す、読む・書く、次も使える、の五つに分かれます。その上に明示的な入口 `/f-mode` があります。各スキルは結果、越えない線、完了の判断だけを書きます。

入り方は明示です。`/name` または `$name`。近い意味ではその手順は始まりません。

## アンインストール

```bash
npx skills remove gofenix/fskill -g
rm -f ~/.claude/statusline.sh
rm -f ~/.claude/rules/english.md
rm -f ~/.claude/rules/anti-patterns.md
rm -f ~/.claude/rules/fskill-routing.md
rm -f ~/.claude/rules/clarity.md
```

ステータスラインを導入していた場合は、`~/.claude/settings.json` から `statusLine` エントリも削除してください。Claude Desktop では Customize > Skills から fskill を削除してください。Codex にルールをインストールした場合は、`~/.codex/AGENTS.md` から fskill のマーク付きブロックを削除してください。Antigravity では `~/.gemini/antigravity-cli/rules/` から該当するルールファイルを削除してください。ほかのツールにコピーしたルールは、各ツールのカスタム指示から削除してください。ルールを削除したら新しいセッションを開始してください。

## サポート

役に立ったら、リポジトリに Star を付けるか Issue を開いてください。

## ライセンス

MIT。UI の参考資料には Apache-2.0 の内容を含みます。[Waza](https://github.com/tw93/Waza)、[Matt Pocock skills](https://github.com/mattpocock/skills)、[pstack](https://github.com/cursor/plugins/tree/main/pstack) に感謝します。UI の手法は [Impeccable](https://github.com/pbakaus/impeccable)、[taste-skill](https://github.com/Leonxlnx/taste-skill)、[apple-design](https://github.com/emilkowalski/skills) も参考に翻訳・再構成しています。元の版、変更内容、完全なライセンスはルートの [LICENSE](LICENSE) で管理します。gofenix の記載は独自の追加と変更、元の作者の記載はそれぞれ再利用した内容に適用されます。
