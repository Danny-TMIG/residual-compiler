def audit(items):
    seen, problems = set(), []
    for i, it in enumerate(items):
        if not it.get("id"):
            problems.append({"index": i, "issue": "missing id"})
        elif it["id"] in seen:
            problems.append({"index": i, "issue": "duplicate id", "id": it["id"]})
        else:
            seen.add(it["id"])
    return problems
