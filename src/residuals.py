"""
First-class reader for the residual register.

The compiler calls:
  residuals.for_task(description) -> [ {id, class, residual, source, arity, score}, ... ]
  residuals.all_ids()            -> set of ids
  residuals.hash()               -> sha256 of data/residual_register.md
"""

import hashlib, re, sqlite3
from pathlib import Path

REGISTER = Path("data/residual_register.md")
DB = Path("data/residuals.sqlite")

_STOP = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "for",
    "with",
    "by",
    "from",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "this",
    "that",
    "these",
    "those",
    "it",
    "as",
    "at",
    "into",
    "via",
    "per",
    "about",
    "over",
    "under",
    "all",
    "any",
    "some",
}


def _ensure_db():
    if DB.exists():
        return
    if not REGISTER.exists():
        return
    import subprocess, sys

    subprocess.run([sys.executable, "src/parse_residuals.py", str(REGISTER)], check=True)


def hash():
    if not REGISTER.exists():
        return None
    return hashlib.sha256(REGISTER.read_bytes()).hexdigest()


def _tokens(text):
    return [
        t
        for t in re.findall(r"[A-Za-zÀ-ÿ0-9_Ω'-]+", text or "")
        if t.lower() not in _STOP and len(t) > 2
    ]


def for_task(description, limit=None):
    """Return every residual whose indexed text overlaps the description.

    We deliberately do NOT truncate to a top-K: dropping a match because
    another one scored slightly higher defeats the purpose of the limit, which
    is to catch every skill the task claims. Callers may still slice if they
    want, but the register's matches must be complete.
    """
    _ensure_db()
    toks = _tokens(description or "")
    if not toks or not DB.exists():
        return []
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    hits, seen = [], set()
    for t in toks:
        try:
            rows = con.execute(
                "SELECT r.*, bm25(residuals_fts) AS score "
                "FROM residuals_fts f JOIN residuals r ON r.rowid=f.rowid "
                "WHERE residuals_fts MATCH ? ORDER BY score",
                (t,),
            ).fetchall()
        except Exception:
            rows = []
        for r in rows:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            hits.append(
                {
                    "id": r["id"],
                    "class": r["class"],
                    "residual": r["residual"],
                    "source": r["source"],
                    "arity": r["arity"],
                    "score": float(r["score"] or 0),
                }
            )
    hits.sort(key=lambda x: (x["score"], x["id"]))
    return hits if limit is None else hits[:limit]


def all_ids():
    _ensure_db()
    if not DB.exists():
        return set()
    con = sqlite3.connect(DB)
    ids = {r[0] for r in con.execute("SELECT id FROM residuals")}
    con.close()
    return ids


def by_class(cls):
    _ensure_db()
    if not DB.exists():
        return []
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM residuals WHERE class=?", (cls,)).fetchall()
    con.close()
    return [dict(r) for r in rows]
