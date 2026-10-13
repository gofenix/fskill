#!/usr/bin/env bash
# Local HTTP smoke for /read; runs even when WAZA_SMOKE_OFFLINE=1.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

python3 "$SCRIPT_DIR/read_fetch_smoke.py"
