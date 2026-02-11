.PHONY: help install test lint format clean build publish

help:
	@grep -E "^[a-zA-Z_-]+:.*?## .*$$" $(MAKEFILE_LIST) | sort | \
		awk "BEGIN {FS = \":.*?## \"}; {printf \"\033[36m%-15s\033[0m %s\n\", $$1, $$2}"

install:  ## Install package in development mode
	pip install -e ".[dev]"

test:  ## Run tests with coverage
	pytest tests/ -v --cov=api_toolkit --cov-report=term-missing

test-fast:  ## Run tests without coverage
	pytest tests/ -v -x

lint:  ## Run linters
	flake8 api_toolkit/ tests/ --max-line-length=100
	mypy api_toolkit/ --ignore-missing-imports

format:  ## Format code
	black api_toolkit/ tests/
	isort api_toolkit/ tests/

clean:  ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

build:  ## Build distribution packages
	python -m build

publish:  ## Publish to PyPI
	twine upload dist/*