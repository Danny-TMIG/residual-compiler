"""Structured logging + health check. Stdlib only."""

import json, logging, os, sys, time
from pathlib import Path


def configure(level="INFO"):
    """Configure structured JSON logging to stderr or a file."""
    dest = os.environ.get("ATLAS_LOG")
    handler = logging.FileHandler(dest) if dest else logging.StreamHandler(sys.stderr)
    handler.setFormatter(_JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(getattr(logging, level, logging.INFO))


class _JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "ts": time.time(),
                "level": record.levelname,
                "logger": record.name,
                "msg": record.getMessage(),
                "exc": self.formatException(record.exc_info) if record.exc_info else None,
            },
            ensure_ascii=False,
        )


def health():
    """Return a health dict: DBs present, chain verifiable, bound count."""
    from src import audit, scoped

    db_ok = Path("data/skills.sqlite").exists()
    atlas_ok = Path("data/atlas/atlas.sqlite").exists()
    chain = audit.verify_chain()
    scope = scoped.load_scope()
    return {
        "ok": db_ok and atlas_ok and chain["ok"],
        "skills_db": db_ok,
        "atlas_db": atlas_ok,
        "chain": chain,
        "bound_tools": len(scope),
    }
