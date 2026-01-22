.PHONY: help install wheel fmt lint test clean serve update-deps

# Default target
help:
	@echo "Django WebAssembly - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install all dependencies (Python + Node)"
	@echo "  make update-deps  - Update all dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make serve        - Start local development server"
	@echo "  make wheel        - Build the Python wheel for browser deployment"
	@echo "  make fmt          - Format all code (Python + JS)"
	@echo "  make lint         - Run linters (Python + JS)"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-py      - Run Python tests only"
	@echo "  make test-e2e     - Run end-to-end browser tests"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Remove build artifacts"

# Install dependencies
install:
	poetry install
	npm install

# Update dependencies
update-deps:
	poetry update
	npm update

# Format code
fmt:
	poetry run black .
	poetry run ruff check --fix .
	npm run lint:fix || true

# Run linters
lint:
	poetry run black --check .
	poetry run ruff check .
	npm run lint

# Build the wheel
wheel: clean-wheel
	pip wheel . --no-deps -w wheel
	@echo "Wheel built successfully"
	@ls -la wheel/

clean-wheel:
	rm -rf wheel/*.whl

# Run tests
test: test-py

test-py:
	poetry run pytest

test-e2e:
	npm run test

# Start development server
serve:
	@echo "Starting development server at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	python -m http.server 8000

# Clean build artifacts
clean:
	rm -rf wheel/*.whl
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf django_webassembly/__pycache__
	rm -rf django_webassembly/polls/__pycache__
	rm -rf .ruff_cache
	rm -rf node_modules/.cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
