#!/usr/bin/env python3
"""model_card.py — emit a model card per ISO/IEC 23053 fields."""

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "apex" / "models"
MODELS.mkdir(parents=True, exist_ok=True)

CARDS = {
    "qwen2.5-vl-7b": {
        "model_id": "Qwen/Qwen2.5-VL-7B-Instruct",
        "version": "unreleased",
        "modality": ["text", "image"],
        "intended_use": "local vision-language inference on Apple Silicon",
        "limitations": ["no tool use attested", "no safety filter run"],
        "eval": {"not_run": True},
        "biases": "unknown — no red-team performed",
        "license": "Apache-2.0 (per upstream)",
        "file": None,
    },
    "qwen2.5-coder-3b": {
        "model_id": "Qwen/Qwen2.5-Coder-3B-Instruct",
        "version": "unreleased",
        "modality": ["text"],
        "intended_use": "local code generation",
        "limitations": ["no eval", "no license audit of training data"],
        "eval": {"not_run": True},
        "biases": "unknown",
        "license": "Apache-2.0 (per upstream)",
        "file": None,
    },
    "bge-small": {
        "model_id": "BAAI/bge-small-en-v1.5",
        "version": "unreleased",
        "modality": ["text"],
        "intended_use": "embedding for retrieval",
        "limitations": ["English only"],
        "eval": {"not_run": True},
        "biases": "unknown",
        "license": "MIT (per upstream)",
        "file": None,
    },
}


def sha256_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    written = []
    for slug, card in CARDS.items():
        # Attach file hash if a GGUF is present.
        for cand in [ROOT / f"{slug}.gguf", ROOT / "models" / f"{slug}.gguf"]:
            if cand.exists():
                card["file"] = {
                    "path": str(cand.relative_to(ROOT)),
                    "sha256": sha256_of(cand),
                }
                break
        card["standard"] = ["ISO/IEC 23053", "EU AI Act Annex IV (partial)"]
        card["ring"] = 2
        card["ts"] = dt.datetime.now(dt.UTC).isoformat()
        out = MODELS / f"{slug}.card.json"
        out.write_text(json.dumps(card, indent=2) + "\n")
        written.append(str(out.relative_to(ROOT)))
    print(json.dumps({"written": written, "count": len(written)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
