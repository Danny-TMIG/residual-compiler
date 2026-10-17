def _match(pattern, value):
    if pattern == "*":
        return True
    return pattern == value


def evaluate(items, allowed):
    return [i for i in items if any(_match(p, i.get("id")) for p in allowed)]
