#!/usr/bin/env bash
# verify_checksums.sh <checksums.txt> <checksums.txt.sig> <public.pem>
set -euo pipefail
IN="${1:-checksums.txt}"
SIG="${2:-checksums.txt.sig}"
PUB="${3:-public.pem}"
openssl pkeyutl -verify -pubin -inkey "$PUB" -rawin -in "$IN" -sigfile "$SIG"
echo "signature ok"
shasum -a 256 -c "$IN"
