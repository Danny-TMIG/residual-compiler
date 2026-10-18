import os, sys, subprocess
from pathlib import Path

def find_root():
    # env wins
    if env := os.environ.get("RESIDUAL_ROOT"):
        p = Path(env).expanduser().resolve()
        if (p / "scripts" / "control_plane.py").exists():
            return p
    # bundled: PyInstaller unpacks --add-data into sys._MEIPASS
    if hasattr(sys, "_MEIPASS"):
        p = Path(sys._MEIPASS)
        if (p / "scripts" / "control_plane.py").exists():
            return p
    # shell cwd
    cwd = Path.cwd()
    if (cwd / "scripts" / "control_plane.py").exists():
        return cwd
    # binary's real location
    exe = Path(sys.argv[0]).resolve().parent
    if (exe / "scripts" / "control_plane.py").exists():
        return exe
    raise SystemExit("cannot find repo root: set RESIDUAL_ROOT=/path/to/project")

ROOT = find_root()

def python_bin():
    # when bundled, sys.executable is the frozen binary, not Python
    if getattr(sys, "frozen", False):
        return "python3"
    return sys.executable

COMMANDS = {
    "verify":   ["scripts/control_plane.py"],
    "org":      ["scripts/org.py"],
    "const":    ["scripts/constitution.py", "validate", "apex/RECORD.template.json"],
    "conform":  ["scripts/conformance.py"],
    "evidence": ["make", "-f", "Makefile.build", "build"],
    "ship":     ["make", "-f", "Makefile.ship", "ship"],
}

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("usage: residual {" + ",".join(COMMANDS) + "}")
        print(f"root:  {ROOT}")
        return 2
    cmd = COMMANDS[sys.argv[1]]
    if cmd[0].endswith(".py"):
        cmd = [python_bin()] + cmd
    r = subprocess.run(cmd, cwd=str(ROOT))
    return r.returncode

if __name__ == "__main__":
    sys.exit(main())
