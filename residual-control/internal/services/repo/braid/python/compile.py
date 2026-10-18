#!/usr/bin/env python3
"""Python backend with NLTK symbol resolution and numpy tensors."""
import json
from pathlib import Path

# ---- tensors (no numpy dependency) ----
class Tensor:
    def __init__(self, data):
        self.data = data  # list of lists
    def __repr__(self):
        return f"Tensor({self.data})"
    def __matmul__(self, other):
        a, b = self.data, other.data
        rows = len(a)
        cols = len(b[0])
        return Tensor([[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(cols)] for i in range(rows)])
    def __add__(self, other):
        return Tensor([[self.data[i][j] + other.data[i][j] for j in range(len(self.data[0]))] for i in range(len(self.data))])
    def T(self):
        return Tensor([[self.data[j][i] for j in range(len(self.data))] for i in range(len(self.data[0]))])

# ---- NLTK symbol resolution (optional) ----
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import wordnet as wn
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False

def resolve_with_nltk(raw_input):
    """Resolve symbols by tokenizing + lemma expansion."""
    if not HAS_NLTK:
        return raw_input.split()
    try:
        tokens = word_tokenize(raw_input.lower())
    except LookupError:
        tokens = raw_input.lower().split()
    expanded = []
    for tok in tokens:
        expanded.append(tok)
        for syn in wn.synsets(tok)[:1]:
            for lemma in syn.lemmas():
                if lemma.name() not in expanded:
                    expanded.append(lemma.name())
    return expanded

# ---- compile ----
def compile_intent(intent, table):
    resolved = [table[sid] for sid in intent["symbols"] if sid in table]
    ops = []
    for s in resolved:
        ops.extend(s["expands_to"]["operators"])
    nodes = [
        {"id": f"n-{i}", "operator": op, "inputs": {}, "outputs": {}, "status": "PENDING"}
        for i, op in enumerate(ops)
    ]
    edges = [
        {"from": nodes[i]["id"], "to": nodes[i+1]["id"], "condition": {}}
        for i in range(len(nodes) - 1)
    ]
    return {"nodes": nodes, "edges": edges}

def main():
    root = Path(__file__).resolve().parent.parent
    schema = json.loads((root / "schema.json").read_text())
    symbols = json.loads((root / "symbols.json").read_text())
    intent = json.loads((root / "intent.json").read_text())

    print(f"[python] nltk={'yes' if HAS_NLTK else 'no'}")
    if HAS_NLTK:
        resolved = resolve_with_nltk(intent["raw_input"])
        print(f"[python] nltk tokens: {resolved}")

    graph = compile_intent(intent, symbols)
    (root / "graph-python.json").write_text(json.dumps(graph, indent=2))
    print(json.dumps(graph, indent=2)[:300])

    # demo tensor
    a = Tensor([[1, 2], [3, 4]])
    b = Tensor([[5, 6], [7, 8]])
    print(f"[tensor] a@b = {(a @ b).data}")
    print(f"[tensor] a+b = {(a + b).data}")

if __name__ == "__main__":
    main()
