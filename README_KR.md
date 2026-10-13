<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/logo.svg" width="120" />
  <h1>fskill</h1>
  <p><b>gofenix의 엔지니어링 습관을 당신의 스킬로</b></p>
  <p><a href="README.md">English</a> · <a href="README_CN.md">中文</a> · <a href="README_TW.md">繁體</a> · <a href="README_JA.md">日本語</a> · 한국어 · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a></p>
  <a href="https://github.com/gofenix/fskill/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/gofenix/fskill/test.yml?branch=main&style=flat-square&label=tests" alt="Tests"></a>
  <a href="https://github.com/gofenix/fskill/stargazers"><img src="https://img.shields.io/github/stars/gofenix/fskill?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/gofenix/fskill/releases"><img src="https://img.shields.io/github/v/tag/gofenix/fskill?label=version&style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://twitter.com/Higofenix"><img src="https://img.shields.io/badge/follow-gofenix-red?style=flat-square&logo=Twitter" alt="Twitter"></a>
</div>

<br/>

## 스킬 목록

각 스킬은 참고 문서, 스크립트, 실제로 겪은 실패를 담은 디렉터리입니다. 기본적으로 `/name` 또는 `$name` 으로 시작합니다. 비슷한 말로는 바뀌지 않습니다. 틀은 [tw93/Waza](https://github.com/tw93/Waza) 에서 왔고, 이름과 본문은 자신의 것입니다.

| 스킬 | 묶음 | 역할 |
| :--- | :--- | :--- |
| [`/mode`](skills/mode/SKILL.md) | 경로 | 명시적으로 들어온 뒤 아래 스킬 중 하나를 고른다. 개별 명령도 그대로 쓸 수 있다. |
| [`/think`](skills/think/SKILL.md) [`/ui`](skills/ui/SKILL.md) [`/domain`](skills/domain/SKILL.md) [`/map`](skills/map/SKILL.md) [`/slice`](skills/slice/SKILL.md) [`/prototype`](skills/prototype/SKILL.md) [`/architect`](skills/architect/SKILL.md) | 정하기 | 계획, 화면, 용어, 세션을 넘는 지도, 쪼개기, 시험, 경계. |
| [`/implement`](skills/implement/SKILL.md) [`/hunt`](skills/hunt/SKILL.md) [`/optimize`](skills/optimize/SKILL.md) | 만들기 | 승인된 작업, 근본 원인, 지표는 한 번에 하나. |
| [`/check`](skills/check/SKILL.md) [`/triage`](skills/triage/SKILL.md) [`/verify`](skills/verify/SKILL.md) | 넘기기 | 머지, push, 릴리스 전 검토, 이슈 정리, 검증 설명. |
| [`/read`](skills/read/SKILL.md) [`/learn`](skills/learn/SKILL.md) [`/write`](skills/write/SKILL.md) | 읽고 쓰기 | URL 또는 PDF 하나, 여러 자료 조사, 문장 다듬기. |
| [`/handoff`](skills/handoff/SKILL.md) [`/retro`](skills/retro/SKILL.md) [`/health`](skills/health/SKILL.md) [`/wizard`](skills/wizard/SKILL.md) | 다음에 쓰기 | 세션 인수인계, 확인된 교훈, 에이전트 설정, 수동 설치. |

`/mode`(Codex: `$mode`, 플러그인: `/fskill:mode`)로 시작한 뒤 평소처럼 요청하세요. 현재 대화에서 `/mode off`까지 자동 선택합니다. `/mode status`로 상태를 확인합니다. 직접 명령을 우선하며 mode는 유지됩니다. 새 대화에서는 꺼져 있습니다. 작업 권한은 바뀌지 않습니다.

## 설치 방법

**Claude Code, Codex, Cursor 및 기타 에이전트**

```bash
npx skills add gofenix/fskill -a claude-code codex cursor -g -y
```

스킬은 공유 디렉터리인 `~/.agents/skills`에 저장됩니다. Claude Code는 심볼릭 링크로 연결되며, Codex, Cursor, Gemini CLI, Copilot, Amp, Kimi Code CLI 등 해당 디렉터리를 읽는 에이전트는 21개 스킬을 읽습니다. 각 스킬의 절차는 `/name` 또는 `$name` 일 때만 시작합니다. 독립 디렉터리를 사용하는 에이전트는 `-a` 뒤에 ID(예: `antigravity-cli`, `qwen-code`)를 지정하세요. 업데이트는 `npx skills update -g -y`로 실행합니다. AI 에이전트에게 직접 설치를 요청할 수도 있습니다:
> 다음 문서를 읽고 fskill를 설치해 줘: https://github.com/gofenix/fskill/blob/main/llms.txt

**호스트 플러그인 방식** (네임스페이스 포함: `/fskill:check`):

```bash
# Claude Code (업데이트: claude plugin update fskill)
/plugin marketplace add gofenix/fskill
/plugin install fskill@fskill

# Codex (업데이트: codex plugin marketplace upgrade fskill 후 codex plugin add fskill@fskill)
codex plugin marketplace add gofenix/fskill
codex plugin add fskill@fskill
```

**Claude Desktop**: [fskill.zip](https://github.com/gofenix/fskill/releases/latest/download/fskill.zip)을 다운로드한 뒤 Customize > Skills > "+" > Create skill에서 업로드합니다. 업데이트할 때는 카드에서 "..." > Replace를 선택해 최신 ZIP을 다시 업로드하세요.

**Pi**: `pi install npm:@gofenix/fskill`, 업데이트는 `pi update npm:@gofenix/fskill`로 실행합니다.

## 스킬 연계 워크플로우

mode 밖에서는 순서를 직접 정합니다. 각 스킬은 자기 결과를 내면 멈춥니다. 다음은 `/name` 또는 `$name` 으로 호출합니다.

**자주 쓰이는 워크플로우:**

- **새 기능 구현**: `/think`로 설계를 검증하고, 승인 후 구현한 뒤 `/check`로 최종 검토하고 머지
- **버그 해결**: `/hunt`로 원인을 규명하고, 수정한 뒤 `/check`로 변경 사항을 검토하고 필요하면 배포
- **리서치 및 작성**: `/read`로 자료를 모으고, `/learn`으로 체계화한 뒤 `/write`로 문장 다듬기

## 프로젝트 컨텍스트

fskill는 범용적인 엔지니어링 습관만을 제공합니다. `/check`는 런타임에 대상 저장소의 공개 정보(README, 패키지 파일, Makefile, CI 설정)와 작업 조건만을 읽으며, 비공개 경로나 자격 증명, 토큰에는 접근하지 않습니다. 리뷰 컨텍스트 템플릿은 [`skills/check/references/project-context.md`](skills/check/references/project-context.md)를 참고하세요.

## 추가 도구 및 규칙

curl URL은 최신 GitHub 릴리스 자산을 사용합니다. main의 최신 스크립트를 쓰려면 명령 앞에 `FSKILL_REF=main`을 지정하세요.

### 상태 표시줄

Claude Code용 미니멀 상태 표시줄: 컨텍스트 윈도우, 5시간 한도, 7일 한도를 사용량에 따라 색으로 표시하며, 진행 막대나 군더더기는 없습니다.

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/statusline.png" width="1000" />
</div>

```bash
(
  set -e
  FSKILL_STATUSLINE_SCRIPT="$(mktemp -t fskill-statusline.XXXXXX)"
  trap 'rm -f "$FSKILL_STATUSLINE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-statusline.sh -o "$FSKILL_STATUSLINE_SCRIPT"
  # 실행 전에 내용을 먼저 확인하세요: less "$FSKILL_STATUSLINE_SCRIPT"
  bash "$FSKILL_STATUSLINE_SCRIPT"
)
```

**Codex** 설정 (`~/.codex/config.toml`):

```toml
[tui]
status_line = ["model-with-reasoning", "current-dir", "context-used", "five-hour-limit", "weekly-limit"]
status_line_use_colors = true
```

Codex는 남은 한도를, 위의 Claude Code 상태 표시줄은 사용한 비율을 표시합니다(업스트림에서 아직 `five-hour-used` / `weekly-used`를 제공하지 않음).

### 선택적 규칙

선택적 규칙은 에이전트의 영구 지침에 설치하면 스킬을 호출하지 않을 때도 적용됩니다. fskill 스킬만 설치해서는 활성화되지 않습니다. 필요한 규칙을 복사해 실행하세요(Codex나 Antigravity에서는 `claude-code`를 `codex` 또는 `antigravity-cli`로 바꾸세요):

```bash
(
  set -e
  FSKILL_RULE_SCRIPT="$(mktemp -t fskill-rule.XXXXXX)"
  trap 'rm -f "$FSKILL_RULE_SCRIPT"' EXIT
  curl -fL https://github.com/gofenix/fskill/releases/latest/download/setup-rule.sh -o "$FSKILL_RULE_SCRIPT"
  # 실행 전에 내용을 먼저 확인하세요: less "$FSKILL_RULE_SCRIPT"

  # 영어 코칭: 프롬프트에 영어 실수가 있으면 끝에 짧은 😇 교정을 덧붙임
  bash "$FSKILL_RULE_SCRIPT" english claude-code

  # 안티패턴: 모든 스킬에 항상 적용되는 가드레일 (먼저 읽고 행동, 범위 확장 금지, 요청하지 않은 요약 금지)
  bash "$FSKILL_RULE_SCRIPT" anti-patterns claude-code

  # 라우팅 힌트: 스킬 이름, 그리고 /name 또는 $name 으로만 들어간다는 규칙
  bash "$FSKILL_RULE_SCRIPT" fskill-routing claude-code

  # 명확한 일상 답변: 일관된 용어, 명시적인 조건, 불확실성 유지
  # Clarity는 main 브랜치에서 사용할 수 있으며 아직 정식 릴리스에는 포함되지 않았습니다
  FSKILL_REF=main bash "$FSKILL_RULE_SCRIPT" clarity claude-code
)
```

<div align="center">
  <img src="https://raw.githubusercontent.com/gofenix/fskill/main/assets/english-coaching.png" width="1000" />
</div>

[Clarity](rules/clarity.md)는 ASD-STE100의 명확한 글쓰기 원칙을 가져오지만, 통제 영어 문법을 강요하거나 문체를 바꾸지는 않습니다. 명령을 다시 실행하면 설치된 규칙이 업데이트되며, 그 뒤 새 세션을 시작하세요. Codex는 `~/.codex/AGENTS.md`에 표시된 블록을 추가하고, Claude Code와 Antigravity는 규칙 파일을 설치합니다. 다른 도구에서는 규칙을 해당 도구의 영구 사용자 지정 지침에 복사하세요.

## fskill를 만든 이유

fskill 은 gofenix 자신의 스킬 모음입니다. 일하는 방식은 [tw93/Waza](https://github.com/tw93/Waza) 에서 가져왔고, 이름은 가져오지 않았습니다. Waza 는 다른 사람의 이름입니다. 스킬은 20개이며, 정하기, 만들기, 넘기기, 읽고 쓰기, 다음에 쓰기로 나뉩니다. 그 위에 명시적 입구 `/mode` 가 있습니다. 각 스킬은 결과, 넘지 않을 선, 완료 기준만 적습니다.

호출은 명시적입니다. `/name` 또는 `$name`. 비슷한 뜻으로는 그 절차가 시작되지 않습니다.

## 삭제 방법

```bash
npx skills remove gofenix/fskill -g
rm -f ~/.claude/statusline.sh
rm -f ~/.claude/rules/english.md
rm -f ~/.claude/rules/anti-patterns.md
rm -f ~/.claude/rules/fskill-routing.md
rm -f ~/.claude/rules/clarity.md
```

상태 표시줄을 설치했다면 `~/.claude/settings.json`에서 `statusLine` 항목도 삭제하세요. Claude Desktop에서는 Customize > Skills에서 fskill를 삭제하세요. Codex에 규칙을 설치했다면 `~/.codex/AGENTS.md`에서 fskill 표시 블록을 제거하세요. Antigravity에서는 `~/.gemini/antigravity-cli/rules/`에서 선택한 규칙 파일을 삭제하세요. 다른 도구에 복사한 규칙은 해당 도구의 사용자 지정 지침에서 제거하세요. 규칙을 제거한 뒤에는 새 세션을 시작하세요.

## 후원 안내

도움이 되었다면 저장소에 Star 를 누르거나 Issue 를 열어 주세요.

## 라이선스

MIT License. Please feel free to use and contribute to the development.
