#!/usr/bin/env sh
set -eu
IN="${1:-checksums.txt}"
SIG="${2:-checksums.txt.sig}"
PUB="${3:-public.pem}"
openssl pkeyutl -verify -pubin -inkey "$PUB" -rawin -in "$IN" -sigfile "$SIG"
echo "✓ Ed25519 signature ok"
shasum -a 256 -c "$IN"
