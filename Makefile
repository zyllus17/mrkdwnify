.PHONY: install test lint format typecheck check build clean

install:
	uv sync

test:
	uv run pytest tests/

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

typecheck:
	uv run mypy src/

check: lint typecheck test

build:
	uv run python -m build

clean:
	rm -rf dist/ build/ .eggs/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -f .coverage coverage.xml
