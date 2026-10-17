import json, re, sqlite3, sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "data/atlas/atlas.txt")
OUT_JSONL = Path("data/atlas/atlas.jsonl")
OUT_DB = Path("data/atlas/atlas.sqlite")
SECTION_RE = re.compile(r"^(\d{2})\.\s+(.+?)\s*$")
BULLET_RE = re.compile(r"^\*\s+(.+?)\s*$")
HEADER_RE = re.compile(r"^[A-Z][A-Za-z0-9 /&\-]+$")
KIND = {
    "01": "role",
    "02": "skill",
    "03": "operation",
    "04": "granularity",
    "05": "contract_field",
    "06": "routing_dim",
    "07": "result_state",
    "08": "flow_step",
}


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().strip()).strip("-")


def parse(path):
    out, section, sub, num = [], None, None, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        m = SECTION_RE.match(line)
        if m and len(m.group(1)) == 2:
            num, section, sub = m.group(1), line.strip(), None
            continue
        if (
            (not line.startswith("*"))
            and HEADER_RE.match(line.strip())
            and len(line.strip()) <= 60
            and not line.strip().endswith(".")
        ):
            sub = line.strip()
            continue
        b = BULLET_RE.match(line)
        if b:
            name = b.group(1).strip()
            out.append(
                {
                    "id": f"{num}:{slugify(sub or 'root')}:{slugify(name)}",
                    "kind": KIND.get(num, "unknown"),
                    "section": section,
                    "subsection": sub,
                    "name": name,
                    "slug": slugify(name),
                    "text": name,
                }
            )
    return out


def write_jsonl(recs, p):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_db(recs, p):
    if p.exists():
        p.unlink()
    con = sqlite3.connect(p)
    con.executescript("""CREATE TABLE items(id TEXT PRIMARY KEY, kind TEXT, section TEXT,
        subsection TEXT, name TEXT, slug TEXT, text TEXT);
        CREATE INDEX i_kind ON items(kind);
        CREATE VIRTUAL TABLE items_fts USING fts5(name,text,subsection,
        content='items',content_rowid='rowid');""")
    con.executemany(
        "INSERT INTO items VALUES(?,?,?,?,?,?,?)",
        [
            (r["id"], r["kind"], r["section"], r["subsection"], r["name"], r["slug"], r["text"])
            for r in recs
        ],
    )
    con.execute(
        "INSERT INTO items_fts(rowid,name,text,subsection) SELECT rowid,name,text,subsection FROM items"
    )
    con.commit()
    con.close()


if __name__ == "__main__":
    if not SRC.exists():
        sys.exit(f"input not found: {SRC}")
    recs = parse(SRC)
    write_jsonl(recs, OUT_JSONL)
    write_db(recs, OUT_DB)
    from collections import Counter

    print(f"parsed {len(recs)} items -> {OUT_JSONL}, {OUT_DB}")
    for k, v in sorted(Counter(r["kind"] for r in recs).items()):
        print(f"  {k:16} {v}")
