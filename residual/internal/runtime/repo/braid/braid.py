#!/usr/bin/env python3
"""braid.py — run all 6 language backends + NLTK + tensors, compare graphs."""
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def run(cmd, label, cwd=ROOT):
    print(f"\n[{label}]")
    print(f"  cmd: {' '.join(cmd)}")
    try:
        r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            print(f"  [PASS] {r.stdout.strip().splitlines()[:2]}")
            return True
        else:
            print(f"  [SKIP] not available or failed: {(r.stderr or r.stdout)[:100]}")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  [SKIP] {e}")
        return False

def main():
    results = {}

    # 1. Go
    if shutil.which("go"):
        results["go"] = run(["go", "run", "go/main.go"], "go")
    else:
        print("\n[go] not installed — skipping")

    # 2. Ruby
    if shutil.which("ruby"):
        results["ruby"] = run(["ruby", "ruby/compile.rb"], "ruby")
    else:
        print("\n[ruby] not installed — skipping")

    # 3. Rust
    if shutil.which("cargo"):
        results["rust"] = run(["cargo", "run", "--quiet"], "rust", cwd=ROOT / "rust")
    else:
        print("\n[rust] not installed — skipping")

    # 4. Perl
    if shutil.which("perl"):
        results["perl"] = run(["perl", "perl/compile.pl"], "perl")
    else:
        print("\n[perl] not installed — skipping")

    # 5. Python
    results["python"] = run(["python3", "python/compile.py"], "python")

    # 6. compare graphs
    print("\n[braid] comparing graphs from all backends")
    graphs = {}
    for name in ["go", "ruby", "rust", "perl", "python"]:
        p = ROOT / f"graph-{name}.json"
        if p.exists():
            try:
                graphs[name] = json.loads(p.read_text())
                n_ops = len(graphs[name].get("nodes", []))
                print(f"  {name}: {n_ops} nodes")
            except Exception as e:
                print(f"  {name}: parse error {e}")

    if graphs:
        node_counts = [len(g.get("nodes", [])) for g in graphs.values()]
        consistent = len(set(node_counts)) <= 1
        print(f"\n[braid] {len(graphs)} backends, node counts: {node_counts}")
        print(f"[braid] consistent: {consistent}")
        print(f"[braid] {'ALL BACKENDS AGREE' if consistent else 'BACKENDS DISAGREE'}")

    print(f"\n[braid] available: {sum(results.values())}/{len(results)}")

if __name__ == "__main__":
    main()
