#!/usr/bin/env python3
"""sci.py — ISO/IEC 21031 Software Carbon Intensity."""

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"

# Inputs (fill these from real measurements; defaults are conservative).
# E: joules per resolved request, from a wall-meter or powermetrics.
# I: marginal carbon intensity gCO2e/kWh for your grid region (e.g. WattTime).
# M: embodied carbon of M4 Max (~300_000 gCO2e over 5y), divided by expected
#    lifetime requests. With 1 req/sec for 5y = 157_680_000 req -> 0.0019 g/req.
# R: number of resolved requests the run covers.
DEFAULTS = {
    "energy_j_per_request": 8.5,  # placeholder: MEASURE THIS
    "grid_gco2_per_kwh": 400.0,  # placeholder: query regional API
    "embodied_gco2_total": 300_000,  # M4 Max, published LCA order-of-mag
    "lifetime_requests": 157_680_000,
    "resolved_requests": 1,
}


def sci(inp):
    E_kwh = inp["energy_j_per_request"] / 3.6e6
    I = inp["grid_gco2_per_kwh"]
    M = inp["embodied_gco2_total"] / inp["lifetime_requests"]
    R = max(1, inp["resolved_requests"])
    g_per_req = (E_kwh * I + M) / R
    return {
        "standard": "ISO/IEC 21031",
        "sci_gco2e_per_request": round(g_per_req, 6),
        "components": {
            "E_kwh": E_kwh,
            "I_gco2_per_kwh": I,
            "M_gco2_per_request": round(M, 6),
            "R": R,
        },
        "inputs": inp,
        "measured": False,
        "note": "E and I are placeholders. Replace with wall-meter + grid API before claiming.",
        "ts": dt.datetime.now(dt.UTC).isoformat(),
    }


def main():
    out = sci(DEFAULTS)
    (APEX / "SCI.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
