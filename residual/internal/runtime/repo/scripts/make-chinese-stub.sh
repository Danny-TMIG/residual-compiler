#!/usr/bin/env bash
# Generate a small Chinese smoke corpus (for the Chinese path only).
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$HERE/data/raw/chinese_corpus.txt"
python - "$OUT" <<'PY'
import sys, itertools, pathlib
lines = [
    "人工智能正在改变我们的生活方式。",
    "机器学习模型需要大量高质量的数据。",
    "自然语言处理是计算机科学的重要分支。",
    "深度学习在图像识别领域取得了巨大成功。",
    "数据清洗是训练模型之前的关键步骤。",
]
out = pathlib.Path(sys.argv[1])
with out.open("w", encoding="utf-8") as f:
    for i, line in enumerate(itertools.islice(itertools.cycle(lines), 2000)):
        f.write(line + "\n")
print("wrote", out, "lines:", 2000)
PY
