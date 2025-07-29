SHELL := /bin/bash
.PHONY: setup all hooks check clean env build serve jupyter test

setup:
	./scripts/contributor_setup.sh

test:
	@source .venv/bin/activate; \
	echo "Running tests..."; \
	uv run pytest tests/ -v --cov=mkdocs_panzoom_plugin --cov-report=term-missing --cov-report=html --cov-report=xml

check: test
	@source .venv/bin/activate; \
	if [ -n "$$CI" ]; then \
		uvx --from 'pre-commit' pre-commit run --all-files --origin HEAD --source origin/HEAD; \
	else \
		uvx --from 'pre-commit' pre-commit run --all-files; \
	fi

clean:
	@echo "Cleaning up..."
	@find . -name '.venv' -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name 'build' -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name 'dist' -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name '*.egg-info' -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name '.pytest_cache' -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name '.mypy_cache' -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name '.ruff_cache' -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name 'site' -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name '*.pyc' -delete 2>/dev/null || true
	@echo "✓ Cleanup complete!"

env:
	@source .venv/bin/activate; \
	echo "Environment information:"
	@echo "Project root: $(shell pwd)"
	@echo -n "Python version: " && python --version 2>/dev/null || echo "Python not found"
	@echo -n "UV version: " && uv --version 2>/dev/null || echo "UV not found"
	@echo "Virtual environment: $${VIRTUAL_ENV:-Not activated}"
	@echo "UV project info:"
	@uv info 2>/dev/null || echo "No UV project found"
	@echo "UV lock status:"
	@test -f uv.lock && echo "✓ uv.lock exists" || echo "✗ uv.lock missing"
	@echo "UV cache info:"
	@uv cache dir 2>/dev/null || echo "UV cache directory not available"

build:
	@source .venv/bin/activate; \
	if [ -f "mkdocs.yml" ]; then \
		echo "Building documentation..."; \
		echo "Will generate static HTML in 'site' folder"; \
		uv run mkdocs build; \
		echo "✓ Documentation built!"; \
	else \
		echo "No mkdocs.yml found, skipping docs build."; \
	fi

serve:
	@source .venv/bin/activate; \
	echo "Starting documentation server..."; \
	uv run mkdocs serve

docs: build

all: check
hooks: check
