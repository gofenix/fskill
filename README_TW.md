<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/logo.svg" width="120" />
  <h1>fskill</h1>
  <p><b>把 gofenix 的工程習慣，變成你的技能</b></p>
  <p><a href="README.md">English</a> · <a href="README_CN.md">中文</a> · 繁體 · <a href="README_JA.md">日本語</a> · <a href="README_KR.md">한국어</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a></p>
  <a href="https://github.com/gofenix/fskill/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/gofenix/fskill/test.yml?branch=main&style=flat-square&label=tests" alt="Tests"></a>
  <a href="https://github.com/gofenix/fskill/stargazers"><img src="https://img.shields.io/github/stars/gofenix/fskill?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/gofenix/fskill/releases"><img src="https://img.shields.io/github/v/tag/gofenix/fskill?label=version&style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://twitter.com/Higofenix"><img src="https://img.shields.io/badge/follow-gofenix-red?style=flat-square&logo=Twitter" alt="Twitter"></a>
</div>

<br/>

## 技能

每個技能是一個目錄，裡面有參考、腳本和踩過的坑。預設透過 `/name` 或 `$name` 進入；說到相關的詞不會自動換技能。以 Waza 為基礎，並融合 Matt Pocock skills 和 pstack 的流程；完整來源見下方授權說明。

| 技能 | 分組 | 它做什麼 |
| :--- | :--- | :--- |
| [`/f-mode`](skills/f-mode/SKILL.md) | 路由 | 先顯式進入，再從下面的技能裡選一條。單條仍然可以直接用。 |
| [`/f-help`](skills/f-help/SKILL.md) | 幫助 | 了解 fskill 用法、選擇技能、排障與自訂。 |
| [`/catchup`](skills/catchup/SKILL.md) | 彙報 | 唯讀核對進展、變化與待你處理的事項。 |
| [`/sharpen`](skills/sharpen/SKILL.md) | 想清楚 | 校準方法、目標和約束，再直接完成已授權任務。 |
| [`/think`](skills/think/SKILL.md) [`/ui`](skills/ui/SKILL.md) [`/domain`](skills/domain/SKILL.md) [`/map`](skills/map/SKILL.md) [`/slice`](skills/slice/SKILL.md) [`/prototype`](skills/prototype/SKILL.md) [`/architect`](skills/architect/SKILL.md) | 想清楚 | 方案、介面、術語、跨會話地圖、切片、試驗、邊界。 |
| [`/implement`](skills/implement/SKILL.md) [`/hunt`](skills/hunt/SKILL.md) [`/optimize`](skills/optimize/SKILL.md) | 做出來 | 已批准的任務圖、根因、一次只動一個指標。 |
| [`/check`](skills/check/SKILL.md) [`/triage`](skills/triage/SKILL.md) [`/verify`](skills/verify/SKILL.md) | 交出去 | 合併、推送和發布前的審查，問題佇列，驗證說明。 |
| [`/read`](skills/read/SKILL.md) [`/learn`](skills/learn/SKILL.md) [`/write`](skills/write/SKILL.md) | 讀和寫 | 一個連結或 PDF、多來源研究、把文字改順。 |
| [`/handoff`](skills/handoff/SKILL.md) [`/retro`](skills/retro/SKILL.md) [`/health`](skills/health/SKILL.md) [`/wizard`](skills/wizard/SKILL.md) | 下次還能用 | 會話交接、已經驗證的教訓、Agent 設定、人工安裝。 |

不知道從哪開始？試試 `/f-help 我這個任務該用哪個技能？`（Codex 用 `$f-help`，外掛用 `/fskill:f-help`）。

輸入 `/f-mode`（Codex 用 `$f-mode`，外掛用 `/fskill:f-mode`）進入，再直接描述任務；目前會話內持續自動選技能。`/f-mode off` 退出，`/f-mode status` 查看狀態。直接 `/hunt` 等命令優先，不關閉 f-mode。新會話預設關閉；選路不擴大操作授權。

## 安裝

