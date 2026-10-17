import sqlite3
from .contracts import SkillContract, ResultState
from . import dispatch

IMPL = {
    "filesystem-search": "filesystem-search",
    "regex-search": "regex-search",
    "execute-command": "execute-command",
    "evidence-hash": "evidence-hash",
    "evidence-capture": "evidence-capture",
    "policy-check": "policy-check",
    "authority-check": "authority-check",
}


def _ensure_atlas():
    """Build data/atlas/atlas.sqlite from data/atlas/atlas.txt if missing."""
    from pathlib import Path
    import subprocess, sys

    db = Path("data/atlas/atlas.sqlite")
    txt = Path("data/atlas/atlas.txt")
    if db.exists():
        return
    if not txt.exists():
        raise SystemExit(f"cannot seed: missing {txt} and {db}")
    print(f"[seed] building {db} from {txt}")
    subprocess.run([sys.executable, "src/parse_atlas.py", str(txt)], check=True)


def main():
    _ensure_atlas()
    from . import bind_all  # registers every skill tool on import

    # rotate evidence log so chain starts at genesis
    import os

    for f in ("evidence.log",):
        if os.path.exists(f):
            os.replace(f, f + ".prev")
    n_slugs = bind_all.apply()
    from . import scoped, tools as _t

    scoped.write_scope(_t.REG)
    con = sqlite3.connect("data/atlas/atlas.sqlite")
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM items WHERE kind='skill'").fetchall()
    con.close()
    for r in rows:
        impl = IMPL.get(r["slug"], "")
        sub = "-".join(r["subsection"].lower().split()) if r["subsection"] else "root"
        qid = f"{r['slug']}__{sub}"
        from . import tools as _t

        schema = (_t.REG.get(impl, {}) or {}).get("schema", {}) if impl else {}
        c = SkillContract(
            identifier=qid,
            description=f"{r['name']} ({r['subsection']})",
            input_types=schema,
            capability=r["subsection"] or "",
            domain=r["section"] or "",
            operation=r["slug"].split("-")[0],
            output_types={"result_state": "string"},
            result_states=[s.value for s in ResultState],
            impl=impl,
            evidence_produced=["skill_result"],
        )
        try:
            dispatch.bind(c)
        except Exception as e:
            print(f"skip {r['slug']}: {e}")
    import sqlite3 as _sq

    c2 = _sq.connect("data/skills.sqlite")
    bound = c2.execute(
        "SELECT COUNT(*) FROM skills WHERE json_extract(contract,'$.impl') <> ''"
    ).fetchone()[0]
    total = c2.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
    print(f"seeded {total} skills, {bound} bound  (+{n_slugs} new mappings from bind_all)")


if __name__ == "__main__":
    main()
