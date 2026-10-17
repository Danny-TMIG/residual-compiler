#!/usr/bin/env python3
import json, random, sys

def attack_boundary(pred):
    cases = [0, 1, -1, 2**31-1, -2**31, 0.0, 1.0, -1.0, float('inf'), float('-inf'), float('nan'), "", None, [], {}]
    failures = []
    for v in cases:
        try:
            if not pred(v):
                failures.append({"input": str(v)[:30], "kind": "boundary"})
        except Exception as e:
            failures.append({"input": str(v)[:30], "kind": "exception", "error": str(e)[:50]})
    return failures

def attack_adversarial(pred, trials=200):
    failures = []
    for _ in range(trials):
        kind = random.choice(["int","float","str","list","dict"])
        if kind == "int": v = random.randint(-2**63, 2**63)
        elif kind == "float": v = random.uniform(-1e308, 1e308)
        elif kind == "str": v = "".join(random.choices("abc'\";<>", k=random.randint(0,10)))
        elif kind == "list": v = [random.random() for _ in range(random.randint(0,3))]
        else: v = {"k": random.random()}
        try:
            if not pred(v):
                failures.append({"input": str(v)[:30], "kind": kind})
                if len(failures) > 5: break
        except Exception as e:
            failures.append({"input": str(v)[:30], "kind": "exception", "error": str(e)[:50]})
            if len(failures) > 5: break
    return failures

def main():
    tests = {
        "positive": lambda x: isinstance(x,(int,float)) and not isinstance(x,bool) and x > 0,
        "not_none": lambda x: x is not None,
        "safe_str": lambda x: isinstance(x,str) and "<" not in x,
    }
    results = {}
    for name, pred in tests.items():
        r = {"boundary": attack_boundary(pred), "adversarial": attack_adversarial(pred)}
        n = len(r["boundary"]) + len(r["adversarial"])
        results[name] = {"failures": n, "sample": (r["boundary"] + r["adversarial"])[:2]}
    print(json.dumps(results, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
