def flow(items, steps):
    cur = list(items)
    for step in steps:
        cur = [step(c) for c in cur]
    return cur
