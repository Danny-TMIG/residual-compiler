#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
mkdir -p ../host/bin
for f in *.S; do
    clang -c -o "../host/bin/${f%.S}.o" "$f" || echo "[skip] ${f}"
done
echo "[build] assembled"
