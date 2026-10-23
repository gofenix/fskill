#!/usr/bin/env bash
# Copy this file and wizard_config.py into the same task directory.
# Author run_stages below. A human runs the resulting script in a terminal.
set -euo pipefail
set +x

WIZARD_RESOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIZARD_SKIPPED=()
WIZARD_UNVERIFIED=()
WIZARD_SECRET_READY=()
WIZARD_STAGE=0
TOTAL_STAGES=0

die() { printf '停止：%s\n' "$1" >&2; return 1; }
say() { printf '%s\n' "$1"; }
stage() {
  WIZARD_STAGE=$((WIZARD_STAGE + 1))
  printf '\n[%s/%s] %s\n' "$WIZARD_STAGE" "$TOTAL_STAGES" "$1"
}
pause() { read -r -p "${1:-完成后按 Enter：}" _; }
confirm() {
  local reply
  read -r -p "$1 [y/N] " reply || return 1
  [[ "$reply" == y || "$reply" == Y ]]
}
open_url() {
  say "请打开：$1"
  if command -v wslview >/dev/null 2>&1; then wslview "$1" >/dev/null 2>&1 || true
  elif command -v open >/dev/null 2>&1; then open "$1" >/dev/null 2>&1 || true
  elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$1" >/dev/null 2>&1 || true
  fi
}

