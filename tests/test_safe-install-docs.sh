#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

python3 "$ROOT/scripts/check_safe_install_docs.py" --root "$ROOT"

if [ "$(grep -c '^[[:space:]]*set -e$' "$ROOT/README.md")" -lt 2 ] ||
   [ "$(grep -c "trap 'rm -f.*' EXIT" "$ROOT/README.md")" -lt 2 ]; then
  echo "download-review examples must fail closed and clean temporary scripts" >&2
  exit 1
fi

echo "safe install docs smoke: ok"
