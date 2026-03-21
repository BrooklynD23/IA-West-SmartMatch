#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAT3_DIR="$ROOT_DIR/Category 3 - IA West Smart Match CRM"

exec "$CAT3_DIR/scripts/start_dev.sh"
