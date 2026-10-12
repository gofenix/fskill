#!/usr/bin/env bash
# Quiet daily update check for the installed Waza skills.
#
# Reads the public VERSION file on the default branch and compares it to the
# bundled VERSION. If a newer version exists, prints one line so the agent can
# relay it. No data is ever sent (a plain read-only GET); any failure is silent;
# the check runs at most once per day via a shared cache marker, so whichever
# Waza skill runs first that day does the single check and the rest are instant.
set -u

SKILL="waza"
REPO="gofenix/Waza"
UPDATE_CMD="npx skills update -g -y"
# WAZA_UPDATE_URL overrides the source (used by tests); defaults to the public VERSION.
REMOTE_URL="${WAZA_UPDATE_URL:-https://raw.githubusercontent.com/${REPO}/main/VERSION}"

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# VERSION is not packaged; read the version build_metadata.py stamps into the
# shipped setup-rule.sh (WAZA_REF=vX.Y.Z).
local_ver="$(grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?' "${root}/scripts/setup-rule.sh" 2>/dev/null | head -1 | sed 's/^v//')"
[ -n "${local_ver}" ] || exit 0

day="$(date +%F 2>/dev/null)" || exit 0
cache_dir="${XDG_CACHE_HOME:-${HOME}/.cache}/${SKILL}"
marker="${cache_dir}/update-checked-${day}"
[ -f "${marker}" ] && exit 0
mkdir -p "${cache_dir}" 2>/dev/null
: > "${marker}" 2>/dev/null

command -v curl >/dev/null 2>&1 || exit 0
remote_ver="$(curl -fsSL --max-time 3 "${REMOTE_URL}" 2>/dev/null | tr -d '[:space:]')"
[ -n "${remote_ver}" ] || exit 0
[ "${remote_ver}" = "${local_ver}" ] && exit 0

highest="$(printf '%s\n%s\n' "${local_ver}" "${remote_ver}" | sort -V 2>/dev/null | tail -1)"
[ "${highest}" = "${remote_ver}" ] || exit 0

echo "Waza ${remote_ver} is available (you have ${local_ver}). Update: ${UPDATE_CMD}"
exit 0