**Claude Code、Codex、Cursor 與其他 Agent**

```bash
npx skills add gofenix/fskill -a claude-code codex cursor -g -y
```

技能統一存放在 `~/.agents/skills` 共享目錄，Claude Code 透過符號連結接入，Codex、Cursor、Gemini CLI、Copilot、Amp、Kimi Code CLI 以及其他能讀這個目錄的 Agent 都會讀到這 24 個技能。進入某個技能的流程仍要顯式呼叫。有自己技能目錄的 Agent 在 `-a` 後面寫上它的 ID，比如 `antigravity-cli` 或 `qwen-code`，後續透過 `npx skills update -g -y` 保持更新。也可以直接告訴你的 Agent 幫你安裝：
> 閱讀 https://github.com/gofenix/fskill/blob/main/llms.txt 幫我安裝 fskill

**宿主外掛方式**，如果你更習慣使用宿主自有的更新指令（技能帶有命名空間前綴，如 `/fskill:check`）：

```bash
# Claude Code（更新指令：claude plugin update fskill）
/plugin marketplace add gofenix/fskill
/plugin install fskill@fskill

# Codex（更新指令：codex plugin marketplace upgrade fskill，然後 codex plugin add fskill@fskill）
codex plugin marketplace add gofenix/fskill
codex plugin add fskill@fskill
```

