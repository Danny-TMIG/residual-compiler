import hashlib
import json


def bundle(items):
    payload = json.dumps(items, sort_keys=True, separators=(",", ":")).encode()
    return {"items": items, "sha256": hashlib.sha256(payload).hexdigest()}
