#!/usr/bin/env sh
set -eu
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m); case "$ARCH" in x86_64) ARCH=amd64;; arm64|aarch64) ARCH=arm64;; esac
BASE="https://github.com/Danny-TMIG/residual-compiler/releases/latest/download"
BIN_DIR="${BIN_DIR:-/usr/local/bin}"
[ -w "$BIN_DIR" ] 2>/dev/null || BIN_DIR="$HOME/.local/bin"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "→ fetching residual_${OS}_${ARCH}.tar.gz"
curl -fsSL "${BASE}/residual_${OS}_${ARCH}.tar.gz" -o "$TMP/r.tgz"
curl -fsSL "${BASE}/checksums.txt"     -o "$TMP/checksums.txt"
curl -fsSL "${BASE}/checksums.txt.sig" -o "$TMP/checksums.txt.sig" || true
curl -fsSL "${BASE}/public.pem"        -o "$TMP/public.pem" || true

if [ -s "$TMP/checksums.txt.sig" ] && [ -s "$TMP/public.pem" ] && command -v openssl >/dev/null 2>&1; then
  echo "→ verifying Ed25519 signature"
  openssl pkeyutl -verify -pubin -inkey "$TMP/public.pem" -rawin \
    -in "$TMP/checksums.txt" -sigfile "$TMP/checksums.txt.sig" >/dev/null 2>&1 \
    && echo "  ✓ signature ok" \
    || { echo "  ✗ signature failed"; exit 1; }
fi

echo "→ verifying sha256"
( cd "$TMP" && grep "residual_${OS}_${ARCH}.tar.gz$" checksums.txt > sha \
  && shasum -a 256 -c sha )

mkdir -p "$BIN_DIR"
tar xzf "$TMP/r.tgz" -C "$BIN_DIR" residual
chmod +x "$BIN_DIR/residual"
echo "✓ installed → $BIN_DIR/residual"
"$BIN_DIR/residual" --help >/dev/null && echo "✓ binary runs"
