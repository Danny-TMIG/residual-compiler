"""
Parse The Complete Residual Register into structured form.

Input : data/residual_register.md
Output: data/residuals.sqlite  (table: residuals)
        data/residuals.jsonl   (one record per residual)
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "data/residual_register.md")
OUT_JSONL = Path("data/residuals.jsonl")
OUT_DB = Path("data/residuals.sqlite")

PART_RE = re.compile(r"^Part\s+([IVX]+)\s+[—-]\s+(.+?)(?:\s+\(\d+\))?\s*$")
ROW_RE = re.compile(
    r"^(?P<id>[A-ZΩ][A-Z]?-\d{2,3}|Ω)\s+(?P<rest>.+?)\s+(?P<arity>\d+)\s*$"
)


def parse_rows(text):
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = ROW_RE.match(line)
        if not m:
            continue
        rid, rest, arity = m.group("id"), m.group("rest"), int(m.group("arity"))
        parts = rest.rsplit(" ", 2)
        head, mid, source = parts if len(parts) == 3 else (rest, "", "")
        out.append(
            {
                "id": rid,
                "residual": head.strip(),
                "residual_to": mid.strip(),
                "source": source.strip(),
                "arity": arity,
                "raw": line,
            }
        )
    return out


def main():
    if not SRC.exists():
        sys.exit(f"input not found: {SRC}")
    text = SRC.read_text(encoding="utf-8")
    recs, section, buf = [], None, []
    for line in text.splitlines():
        m = PART_RE.match(line.strip())
        if m:
            if buf:
                for r in parse_rows("\n".join(buf)):
                    r["section"] = section
                    r["class"] = section.split(" — ")[0] if section else None
                    recs.append(r)
                buf = []
            section = f"{m.group(1)} — {m.group(2).strip()}"
            continue
        buf.append(line)
    if buf:
        for r in parse_rows("\n".join(buf)):
            r["section"] = section
            r["class"] = section.split(" — ")[0] if section else None
            recs.append(r)
    if not any(r["id"] == "Ω" for r in recs):
        recs.append(
            {
                "id": "Ω",
                "residual": "The act of proceeding",
                "residual_to": "All chains",
                "source": "This thread",
                "arity": 0,
                "section": "XXIV — The Terminal Residual",
                "class": "XXIV",
                "raw": "Ω The act of proceeding All chains This thread 0",
            }
        )
    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    if OUT_DB.exists():
        OUT_DB.unlink()
    con = sqlite3.connect(OUT_DB)
    con.executescript("""
      CREATE TABLE residuals(id TEXT PRIMARY KEY, class TEXT, section TEXT,
        residual TEXT, residual_to TEXT, source TEXT, arity INTEGER, raw TEXT);
      CREATE INDEX i_class ON residuals(class);
      CREATE INDEX i_arity ON residuals(arity);
      CREATE VIRTUAL TABLE residuals_fts USING fts5(residual, residual_to, source, raw,
        content='residuals', content_rowid='rowid');
    """)
    con.executemany(
        "INSERT INTO residuals VALUES(?,?,?,?,?,?,?,?)",
        [
            (
                r["id"],
                r.get("class"),
                r.get("section"),
                r.get("residual"),
                r.get("residual_to"),
                r.get("source"),
                r.get("arity"),
                r.get("raw"),
            )
            for r in recs
        ],
    )
    con.execute(
        "INSERT INTO residuals_fts(rowid,residual,residual_to,source,raw) "
        "SELECT rowid,residual,residual_to,source,raw FROM residuals"
    )
    con.commit()
    con.close()
    from collections import Counter

    c = Counter(r.get("class") for r in recs)
    print(f"parsed {len(recs)} residuals -> {OUT_JSONL}, {OUT_DB}")
    for cls, n in sorted(c.items(), key=lambda x: str(x[0])):
        print(f"  {cls:6} {n}")


if __name__ == "__main__":
    main()
