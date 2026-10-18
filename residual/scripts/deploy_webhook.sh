#!/usr/bin/env bash
set -euo pipefail
: "${RESIDUAL_SIGNING_KEY:?set RESIDUAL_SIGNING_KEY to contents of keys/signing.pem}"
: "${STRIPE_WEBHOOK_SECRET:?set STRIPE_WEBHOOK_SECRET}"
cd "$(dirname "$0")/../webhook"
fly launch --no-deploy --name residual-webhook --region sjc --yes 2>/dev/null || true
fly secrets set RESIDUAL_SIGNING_KEY="${RESIDUAL_SIGNING_KEY}" \
                STRIPE_WEBHOOK_SECRET="${STRIPE_WEBHOOK_SECRET}" \
                PORT=8080
fly deploy
