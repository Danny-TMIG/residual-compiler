#!/usr/bin/env python3
import json, math, sys

def fft(x):
    n = len(x)
    if n <= 1:
        return [complex(v) for v in x]
    even = fft(x[0::2])
    odd = fft(x[1::2])
    out = [0j] * n
    for k in range(n // 2):
        t = complex(math.cos(-2*math.pi*k/n), math.sin(-2*math.pi*k/n)) * odd[k]
        out[k] = even[k] + t
        out[k + n//2] = even[k] - t
    return out

def analyze(signal, f_max=0.4):
    n = len(signal)
    if n == 0:
        return {"error": "empty"}
    spectrum = fft(signal)
    power = [abs(c)**2 for c in spectrum]
    total = sum(power)
    if total == 0:
        return {"error": "zero power"}
    cutoff = int(n * f_max)
    bandwidth = sum(power[cutoff:]) / total
    log_sum = sum(math.log(p + 1e-12) for p in power) / n
    flatness = math.exp(log_sum) / (total / n)
    f0 = max(range(n), key=lambda i: power[i])
    harmonics = sum(power[f0*k] for k in range(2, 6) if f0*k < n)
    thd = harmonics / power[f0] if power[f0] > 0 else 0
    aliasing = sum(power[n//2:]) / total
    verdict = "pass"
    if bandwidth > 0.1:  verdict = "refuted:bandwidth"
    elif flatness < 0.5: verdict = "refuted:flatness"
    elif thd > 0.05:     verdict = "refuted:thd"
    elif aliasing > 0.1: verdict = "refuted:aliasing"
    return {"bandwidth": round(bandwidth,4), "flatness": round(flatness,4),
            "thd": round(thd,4), "aliasing": round(aliasing,4), "verdict": verdict}

def main():
    n = 64
    signal = [math.sin(2 * math.pi * 4 * i / n) for i in range(n)]
    out = analyze(signal)
    print(json.dumps(out, indent=2))
    return 0 if out.get("verdict") == "pass" else 1

if __name__ == "__main__":
    sys.exit(main())
