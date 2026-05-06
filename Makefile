.PHONY: install install-dev clean runserver

install:
	uv sync

install-dev:
	uv sync --dev

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

runserver:
	uv run python -m src.simple_api