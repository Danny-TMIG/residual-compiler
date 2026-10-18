#!/usr/bin/env bash
set -euo pipefail
KEY="${1:-keys/signing.pem}"
IN="${2:-dist/checksums.txt}"
OUT="${IN}.sig"
openssl pkeyutl -sign -inkey "$KEY" -rawin -in "$IN" -out "$OUT"
echo "signed $IN → $OUT"
