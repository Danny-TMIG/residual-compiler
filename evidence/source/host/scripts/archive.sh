#!/usr/bin/env bash
# Build a clean source archive (sources only).
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=${1:-/tmp/test-source-$(date +%Y%m%dT%H%M%S).tgz}
HOLD=$(mktemp -d)
for f in \
  .venv .git \
  training_result.json synthetic_dataset.jsonl tokens.bin \
  corpus_real.txt corpus.txt math_code_sample.txt \
  chinese_sp.model chinese_sp.vocab domain_sp.model domain_sp.vocab \
  decision_record.json attestation.json \
  .state state checkpoints bundles artifacts \
  .artifacts .pytest_cache logs \
  evidence.log evidence.log.prev \
  skills.sqlite atlas.sqlite atlas.jsonl \
  data/skills.sqlite data/atlas/atlas.sqlite data/atlas/atlas.jsonl; do
  [ -e "$f" ] && mv "$f" "$HOLD/" 2>/dev/null || true
done
find . -name __pycache__ -type d -prune -exec mv {} "$HOLD/" \; 2>/dev/null || true
tar czf "$OUT" -C "$(dirname "$PWD")" "$(basename "$PWD")"
mv "$HOLD"/* . 2>/dev/null || true
rmdir "$HOLD" 2>/dev/null || true
echo "$OUT ($(du -h "$OUT" | cut -f1))"
