#!/usr/bin/env bash
# Run in MSYS2 CLANG64, following the upstream Windows toolchain.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ "${MSYSTEM:-}" != CLANG64 ]]; then
    echo 'Run this script in the MSYS2 CLANG64 shell on Windows.' >&2
    exit 1
fi
python scripts/prepare.py
cmake -S .cache/azahar -B build/windows -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DENABLE_QT=ON -DENABLE_QT_TRANSLATION=ON \
    -DENABLE_QT_UPDATE_CHECKER=OFF -DENABLE_TESTS=ON \
    -DENABLE_ROOM_STANDALONE=OFF -DUSE_DISCORD_PRESENCE=OFF \
    -DENABLE_LTO=OFF -DCITRA_WARNINGS_AS_ERRORS=OFF
cmake --build build/windows --parallel "${BUILD_JOBS:-4}"
ctest --test-dir build/windows -C Release --output-on-failure --no-tests=error
cmake --build build/windows --target bundle --parallel "${BUILD_JOBS:-4}"
python scripts/package.py
