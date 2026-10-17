.PHONY: seed test lint fmt verify health clean archive

seed:
	python -m src.cli seed

test:
	pytest -q

lint:
	ruff check src tests

fmt:
	ruff format src tests
	black --check src tests 2>/dev/null || true

verify:
	python -m src.cli verify
	python -m src.policy_builder_cli validate
	[ -z "$$(ls -t bundles/*.json 2>/dev/null | head -1)" ] || python -m src.cli verify-bundle "$$(ls -t bundles/*.json | head -1)"

health:
	python -m src.cli health

archive:
	@echo "use ./scripts/archive.sh"

clean:
	rm -rf .artifacts .state artifacts state checkpoints bundles evidence.log evidence.log.prev
	rm -f data/skills.sqlite data/atlas/atlas.sqlite data/atlas/atlas.jsonl skills.sqlite atlas.sqlite atlas.jsonl
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

# ---- data targets (regenerable) ----
PYTHON ?= /tmp/test/.venv/bin/python
DATA   := data

.PHONY: data
data: $(DATA)/residuals.sqlite $(DATA)/skills.sqlite $(DATA)/atlas/atlas.sqlite

$(DATA)/residuals.sqlite: $(DATA)/residual_register.md src/parse_residuals.py
	$(PYTHON) -m src.parse_residuals $<

$(DATA)/skills.sqlite: src/seed_skills.py src/contracts.py
	$(PYTHON) -c "import src.seed_skills as s; s.main()"

$(DATA)/atlas/atlas.sqlite: src/parse_atlas.py $(DATA)/atlas/atlas.txt
	$(PYTHON) -m src.parse_atlas $(DATA)/atlas/atlas.txt
