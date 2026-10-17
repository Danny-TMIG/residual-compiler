# Contributing

## Setup

    python3 -m venv .venv && source .venv/bin/activate
    python3 -m pip install -e '.[test,dev]'
    pre-commit install

## Before opening a PR

    make lint
    make test

Both must pass. Keep diffs focused; one concern per PR.
