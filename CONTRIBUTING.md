# Contributing to Django WebAssembly

Thank you for your interest in contributing to Django WebAssembly! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/m-butterfield/django_webassembly.git
cd django_webassembly

# Install dependencies
make install
# Or manually:
pip install -e ".[dev]"
npm install
```

### Development Workflow

```bash
# Start local development server
make serve
# Open http://localhost:8000

# After making changes to Django code, rebuild the wheel
make wheel

# Run tests
make test

# Format code
make fmt

# Run linters
make lint
```

## Code Style

### Python

- We use [Black](https://black.readthedocs.io/) for formatting
- We use [Ruff](https://docs.astral.sh/ruff/) for linting
- Line length: 100 characters
- Follow PEP 8 guidelines

### JavaScript

- We use [ESLint](https://eslint.org/) for linting
- Double quotes for strings
- Semicolons required
- 2-space indentation

## Testing

### Python Tests

```bash
# Run all Python tests
make test-py

# Run Django's test runner
python manage.py test django_webassembly.polls

# Run pytest
pytest tests/ -v
```

### E2E Tests

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run E2E tests
make test-e2e
# Or: npx playwright test
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`make test && make lint`)
5. Commit your changes with a descriptive message
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### PR Guidelines

- Keep PRs focused on a single change
- Include tests for new functionality
- Update documentation if needed
- Ensure CI passes before requesting review

## Architecture Overview

```
Browser Request → Service Worker → Pyodide (Python) → Django WSGI → Response
```

### Key Files

- `worker.js` - Service worker that intercepts requests and runs Python
- `init.py` - Python initialization script (runs migrations, creates users)
- `app.js` - Service worker registration and loading UI
- `django_webassembly/` - Django application code

### How It Works

1. User visits the page
2. `app.js` registers the service worker (`worker.js`)
3. Service worker loads Pyodide and installs Django wheel
4. `init.py` runs to set up Django
5. All subsequent requests are intercepted by the service worker
6. Requests are converted to Python and processed by Django

## Reporting Issues

When reporting issues, please include:

- Browser and version
- Steps to reproduce
- Expected vs actual behavior
- Console errors (if any)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
