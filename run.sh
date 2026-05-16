#!/usr/bin/env bash
# EGC runtime wrapper — repository-isolated, cwd-independent.
#
# All runtime paths derive from the wrapper location (PROJECT_ROOT), never
# from the current working directory. Repository-local binaries
# (node_modules/.bin, .venv/bin) always win over host binaries.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
export PROJECT_ROOT

export PATH="$PROJECT_ROOT/node_modules/.bin:$PROJECT_ROOT/.venv/bin:$PATH"

exec node "$PROJECT_ROOT/scripts/egc.js" "$@"
