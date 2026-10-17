#!/usr/bin/env bash
# build.sh — one-shot build for the residual-compiler project.
# Usage: ./build.sh [--skip-pipeline] [--skip-tests]
set -euo pipefail

cd "$(dirname "$0")"
HERE="$(pwd)"

SKIP_PIPELINE=0
SKIP_TESTS=0
for arg in "$@"; do
  case "$arg" in
    --skip-pipeline) SKIP_PIPELINE=1 ;;
    --skip-tests)    SKIP_TESTS=1 ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

step() { printf '\n==> %s\n' "$*"; }
fail() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

# ---------- 1. Python environment ----------
step "python environment"
if [ ! -d .venv ]; then
  python3 -m venv .venv || fail "could not create .venv"
fi
# shellcheck disable=SC1091
. .venv/bin/activate
python -m pip install -q --upgrade pip
python -m pip install -q -e . || fail "pip install -e . failed (check pyproject.toml)"

# ---------- 2. Data artifacts ----------
step "data: residuals"
[ -f data/residual_register.md ] || fail "missing data/residual_register.md"
python -m src.parse_residuals data/residual_register.md

step "data: atlas"
if [ -f data/atlas/atlas.txt ]; then
  python -m src.parse_atlas data/atlas/atlas.txt
else
  python -m src.parse_atlas
fi

step "data: skills"
python -m src.seed_skills || fail "seed_skills failed — needs a __main__ block"

# ---------- 3. Pipeline ----------
if [ "$SKIP_PIPELINE" -eq 0 ]; then
  step "pipeline"
  bin/run-pipeline || fail "pipeline failed"
else
  step "pipeline (skipped)"
fi

# ---------- 4. Tests ----------
if [ "$SKIP_TESTS" -eq 0 ]; then
  step "tests"
  python -m pytest -q || fail "tests failed"
else
  step "tests (skipped)"
fi

# ---------- 5. Verify compiler contract ----------
step "contract check"
blocked=$("$HERE/.venv/bin/python" -m src.compile_cli "prove this program terminates" 2>&1 || true)
if printf '%s' "$blocked" | grep -qi 'blocked'; then
  echo "  ok: prove-terminates is blocked"
else
  echo "  WARN: prove-terminates was not blocked" >&2
  printf '%s
' "$blocked" | head -5 >&2
fi
allowed=$("$HERE/.venv/bin/python" -m src.compile_cli "search for TODOs in src/tools.py" 2>&1 || true)
if printf '%s' "$allowed" | grep -q '"allowed": *true'; then
  echo "  ok: benign query allowed"
else
  echo "  WARN: benign query not allowed" >&2
  printf '%s
' "$allowed" | head -5 >&2
fi

step "build OK"
echo "  commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'no git')"
echo "  files:  $(git ls-files 2>/dev/null | wc -l | tr -d ' ') tracked"
