def dispatch(items, handler):
    return [handler(i) for i in items]
