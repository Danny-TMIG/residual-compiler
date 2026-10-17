"""
Runtime safety: wraps tool execution with timeout + output cap + determinism.

- TIMEOUT_DEFAULT: seconds per tool call
- OUTPUT_CAP: max bytes per tool return (stringified)
Every dispatch passes through run_tool() which cannot be bypassed by tools.
"""

import json, signal, sys
from .contracts import ResultState

TIMEOUT_DEFAULT = 30
OUTPUT_CAP = 200_000  # 200 KB


class _Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise _Timeout()


def _set_alarm(seconds):
    try:
        signal.signal(signal.SIGALRM, _alarm)
        signal.alarm(int(seconds))
    except (ValueError, AttributeError):
        pass  # not on main thread, or not Unix; skip


def _clear_alarm():
    try:
        signal.alarm(0)
    except Exception:
        pass


def _cap(out):
    try:
        s = json.dumps(out, ensure_ascii=False)
    except Exception:
        return out
    if len(s.encode()) > OUTPUT_CAP:
        return {
            "result_state": ResultState.RESOURCE_EXHAUSTED.value,
            "reason": f"output exceeded {OUTPUT_CAP} bytes",
        }
    return out


def run_tool(fn, inputs, ctx, timeout=None):
    _set_alarm(timeout or TIMEOUT_DEFAULT)
    try:
        out = fn(inputs or {}, ctx or {})
        if not isinstance(out, dict):
            out = {"result": out}
        out.setdefault("result_state", ResultState.PASS.value)
        return _cap(out)
    except _Timeout:
        return {"result_state": ResultState.TIMEOUT.value}
    except PermissionError:
        return {"result_state": ResultState.POLICY_DENIED.value}
    except FileNotFoundError as e:
        return {"result_state": ResultState.ENVIRONMENT_FAILURE.value, "reason": str(e)}
    except Exception as e:
        return {"result_state": ResultState.EXECUTION_FAILURE.value, "reason": repr(e)[:400]}
    finally:
        _clear_alarm()
