#!/usr/bin/env bash
# Report whether rtk and codegraph are available outside the audited project.
# Presence only: this script does not install either tool or write an index.
set -euo pipefail

unset FSKILL_PYTHON DOC_REF_CHECKER GIT_INSTALL_ROOT BASH_ENV ENV
unset FSKILL_HEALTH_MODE FSKILL_HEALTH_DEEP
# A parent environment can export a function over the type builtin. Drop it
# before the first lookup so a startup hook cannot run during this report.
unset -f type || true

sanitize_health_path() {
  local target="$1"
  local entry physical safe=""
  local -a path_entries=()
  target=$(cd "$target" 2>/dev/null && pwd -P) || target=$(pwd -P)
  IFS=: read -r -a path_entries <<< "${PATH:-}"
  for entry in "${path_entries[@]}"; do
    [ -n "$entry" ] || continue
    case "$entry" in
      /*) ;;
      *) continue ;;
    esac
    [ -d "$entry" ] || continue
    physical=$(cd "$entry" 2>/dev/null && pwd -P) || continue
    case "$physical/" in
      "$target/"*) continue ;;
    esac
    safe="${safe:+$safe:}$physical"
  done
  printf '%s\n' "$safe"
}

canonical_health_executable() {
  local current="$1"
  local parent name link readlink_bin=""
  local depth=0
  case "$current" in
    /*) ;;
    *) return 1 ;;
  esac
  while [ "$depth" -lt 32 ]; do
    parent="${current%/*}"
    name="${current##*/}"
    [ -n "$parent" ] || parent="/"
    parent=$(cd "$parent" 2>/dev/null && pwd -P) || return 1
    if [ "$parent" = "/" ]; then
      current="/$name"
    else
      current="$parent/$name"
    fi
    if [ ! -L "$current" ]; then
      [ -f "$current" ] && [ -x "$current" ] || return 1
      printf '%s\n' "$current"
      return 0
    fi
    if [ -z "$readlink_bin" ]; then
      if [ -x /usr/bin/readlink ]; then
        readlink_bin=/usr/bin/readlink
      else
        readlink_bin=$(type -P readlink 2>/dev/null || true)
      fi
      [ -n "$readlink_bin" ] || return 1
    fi
    link=$("$readlink_bin" "$current") || return 1
    case "$link" in
      /*) current="$link" ;;
      *) current="$parent/$link" ;;
    esac
    depth=$((depth + 1))
  done
  return 1
}

HEALTH_TARGET=$(cd "${1:-$PWD}" 2>/dev/null && pwd -P) || HEALTH_TARGET=$(pwd -P)
HEALTH_HOME=$(cd "$HOME" 2>/dev/null && pwd -P) || HEALTH_HOME="$HOME"
PATH="$(sanitize_health_path "$HEALTH_TARGET")"
export PATH

safe_health_text() {
  printf '%s' "$1" | LC_ALL=C tr '\000-\037\177' '_'
  printf '\n'
}

display_path() {
  local path="$1" shown="$1"
  # Report a literal home abbreviation, not an expanded filesystem path.
  # shellcheck disable=SC2088
  case "$path" in
    "$HOME"/*) shown="~/${path#"$HOME"/}" ;;
    "$HEALTH_HOME"/*) shown="~/${path#"$HEALTH_HOME"/}" ;;
  esac
  safe_health_text "$shown"
}

resolve_on_path() {
  local name="$1" resolved=""
  while IFS= read -r resolved; do
    [ -n "$resolved" ] || continue
    resolved=$(canonical_health_executable "$resolved" 2>/dev/null || true)
    [ -n "$resolved" ] || continue
    case "$resolved/" in
      "$HEALTH_TARGET/"*) continue ;;
    esac
    printf '%s\n' "$resolved"
    return 0
  done < <(type -aP "$name" 2>/dev/null || true)
  return 1
}

resolve_candidate() {
  local candidate="$1" resolved=""
  [ -n "$candidate" ] || return 1
  case "$candidate" in
    /*) ;;
    *) return 1 ;;
  esac
  [ -x "$candidate" ] || return 1
  resolved=$(canonical_health_executable "$candidate" 2>/dev/null || true)
  [ -n "$resolved" ] || return 1
  case "$resolved/" in
    "$HEALTH_TARGET/"*) return 1 ;;
  esac
  printf '%s\n' "$resolved"
}

first_off_path() {
  local name="$1" candidate="" resolved=""
  shift
  for candidate in "$@"; do
    resolved=$(resolve_candidate "$candidate" 2>/dev/null || true)
    [ -n "$resolved" ] || continue
    case "$resolved" in
      */"$name") ;;
      *) continue ;;
    esac
    printf '%s\n' "$resolved"
    return 0
  done
  return 1
}

classify_index() {
  local text="$1"
  case "$text" in
    *"Not initialized"*) printf 'missing\n' ;;
    *"out of date"*|*"Index is stale"*|*"needs sync"*) printf 'stale\n' ;;
    *"up to date"*|*"Index Statistics"*) printf 'current\n' ;;
    *) printf 'unavailable\n' ;;
  esac
}

codegraph_status_text() {
  local bin="$1" target="$2" tmp pid waited=0
  tmp=$(mktemp -t fskill-codegraph-status.XXXXXX)
  "$bin" status "$target" >"$tmp" 2>&1 &
  pid=$!
  while [ "$waited" -lt 20 ]; do
    if ! kill -0 "$pid" 2>/dev/null; then
      wait "$pid" || true
      cat "$tmp"
      rm -f "$tmp"
      return 0
    fi
    sleep 1
    waited=$((waited + 1))
  done
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  rm -f "$tmp"
  printf 'timeout\n'
}

report_tool() {
  local name="$1" on_path="$2" off_path="$3"
  if [ -n "$on_path" ]; then
    printf '%s_present: yes\n' "$name"
    printf '%s_path: %s\n' "$name" "$(display_path "$on_path")"
    return 0
  fi
  printf '%s_present: no\n' "$name"
  if [ -n "$off_path" ]; then
    printf '%s_off_path: %s\n' "$name" "$(display_path "$off_path")"
  fi
}

rtk_bin=$(resolve_on_path rtk 2>/dev/null || true)
rtk_off=""
if [ -z "$rtk_bin" ]; then
  rtk_off=$(first_off_path rtk \
    "$HOME/.local/bin/rtk" \
    /opt/homebrew/bin/rtk \
    /usr/local/bin/rtk 2>/dev/null || true)
fi
report_tool rtk "$rtk_bin" "$rtk_off"

codegraph_bin=$(resolve_on_path codegraph 2>/dev/null || true)
codegraph_off=""
codegraph_index="unavailable"
if [ -z "$codegraph_bin" ]; then
  codegraph_off=$(first_off_path codegraph \
    "$HOME/.local/bin/codegraph" \
    "$HOME/.npm-global/bin/codegraph" \
    "$HOME/repos/.npm-global/bin/codegraph" \
    /opt/homebrew/bin/codegraph \
    /usr/local/bin/codegraph 2>/dev/null || true)
else
  codegraph_index=$(classify_index "$(codegraph_status_text "$codegraph_bin" "$HEALTH_TARGET")")
fi
report_tool codegraph "$codegraph_bin" "$codegraph_off"
printf 'codegraph_index: %s\n' "$codegraph_index"
