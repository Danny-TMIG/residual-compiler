import os
import sys
import hashlib
from pathlib import Path

class RepositoryJanitor:
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir).resolve()
        self.purged_count = 0
        self.normalized_count = 0

    def run_full_cycle(self):
        for cache_dir in self.root.rglob("__pycache__"):
            if cache_dir.is_dir():
                import shutil
                shutil.rmtree(cache_dir)
                self.purged_count += 1
        for pattern in ["*.pyc", "*.tmp", "*.log", ".DS_Store", "fix_*.sh", "*_align.py", "fix_git_blocks.sh"]:
            for junk_file in self.root.rglob(pattern):
                if junk_file.is_file():
                    junk_file.unlink()
                    self.purged_count += 1
        for p in self.root.rglob("*"):
            if any(part.startswith('.') and part != '.' for part in p.parts):
                if not any(sig in str(p) for sig in [".pre-commit-config.yaml", ".github"]):
                    continue
            if p.is_file() and p.suffix in {".py", ".asm", ".json", ".yaml", ".yml", ".md", ".toml"}:
                try:
                    src = p.read_text(encoding="utf-8")
                    lines = src.splitlines()
                    cleaned_lines = [line.rstrip() for line in lines]
                    new_content = "\n".join(cleaned_lines).strip("\n") + "\n"
                    if src != new_content:
                        p.write_text(new_content, encoding="utf-8")
                        self.normalized_count += 1
                except Exception:
                    continue
        target = self.root / "data/skills.sqlite"
        if target.exists():
            sha256_hash = hashlib.sha256()
            with open(target, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            target.with_suffix(target.suffix + ".sha256").write_text(sha256_hash.hexdigest() + "\n")

if __name__ == "__main__":
    RepositoryJanitor().run_full_cycle()
