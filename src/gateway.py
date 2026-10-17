import json
import os
import socket
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

LEDGER = Path("sovereign/manifold_ledger.jsonl")
app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "operational"}


@app.get("/manifold/state")
async def state():
    if not LEDGER.exists():
        raise HTTPException(404, "not initialized")
    latest = None
    for line in LEDGER.read_text().splitlines():
        if line.strip():
            latest = json.loads(line)
    if not latest:
        raise HTTPException(500, "empty")
    return JSONResponse(content=latest)


def main():
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", port))
    except OSError:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        print(f"[gateway] port busy, using {port}")
    finally:
        s.close()
    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
