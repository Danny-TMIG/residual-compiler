#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"

ENGINES = {
    "python": ("python3", "language"), "rust": ("cargo", "language"),
    "go": ("go", "language"), "swift": ("swiftc", "language"),
    "node": ("node", "language"), "perl": ("perl", "language"),
    "ruby": ("ruby", "language"), "php": ("php", "language"),
    "java": ("javac", "language"), "kotlin": ("kotlinc", "language"),
    "scala": ("scalac", "language"), "groovy": ("groovyc", "language"),
    "c": ("clang", "language"), "cpp": ("clang++", "language"),
    "fortran": ("gfortran", "language"), "haskell": ("ghc", "language"),
    "erlang": ("erlc", "language"), "elixir": ("elixirc", "language"),
    "lua": ("lua", "language"), "tcl": ("tclsh", "language"),
    "r": ("Rscript", "language"), "julia": ("julia", "language"),
    "bash": ("bash", "language"), "zsh": ("zsh", "language"),
    "powershell": ("pwsh", "language"), "dotnet": ("dotnet", "language"),
    "dart": ("dart", "language"), "typescript": ("tsc", "language"),
    "objectivec": ("clang", "language"), "ocaml": ("ocamlopt", "language"),
    "nim": ("nim", "language"), "zig": ("zig", "language"),
    "crystal": ("crystal", "language"), "wasm": ("wasm-pack", "language"),
    "cuda": ("nvcc", "language"), "opencl": ("clang", "language"),
    "verilog": ("iverilog", "language"), "vhdl": ("ghdl", "language"),
    "matlab": ("matlab", "language"), "wolfram": ("wolframscript", "language"),
    "smalltalk": ("gst", "language"), "prolog": ("swipl", "language"),
    "clojure": ("clj", "language"), "scheme": ("guile", "language"),
    "commonlisp": ("sbcl", "language"), "fsharp": ("fsharpc", "language"),
    "reasonml": ("rebuild", "language"), "ada": ("gnatmake", "language"),
    "pascal": ("fpc", "language"), "cobol": ("cobc", "language"),
    "assembly": ("nasm", "language"), "ml": ("ocaml", "language"),
    "jsonnet": ("jsonnet", "language"), "yaml": ("yq", "config"),
    "graphql": ("graphql", "config"), "sql": ("sqlite3", "data"),
    "nosql": ("mongo", "data"), "docker": ("docker", "infra"),
    "kubernetes": ("kubectl", "infra"), "terraform": ("terraform", "infra"),
    "ansible": ("ansible-playbook", "infra"), "nix": ("nix-build", "build"),
    "bazel": ("bazel", "build"), "make": ("make", "build"),
    "cmake": ("cmake", "build"), "gradle": ("gradle", "build"),
    "maven": ("mvn", "build"), "poetry": ("poetry", "package"),
    "pip": ("pip", "package"), "conda": ("conda", "package"),
    "npm": ("npm", "package"), "pnpm": ("pnpm", "package"),
    "yarn": ("yarn", "package"), "composer": ("composer", "package"),
    "helm": ("helm", "infra"), "ipfs": ("ipfs", "data"),
    "nats": ("nats-server", "data"), "redis": ("redis-server", "data"),
    "postgres": ("psql", "data"), "mysql": ("mysql", "data"),
    "sqlite": ("sqlite3", "data"), "mongodb": ("mongod", "data"),
    "influxdb": ("influxd", "data"), "grafana": ("grafana-server", "obs"),
    "prometheus": ("prometheus", "obs"), "openai": ("openai", "ai"),
    "huggingface": ("transformers-cli", "ai"),
    "torch": ("python3 -m torch.utils.collect_env", "ai"),
    "tensorflow": ("python3 -c 'import tensorflow as tf;print(tf.__version__)'", "ai"),
    "jax": ("python3 -c 'import jax;print(jax.__version__)'", "ai"),
    "onnx": ("onnxruntime", "ai"), "mlflow": ("mlflow", "ai"),
    "ray": ("ray", "ai"), "langchain": ("python3 -m langchain", "ai"),
    "autogen": ("python3 -m autogen", "ai"),
    "quantum_qiskit": ("python3 -m qiskit", "quantum"),
    "quantum_cirq": ("python3 -m cirq", "quantum"),
    "quantum_braket": ("braket", "quantum"),
    "quantum_ionq": ("ionq", "quantum"),
    "quantum_qsharp": ("dotnet run --project qsharp", "quantum"),
    "quantum_xanadu": ("python3 -m pennylane", "quantum"),
    "tensors": ("python3 -c 'import torch, tensorflow; print(\"tensors ok\")'", "ai"),
    "nltk": ("python3 -m nltk.downloader punkt", "ai"),
}

def probe(name, cmd):
    first = cmd.split()[0]
    if first == "python3" and "-m" in cmd.split():
        parts = cmd.split()
        idx = parts.index("-m")
        mod = parts[idx+1] if idx+1 < len(parts) else ""
        try:
            r = subprocess.run(["python3","-c",f"import importlib.util; print('ok' if importlib.util.find_spec('{mod}') else 'missing')"],
                               capture_output=True, text=True, timeout=5)
            return r.stdout.strip() == "ok"
        except Exception:
            return False
    return shutil.which(first) is not None

def main():
    nodes = []
    for name, (cmd, category) in ENGINES.items():
        nodes.append({
            "id": f"engine:{name}", "class": category, "name": name,
            "layer": 4, "invariant": "engine_available",
            "transform": "T_execute", "evidence_id": f"E:{name}",
            "falsify": "cmd_not_found", "closure": "C_engine",
            "cmd": cmd, "category": category,
            "capabilities_provided": [f"exec:{name}"],
            "capabilities_required": [],
            "state": "PENDING",
        })
    (APEX / "ENGINES.json").write_text(json.dumps({"schema":"engines/v1","count":len(nodes),"nodes":nodes}, indent=2) + "\n")
    print(f"[write] apex/ENGINES.json ({len(nodes)} engines)")

    available = 0
    missing = []
    for n in nodes:
        ok = probe(n["name"], n["cmd"])
        n["state"] = "READY" if ok else "PENDING"
        n["available"] = ok
        if ok: available += 1
        else: missing.append(n["name"])

    print(f"[probe] {available}/{len(nodes)} available")
    if missing:
        print(f"[probe] missing ({len(missing)}): {', '.join(missing[:20])}{'...' if len(missing) > 20 else ''}")

    (APEX / "ENGINES-PROBED.json").write_text(json.dumps({
        "schema":"engines/probed/v1","total":len(nodes),"available":available,
        "missing":missing,"nodes":nodes,
    }, indent=2) + "\n")
    print(f"[write] apex/ENGINES-PROBED.json")
    return 0

if __name__ == "__main__":
    import sys; sys.exit(main())
