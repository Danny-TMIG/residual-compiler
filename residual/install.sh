#!/usr/bin/env sh
set -eu
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m); case "$ARCH" in x86_64) ARCH=amd64;; arm64|aarch64) ARCH=arm64;; esac
BASE="https://github.com/Danny-TMIG/residual-compiler/releases/latest/download"
BIN_DIR="${BIN_DIR:-/usr/local/bin}"
[ -w "$BIN_DIR" ] 2>/dev/null || BIN_DIR="$HOME/.local/bin"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "downloading residual_${OS}_${ARCH}.tar.gz"
curl -fsSL "${BASE}/residual_${OS}_${ARCH}.tar.gz" -o "$TMP/residual.tar.gz"
curl -fsSL "${BASE}/checksums.txt"     -o "$TMP/checksums.txt"
curl -fsSL "${BASE}/checksums.txt.sig" -o "$TMP/checksums.txt.sig" 2>/dev/null || true
curl -fsSL "${BASE}/public.pem"        -o "$TMP/public.pem" 2>/dev/null || true

if [ -s "$TMP/checksums.txt.sig" ] && [ -s "$TMP/public.pem" ]; then
  if command -v openssl >/dev/null 2>&1; then
    ( cd "$TMP" && openssl pkeyutl -verify -pubin -inkey public.pem -rawin \
        -in checksums.txt -sigfile checksums.txt.sig >/dev/null 2>&1 ) \
      && echo "✓ signature verified" \
      || { echo "✗ signature failed"; exit 1; }
  fi
fi

( cd "$TMP" && grep "residual_${OS}_${ARCH}.tar.gz$" checksums.txt > sha && shasum -a 256 -c sha )
mkdir -p "$BIN_DIR"
tar xzf "$TMP/residual.tar.gz" -C "$BIN_DIR" residual
echo "installed residual → $BIN_DIR/residual"
"$BIN_DIR/residual" --help >/dev/null && echo "ok"
