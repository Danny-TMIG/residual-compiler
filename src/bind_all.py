def bind_all(items, handlers):
    out = {}
    for it in items:
        key = it.get("id") if isinstance(it, dict) else str(it)
        out[key] = {name: fn(it) for name, fn in handlers.items()}
    return out
