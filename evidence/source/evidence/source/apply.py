import subprocess, sys
from pathlib import Path

CHECK_ONLY = "--check-only" in sys.argv

BASE = "53303ca"  # last known-good commit before scaffold overwrote things
ROOT = Path.cwd()

# --- step 1: recover truncated files from BASE ---
RECOVER = [".gitignore", "Makefile", "pyproject.toml", ".github/workflows/ci.yml"]

def git_show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

print("=== step 1: recover from", BASE, "===")
recovered = []
for rel in RECOVER:
    p = ROOT / rel
    old = p.read_text() if p.exists() else ""
    prior = git_show(BASE, rel)
    if prior is None:
        print(f"[skip]    {rel} — not in {BASE}")
        continue
    if len(prior.splitlines()) > len(old.splitlines()):
        p.write_text(prior)
        recovered.append(rel)
        print(f"[restore] {rel}  {len(old.splitlines())} -> {len(prior.splitlines())} lines")
    else:
        print(f"[keep]    {rel}  (disk {len(old.splitlines())} lines >= base {len(prior.splitlines())})")

# --- step 2: dangerous paths must be ignored ---
DANGER = [
    "atlas.sqlite", "skills.sqlite", "data/skills.sqlite",
    "checkpoints/", "models/", "sovereign/",
    "corpus_real.txt", "corpus.txt", "tokens.bin",
    "bin/flat/", "training_result.json", "split_manifest.json",
]

print("\n=== step 2: verify dangerous paths are ignored ===")
not_ignored = []
for d in DANGER:
    r = subprocess.run(["git", "check-ignore", "-q", d], capture_output=True)
    if r.returncode == 0:
        rule = subprocess.run(["git", "check-ignore", "-v", d],
                              capture_output=True, text=True).stdout.strip()
        print(f"[ok]      {d}  <- {rule}")
    else:
        not_ignored.append(d)
        print(f"[DANGER]  {d}  NOT IGNORED")

if not_ignored:
    print(f"\nABORT: {len(not_ignored)} dangerous path(s) not ignored:")
    for d in not_ignored:
        print(f"  - {d}")
    print("\nRefusing to continue. Fix .gitignore, then re-run.")
    sys.exit(1)

# --- step 3: report current uncommitted state ---
print("\n=== step 3: working tree state ===")
st = subprocess.run(["git", "status", "--short"], capture_output=True, text=True).stdout
if st.strip():
    print(st)
else:
    print("(clean)")

print("\n=== summary ===")
print(f"recovered: {recovered or '(none)'}")
print(f"danger paths: all ignored ({len(DANGER)} checked)")
print("\nSafe to:")
print("  git add .gitignore Makefile pyproject.toml .github/workflows/ci.yml")
print("  git commit -s -m 'fix: restore full config files from 53303ca'")
print("  git push")

# --- step 4: control-plane gate (all crafts must be covered) ---
if not CHECK_ONLY or True:
    print('\n=== step 4: control plane ===')
    import subprocess as _sp
    _r = _sp.run(['python3', 'scripts/control_plane.py'], capture_output=True, text=True)
    print((_r.stdout or '').strip()[-600:])
    if _r.returncode != 0:
        print('\nABORT: control plane REFUTED — at least one craft failed')
        sys.exit(1)

# --- step 5: constitution ---
if not CHECK_ONLY:
    import subprocess as _sp5
    _r5 = _sp5.run(['python3','scripts/constitution.py','validate',
                    'apex/RECORD.template.json'], capture_output=True, text=True)
    if _r5.returncode != 0:
        print('[constitution] INVALID')
        print(_r5.stdout)
        sys.exit(1)
    print('[constitution] record valid (160 classes)')

