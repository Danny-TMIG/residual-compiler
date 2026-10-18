# residual

Sovereign intent verification. One binary. Offline. Verifiable.

## Install

    curl -fsSL https://github.com/Danny-TMIG/residual-compiler/releases/latest/download/install.sh | sh

The installer downloads the tarball, its `checksums.txt`, the Ed25519 signature `checksums.txt.sig`,
and the public key `public.pem`, verifies the signature, verifies the sha256, and extracts
`residual` to `$HOME/.local/bin/`.

## Activate

    residual activate <jwt-from-email>

## Use

    residual verify --intent ./intent.json   # → { "verdict": "COVERED", ... }
    residual conform                         # → { "chain": {"intact": true}, ... }
    residual status                          # → license line
    residual serve                           # → http://localhost:7180

## Verify what you downloaded

    residual/scripts/verify_checksums.sh checksums.txt checksums.txt.sig public.pem

## Build

    cd residual
    go build -trimpath -ldflags="-s -w" -o dist/residual ./cmd/residual
