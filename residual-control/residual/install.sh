#!/usr/bin/env sh
set -eu
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m); case "$ARCH" in x86_64) ARCH=amd64;; arm64|aarch64) ARCH=arm64;; esac
URL="https://github.com/you/residual/releases/latest/download/residual_${OS}_${ARCH}.tar.gz"
BIN_DIR="${BIN_DIR:-/usr/local/bin}"
[ -w "$BIN_DIR" ] 2>/dev/null || BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
curl -fsSL "$URL" | tar xz -C "$BIN_DIR" residual
echo "installed residual → $BIN_DIR/residual"
