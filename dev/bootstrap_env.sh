#!/usr/bin/env bash
# Rebuild everything Protez needs to run outside the GUI, from a bare checkout.
#
#     bash dev/bootstrap_env.sh
#
# Machine-local and gitignored on purpose (the sandbox restores between
# sessions can drop anything that was not committed): the venv at
# /home/user/pyenv, the pinned Luau command line tools in tools/ (built from
# the same upstream tag the app pins), and the native host binary.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV=/home/user/pyenv

if [ ! -x "$VENV/bin/python" ]; then
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install -q --upgrade pip
    "$VENV/bin/pip" install -q cmake lupa zstandard pytest tkinterdnd2
fi

cd "$REPO_ROOT"
if [ ! -x tools/luau-compile ] || [ ! -x tools/luau-ast ] || [ ! -x tools/protez-native-host ]; then
    "$VENV/bin/cmake" -S native -B native/build -DCMAKE_BUILD_TYPE=Release >"$REPO_ROOT/logs/luau-build.log" 2>&1
    "$VENV/bin/cmake" --build native/build -j"$(nproc)" >>"$REPO_ROOT/logs/luau-build.log" 2>&1
    mkdir -p logs tools
    cp native/build/host-bin/luau-ast tools/luau-ast
    cp native/build/host-bin/protez-native-host tools/protez-native-host
    cp native/build/_deps/luau-build/luau-compile tools/luau-compile
fi

echo "ready: $("$VENV/bin/python" -c 'import sys; print(sys.version.split()[0])')"
