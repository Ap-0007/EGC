#!/usr/bin/env bash
# install.sh — Legacy shell entrypoint for the EGC installer.
#
# This wrapper resolves the real repo/package root when invoked through a
# symlinked npm bin, then delegates to the Node-based installer runtime.
# Runtime paths derive from the wrapper location, never from the cwd.

set -euo pipefail

SCRIPT_PATH="$0"
while [ -L "$SCRIPT_PATH" ]; do
    link_dir="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
    SCRIPT_PATH="$(readlink "$SCRIPT_PATH")"
    [[ "$SCRIPT_PATH" != /* ]] && SCRIPT_PATH="$link_dir/$SCRIPT_PATH"
done
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"

# --- Production-grade environment validation (fail deterministically) ---
fail() { echo "[EGC] ERROR: $*" >&2; exit 1; }

command -v node >/dev/null 2>&1 || fail "Node.js not found in PATH. Install Node.js >= 18."
NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
case "$NODE_MAJOR" in ''|*[!0-9]*) NODE_MAJOR=0 ;; esac
[ "$NODE_MAJOR" -ge 18 ] || fail "Node.js >= 18 required (found: $(node --version 2>/dev/null || echo none))."

PYTHON_BIN=""
for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then PYTHON_BIN="$c"; break; fi
done
[ -n "$PYTHON_BIN" ] || fail "Python not found in PATH. Install Python >= 3.10 (python3 or python)."
PY_OK="$("$PYTHON_BIN" -c 'import sys; print(1 if sys.version_info[:2] >= (3, 10) else 0)' 2>/dev/null || echo 0)"
[ "$PY_OK" = "1" ] || fail "Python >= 3.10 required (found: $("$PYTHON_BIN" --version 2>&1 || echo none))."

# Repository-local binaries always win over host binaries.
export PATH="$SCRIPT_DIR/node_modules/.bin:$SCRIPT_DIR/.venv/bin:$PATH"

# Auto-install Node dependencies when running from a git clone
if [ ! -d "$SCRIPT_DIR/node_modules" ]; then
    echo "[EGC] Installing dependencies..."
    (cd "$SCRIPT_DIR" && npm install --no-audit --no-fund --loglevel=error) || fail "npm install failed."
fi

# On MSYS2/Git Bash, convert the POSIX path to a Windows path so Node.js
# (a native Windows binary) receives a valid path instead of a doubled one
# like G:\g\projects\... that results from Git Bash's auto path conversion.
if command -v cygpath >/dev/null 2>&1; then
    NODE_SCRIPT="$(cygpath -w "$SCRIPT_DIR/scripts/install-apply.js")"
else
    NODE_SCRIPT="$SCRIPT_DIR/scripts/install-apply.js"
fi

exec node "$NODE_SCRIPT" "$@"
