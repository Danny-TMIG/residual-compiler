def compile_task(spec):
    if not isinstance(spec, dict):
        raise TypeError("spec must be dict")
    return {
        "id": spec.get("id", "anonymous"),
        "residuals": list(spec.get("residuals", [])),
        "compiled": True,
    }
