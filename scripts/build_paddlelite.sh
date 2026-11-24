#!/usr/bin/env bash
# Run on the matching Linux ARM64 board with its Python/SDK toolchain.
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root/third_party/paddlelite"
"${PYTHON:-python3}" setup.py build_ext --inplace
shopt -s nullglob
libraries=(paddlelite*.so)
if [ "${#libraries[@]}" -eq 0 ]; then
    echo "No PaddleLite extension produced; inspect the SDK/CMake build output." >&2
    exit 1
fi
mkdir -p "$repo_root/third_party/runtime"
cp -- "${libraries[@]}" "$repo_root/third_party/runtime/"
