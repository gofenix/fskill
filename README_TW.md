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

fskill 採用 **9 個精簡工作流 + 8 條 `pstack` 風格工程原則 + 確定性腳本**。全部 9 條技能均僅在顯式呼叫（`/name`、`$name`）或進入 `/f-mode` 後執行，不會自動啟用。以 [Waza](https://github.com/tw93/Waza) 為基礎，融合 [Matt Pocock skills](https://github.com/mattpocock/skills) 與 [pstack](https://github.com/cursor/plugins/tree/main/pstack) 的原則化設計；完整來源見下方授權說明。

| 技能 | 分組 | 它做什麼 |
| :--- | :--- | :--- |
| [`/f-mode`](skills/f-mode/SKILL.md) | 路由 | 顯式開啟，依目標在目前會話選用工作流並參考工程原則。 |
| [`/think`](skills/think/SKILL.md) | 想清楚 | 動手前方案規劃、價值判斷（放棄/保留/轉向）、範圍分類與 `grill me` 壓測。 |
| [`/hunt`](skills/hunt/SKILL.md) | 找問題 | 用執行期證據查實根因；指標已定時單假設對照驗證。 |
| [`/check`](skills/check/SKILL.md) | 做檢查 | 審 diff/PR、發版價值判斷、發布產物門禁、專案審計與事故重放。 |
| [`/ui`](skills/ui/SKILL.md) | 介面 | 做出有方向感、反 AI slop 的介面，依真實算繪與截圖驗收。 |
| [`/learn`](skills/learn/SKILL.md) [`/write`](skills/write/SKILL.md) | 讀和寫 | 抓取 URL/PDF 與一手調研；去掉中英文與發布說明 AI 味。 |
| [`/handoff`](skills/handoff/SKILL.md) [`/health`](skills/health/SKILL.md) | 下次還能用 | 會話交接與現況核對；Agent 設定/hooks/MCP/省 token 工具體檢與規則瘦身。 |

**8 條工程原則（[`rules/principles.md`](rules/principles.md)，同步內嵌於 [`f-mode`](skills/f-mode/references/principles.md)）：** 先減後增 · 質疑前提 · 先證根因 · 真實驗收 · 行為測試 · 解釋數字 · 結構防復發 · 邊界與單向門

輸入 `/f-mode`（Codex 用 `$f-mode`，外掛用 `/fskill:f-mode`）進入，再直接描述任務；目前會話內持續自動選技能。`/f-mode off` 退出，`/f-mode status` 查看狀態。直接 `/hunt` 等命令優先，不關閉 f-mode。新會話預設關閉；選路不擴大操作授權。完整路由見 [skills/RESOLVER.md](skills/RESOLVER.md)。

## 安裝

**Claude Code、Codex、Cursor 與其他 Agent**

```bash
npx skills add gofenix/fskill -a claude-code codex cursor -g -y
```

技能統一存放在 `~/.agents/skills` 共享目錄，Claude Code 透過符號連結接入，Codex、Cursor、Gemini CLI、Copilot、Amp、Kimi Code CLI 以及其他能讀這個目錄的 Agent 都會讀到這 9 個工作流。全部 9 個工作流均僅在 `/ui`、`$ui` 等明確點名或 `/f-mode` 內進入。有自己技能目錄的 Agent 在 `-a` 後面寫上它的 ID，比如 `antigravity-cli` 或 `qwen-code`，後續透過 `npx skills update -g -y` 保持更新。也可以直接告訴你的 Agent 幫你安裝：
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

- **做新功能**：`/think` 用先減後增收斂方案，確認後由目前的 Agent 動手，再用 `/check` 把關。
- **排查修復**：`/hunt` 拿執行期證據查實根因並做最小修復，再用 `/check` 審查改動與發布證據。
- **研究成文**：`/learn` 讀取材料或整理多來源，`/write` 潤色文字。

## 專案上下文

fskill 只沉澱通用的工程原則與工具，`/check` 執行時從目標儲存庫公開的 README、套件清單、Makefile、CI 設定和你的任務要求裡提煉約束，絕不讀取私有路徑、憑證或 Token；常見審查陷阱與發布門禁見 [`skills/check/references/review-patterns.md`](skills/check/references/review-patterns.md) 與 [`skills/check/references/release-artifacts.md`](skills/check/references/release-artifacts.md)。

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

  # 技能路由提示：全部 9 條技能均僅限顯式呼叫，或進入 /f-mode 後按目標選技能
  bash "$FSKILL_RULE_SCRIPT" fskill-routing claude-code

  # 工程原則：8 條 pstack 風格工程不變量（不單獨建技能目錄）
  # Principles 規則目前在 main 分支可用，尚未進入正式版
  FSKILL_REF=main bash "$FSKILL_RULE_SCRIPT" principles claude-code

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

fskill 是 gofenix 自己的技能集，結合 [tw93/Waza](https://github.com/tw93/Waza) 的工具腳本與 [pstack](https://github.com/cursor/plugins/tree/main/pstack) 的原則化設計，保留 **9 個精簡工作流**（`f-mode`、`think`、`hunt`、`check`、`ui`、`learn`、`write`、`handoff`、`health`）、沉澱於 [`rules/principles.md`](rules/principles.md) 的 **8 條短工程原則**與確定性檢查腳本。

全部 9 條技能都只在顯式呼叫（`/name` 或 `$name`）或 `/f-mode` 內開始，不會自動啟用。

## 移除

```bash
npx skills remove gofenix/fskill -g
rm -f ~/.claude/statusline.sh
rm -f ~/.claude/rules/english.md
rm -f ~/.claude/rules/anti-patterns.md
rm -f ~/.claude/rules/fskill-routing.md
rm -f ~/.claude/rules/principles.md
rm -f ~/.claude/rules/clarity.md
```

狀態列還需從 `~/.claude/settings.json` 刪掉 `statusLine` 條目，Claude Desktop 直接在 Customize > Skills 中刪除 fskill，裝過 Codex 規則的，從 `~/.codex/AGENTS.md` 刪掉對應的 fskill 標記塊，Antigravity 從 `~/.gemini/antigravity-cli/rules/` 刪除對應規則檔案，其他工具從自訂指令中移除即可，移除後開啟新會話生效。

## 支持

如果 fskill 有用，給倉庫點個 Star，或者開一個 Issue。

## 授權條款

MIT 授權，UI 參考含 Apache-2.0 材料。感謝 [Waza](https://github.com/tw93/Waza)、[Matt Pocock skills](https://github.com/mattpocock/skills)、[pstack](https://github.com/cursor/plugins/tree/main/pstack)。UI 方法亦改寫自 [Impeccable](https://github.com/pbakaus/impeccable)、[taste-skill](https://github.com/Leonxlnx/taste-skill) 與 [apple-design](https://github.com/emilkowalski/skills)。來源版本、改寫說明與完整授權統一維護於根目錄 [LICENSE](LICENSE)。gofenix 的署名適用於原創新增與修改，上游署名適用於各自沿用的材料。