init_project() {
  WIZARD_ROOT="$(cd "$1" && pwd -P)" || return 1
  local actual
  actual="$(git -C "$WIZARD_ROOT" rev-parse --show-toplevel)" || return 1
  [[ "$actual" == "$WIZARD_ROOT" ]] || { die "目标必须是项目 Git 根目录"; return 1; }
  WIZARD_GITHUB_REPO="${2:-}"
  if [[ -n "$WIZARD_GITHUB_REPO" && ! "$WIZARD_GITHUB_REPO" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
    die "GitHub repo 需要明确的 owner/repo"; return 1
  fi
  ENV_FILE="$WIZARD_ROOT/.env"
  say "目标目录：$WIZARD_ROOT"
  [[ -z "$WIZARD_GITHUB_REPO" ]] || say "GitHub repo：$WIZARD_GITHUB_REPO"
}

_input_key() {
  [[ "$1" =~ ^[A-Z][A-Z0-9_]*$ ]] || { die "采集字段需要大写环境变量名"; return 1; }
  case "$1" in
    HOME|PATH|SHELL|PWD|OLDPWD|IFS|ENV_FILE|BASH*|WIZARD_*|TOTAL_STAGES)
      die "采集字段不能覆盖运行时变量"; return 1 ;;
  esac
}

_ask() {
  local key="$1" prompt="$2" secret="$3" current input
  _input_key "$key" || return 1
  current="$(python3 "$WIZARD_RESOURCE_DIR/wizard_config.py" get "$ENV_FILE" "$key")" || return 1
  [[ -z "$current" ]] || prompt="${prompt}（Enter 保留已有值）"
  printf '%s：' "$prompt"
  if [[ "$secret" == yes ]]; then
    read -r -s input || { printf '\n'; return 1; }
    printf '\n'
  else
    read -r input || return 1
  fi
  [[ -n "$input" ]] || input="$current"
  [[ -n "$input" ]] || { die "必填值尚未提供"; return 1; }
  printf -v "$key" '%s' "$input"
}
ask() { _ask "$1" "$2" no; }
ask_secret() { _ask "$1" "$2" yes; }
write_env() {
  _input_key "$1" || return 1
  printf '%s' "$2" | python3 "$WIZARD_RESOURCE_DIR/wizard_config.py" upsert "$ENV_FILE" "$1" || return 1
  say "本地写入并回读：$1"
}

_github_target() {
  [[ -n "$WIZARD_GITHUB_REPO" ]] || { die "外部写入前需要明确 owner/repo"; return 1; }
  local actual
  actual="$(cd "$WIZARD_ROOT" && gh repo view --json nameWithOwner --jq .nameWithOwner)" || return 1
  [[ "$actual" == "$WIZARD_GITHUB_REPO" ]] || die "当前项目 remote 与目标 GitHub repo 不一致"
}

set_secret() {
  local name="$1" value="$2" names item write_status=0
  local ready=() pending=()
  _input_key "$name" || return 1
  # A new attempt invalidates evidence from an earlier write of this key.
  for item in ${WIZARD_SECRET_READY[@]+"${WIZARD_SECRET_READY[@]}"}; do
    [[ "$item" == "$name" ]] || ready+=("$item")
  done
  WIZARD_SECRET_READY=(${ready[@]+"${ready[@]}"})
  for item in ${WIZARD_UNVERIFIED[@]+"${WIZARD_UNVERIFIED[@]}"}; do
    [[ "$item" == "GitHub secret ${name}："* ]] || pending+=("$item")
  done
  WIZARD_UNVERIFIED=(${pending[@]+"${pending[@]}"})
  if ! command -v gh >/dev/null 2>&1; then
    WIZARD_SKIPPED+=("GitHub secret ${name}：缺少 gh")
    return 2
  fi
  if ! _github_target; then
    WIZARD_SKIPPED+=("GitHub secret ${name}：目标仓库校验失败")
    return 2
  fi
  printf '%s' "$value" | gh secret set "$name" --repo "$WIZARD_GITHUB_REPO" >/dev/null 2>&1 || write_status=$?
  names="$(gh secret list --repo "$WIZARD_GITHUB_REPO" --json name --jq '.[].name')" || {
    WIZARD_SKIPPED+=("GitHub secret ${name}：写入已尝试，名称回读失败，结果未知")
    return 2
  }
  if (( write_status )); then
    WIZARD_SKIPPED+=("GitHub secret ${name}：写入请求异常，已回读名称清单但新值仍未知")
    return 2
  fi
  if ! printf '%s\n' "$names" | grep -Fxq "$name"; then
    WIZARD_SKIPPED+=("GitHub secret ${name}：写入请求成功，未回读到名称")
    return 2
  fi
  say "GitHub secret 写入请求成功，名称已回读：$name"
  WIZARD_SECRET_READY+=("$name")
  WIZARD_UNVERIFIED+=("GitHub secret ${name}：名称存在不证明值正确，需运行消费端验证")
}

set_var() {
  local name="$1" value="$2" observed write_status=0
  _input_key "$name" || return 1
  if ! command -v gh >/dev/null 2>&1; then
    WIZARD_SKIPPED+=("GitHub variable ${name}：缺少 gh")
    return 2
  fi
  if ! _github_target; then
    WIZARD_SKIPPED+=("GitHub variable ${name}：目标仓库校验失败")
    return 2
  fi
  gh variable set "$name" --repo "$WIZARD_GITHUB_REPO" --body "$value" >/dev/null 2>&1 || write_status=$?
  observed="$(gh variable get "$name" --repo "$WIZARD_GITHUB_REPO" --json value --jq .value)" || {
    WIZARD_SKIPPED+=("GitHub variable ${name}：回读失败")
    return 2
  }
  if [[ "$observed" != "$value" ]]; then
    WIZARD_SKIPPED+=("GitHub variable ${name}：回读值不一致")
    return 2
  fi
  if (( write_status )); then say "GitHub variable 请求异常，但实际回读已匹配：$name"; fi
  say "GitHub variable 写入并回读：$name"
}

# The authored verifier must exercise the actual consumer, not just list names.
# Credentials belong in its environment/stdin; command arguments are non-secret.
verify_secret() {
  local name="$1" item secret_ready=no
  local remaining=()
  shift
  _input_key "$name" || return 1
  [[ $# -gt 0 ]] || { die "消费端验证需要明确命令"; return 1; }
  for item in ${WIZARD_SECRET_READY[@]+"${WIZARD_SECRET_READY[@]}"}; do
    [[ "$item" != "$name" ]] || secret_ready=yes
  done
  if [[ "$secret_ready" != yes ]]; then
    WIZARD_SKIPPED+=("GitHub secret ${name}：本次写入请求及名称回读尚未成功，未运行消费端验证")
    return 2
  fi
  if ! "$@" >/dev/null 2>&1; then
    WIZARD_SKIPPED+=("GitHub secret ${name}：消费端验证失败")
    return 2
  fi
  for item in ${WIZARD_UNVERIFIED[@]+"${WIZARD_UNVERIFIED[@]}"}; do
    [[ "$item" == "GitHub secret ${name}："* ]] || remaining+=("$item")
  done
  WIZARD_UNVERIFIED=(${remaining[@]+"${remaining[@]}"})
  say "消费端验证通过：$name"
}

finish() {
  local item
  if (( ${#WIZARD_SKIPPED[@]} || ${#WIZARD_UNVERIFIED[@]} )); then
    say '流程仍有未完成项：'
    for item in ${WIZARD_SKIPPED[@]+"${WIZARD_SKIPPED[@]}"} ${WIZARD_UNVERIFIED[@]+"${WIZARD_UNVERIFIED[@]}"}; do
      say "- $item"
    done
    return 2
  fi
  say '已完成本向导列出的写入及回读；消费端可用性以阶段中的实际验证为准。'
}

# STAGES: author only the manual procedure needed for this task.
run_stages() {
  # Set TOTAL_STAGES, then use stage / open_url / ask_secret / write_env.
  # Add precise confirm gates before irreversible operations.
  # Add task-specific consumer checks; do not put credentials in argv.
  # Chain consumer-dependent work after set_secret AND verify_secret succeed.
  # Use an explicit if/else to continue unrelated work, then always call finish.
  die '模板尚未填写人工操作阶段'
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  [[ $# -ge 1 && $# -le 2 ]] || { say "用法：bash $0 <project-root> [owner/repo]"; exit 1; }
  init_project "$@"
  run_stages
  finish
fi