**Claude Desktop**：下載 [fskill.zip](https://github.com/gofenix/fskill/releases/latest/download/fskill.zip)，開啟 Customize > Skills > "+" > Create skill 並上傳壓縮檔，更新時點選卡片上的 "..." 選擇 Replace 再上傳最新的 ZIP 即可

**Pi**：`pi install npm:@gofenix/fskill`，透過 `pi update npm:@gofenix/fskill` 更新

## 技能串聯

順序由你決定。每個技能做完自己的結果就停下。下一步用 `/name` 或 `$name` 自己呼叫。

**常見工作流程：**

- **做新功能**：`/think` 想透方案，確認後動手實作，再用 `/check` 把關合併
- **排查修復**：`/hunt` 查清根因，動手修復，再用 `/check` 審查改動，需要時一併發布
- **研究成文**：`/read` 讀取素材，`/learn` 消化梳理，`/write` 潤色文字

## 專案上下文

fskill 只沉澱通用的工程習慣，`/check` 執行時從目標儲存庫公開的 README、套件清單、Makefile、CI 設定和你的任務要求裡提煉約束，絕不讀取私有路徑、憑證或 Token，具體上下文模板可參考 [`skills/check/references/project-context.md`](skills/check/references/project-context.md)。

## 附加工具與規則

下載腳本預設使用最新的 GitHub Release 資源，想用 main 上最新的腳本，可以在指令前加 `FSKILL_REF=main`。

### 狀態列

Claude Code 極簡狀態列：顯示上下文視窗、5 小時配額與 7 天配額，按用量著色，沒有進度條，沒有視覺噪音。

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/statusline.png" width="1000" />
</div>

```bash
(
  set -e
  FSKILL_STATUSLINE_SCRIPT="$(mktemp -t fskill-statusline.XXXXXX)"
  trap 'rm -f "$FSKILL_STATUSLINE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-statusline.sh -o "$FSKILL_STATUSLINE_SCRIPT"
  # 可以先檢查腳本內容：less "$FSKILL_STATUSLINE_SCRIPT"
  bash "$FSKILL_STATUSLINE_SCRIPT"
)
```

**Codex** 原生支援狀態列欄位，直接新增至 `~/.codex/config.toml`：

```toml
[tui]
status_line = ["model-with-reasoning", "current-dir", "context-used", "five-hour-limit", "weekly-limit"]
status_line_use_colors = true
```

Codex 顯示剩餘額度，上方 Claude Code 狀態列顯示已用百分比（上游暫未提供 `five-hour-used` / `weekly-used`）。

### 選用規則

選用規則用於補充技能之外的長期習慣，寫入 Agent 的持久化指令後生效，只安裝技能預設不會開啟，按需複製執行即可（在對應 Agent 上把 `claude-code` 換成 `codex` 或 `antigravity-cli`）：

```bash
(
  set -e
  FSKILL_RULE_SCRIPT="$(mktemp -t fskill-rule.XXXXXX)"
  trap 'rm -f "$FSKILL_RULE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-rule.sh -o "$FSKILL_RULE_SCRIPT"
  # 可以先檢查腳本內容：less "$FSKILL_RULE_SCRIPT"

  # 英文寫作教練：Prompt 中有英文表達錯誤時，在結尾追加一條簡短的 😇 糾錯建議
  bash "$FSKILL_RULE_SCRIPT" english claude-code

  # 行為防錯守則：全域常駐約束（先看再改、不隨意擴大範圍、不主動輸出冗餘總結）
  bash "$FSKILL_RULE_SCRIPT" anti-patterns claude-code

  # 技能路由提示：技能名單，以及只在 /name 或 $name 時進入
  bash "$FSKILL_RULE_SCRIPT" fskill-routing claude-code

  # 日常清晰表達：術語統一、條件明確、保留不確定性
  # Clarity 規則目前在 main 分支可用，尚未進入正式版
  FSKILL_REF=main bash "$FSKILL_RULE_SCRIPT" clarity claude-code
)
```

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/english-coaching.png" width="1000" />
</div>

[Clarity](rules/clarity.md) 借鑑了 ASD-STE100 的清晰寫作原則，不會強加受控英文語法，也不會改變你的個人表達風格，重新執行指令即可更新，開一個新會話後生效。Codex 會在 `~/.codex/AGENTS.md` 寫入標記塊，Claude Code 與 Antigravity 則安裝為規則檔案，其他工具把規則複製進各自的自訂指令即可

## 為什麼做 fskill

fskill 是 gofenix 自己的技能集。工作方式來自 [tw93/Waza](https://github.com/tw93/Waza)，名字不沿用，因為 Waza 是別人的。現在是 21 個工作技能，分成想清楚、做出來、交出去、讀和寫、下次還能用。上面再加一個顯式入口 `/f-mode`。每個技能寫清結果、不能碰的線，以及怎麼算做完。

呼叫是顯式的：`/name` 或 `$name`。意思相近不會自動開始那套流程。

## 移除

```bash
npx skills remove gofenix/fskill -g
rm -f ~/.claude/statusline.sh
rm -f ~/.claude/rules/english.md
rm -f ~/.claude/rules/anti-patterns.md
rm -f ~/.claude/rules/fskill-routing.md
rm -f ~/.claude/rules/clarity.md
```

狀態列還需從 `~/.claude/settings.json` 刪掉 `statusLine` 條目，Claude Desktop 直接在 Customize > Skills 中刪除 fskill，裝過 Codex 規則的，從 `~/.codex/AGENTS.md` 刪掉對應的 fskill 標記塊，Antigravity 從 `~/.gemini/antigravity-cli/rules/` 刪除對應規則檔案，其他工具從自訂指令中移除即可，移除後開啟新會話生效。

## 支持

如果 fskill 有用，給倉庫點個 Star，或者開一個 Issue。

## 授權條款

MIT 授權，UI 參考含 Apache-2.0 材料。感謝 [Waza](https://github.com/tw93/Waza)、[Matt Pocock skills](https://github.com/mattpocock/skills)、[pstack](https://github.com/cursor/plugins/tree/main/pstack)。UI 方法亦改寫自 [Impeccable](https://github.com/pbakaus/impeccable)、[taste-skill](https://github.com/Leonxlnx/taste-skill) 與 [apple-design](https://github.com/emilkowalski/skills)。來源版本、改寫說明與完整授權統一維護於根目錄 [LICENSE](LICENSE)，`make regenerate` 為每個技能產生相同的 `NOTICE.md`，供獨立安裝與 Multica 匯入。gofenix 的署名適用於原創新增與修改，上游署名適用於各自沿用的材料。
