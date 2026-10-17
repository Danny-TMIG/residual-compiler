#!/usr/bin/env bash
# Drop the >=30% CJK requirement in output_filter (needed for English data).
set -euo pipefail
TARGET="$HOME/aether/research/train/pipelines/teacher_pipeline.py"
python - "$TARGET" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
s = p.read_text()
old = "        if total == 0 or chinese / total < 0.3:\n"
new = "        if total == 0:\n"
if new in s:
    print("already relaxed"); sys.exit(0)
assert old in s, "expected CJK check not found verbatim"
p.write_text(s.replace(old, new, 1))
print("patched:", p)
PY
find "$HOME/aether/research/train" -name 'teacher_pipeline*.pyc' -delete
echo "cleared bytecode"
