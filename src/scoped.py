from . import tools


def scoped(items, prefix="s:"):
    return {f"{prefix}{i}": tools.ident(i) for i in items}
