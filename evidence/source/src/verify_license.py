#!/usr/bin/env python3
"""Verify the license allow-list includes the licenses you rely on."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "aether" / "research" / "train"))
from pipelines import corpus_pipeline as cp

REQUIRED = {"CC-BY-SA-3.0", "CC-BY-SA-4.0", "CC-BY-4.0", "MIT", "Apache-2.0"}
missing = REQUIRED - cp.PERMISSIVE
print("PERMISSIVE:", sorted(cp.PERMISSIVE))
print("missing:", sorted(missing) or "none")
sys.exit(1 if missing else 0)
