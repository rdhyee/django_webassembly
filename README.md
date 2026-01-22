# Django WebAssembly

Run Django applications entirely in the browser using WebAssembly.

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://django-webassembly.mattbutterfield.com)
[![Django](https://img.shields.io/badge/Django-5.2-092e20)](https://djangoproject.com)
[![Pyodide](https://img.shields.io/badge/Pyodide-0.29-3776ab)](https://pyodide.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**[Live Demo](https://django-webassembly.mattbutterfield.com)** - Give it some time to load (~20MB download on first visit).

## What is this?

This project demonstrates running a complete Django application in the browser without any server. Using [Pyodide](https://pyodide.org/) (Python compiled to WebAssembly) and [Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API), all HTTP requests are intercepted and processed by Django running client-side.

### Key Features

- **No server required** - Host on GitHub Pages or any static file hosting
- **Full Django functionality** - Admin panel, ORM, templates, forms all work
- **Local database** - SQLite runs in-browser, data persists locally
- **Offline capable** - Once loaded, works without internet connection

## How it Works

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser                                  │
│  ┌──────────────┐    ┌──────────────────────────────────────┐  │
│  │   Web Page   │───▶│         Service Worker               │  │
│  └──────────────┘    │  ┌────────────────────────────────┐  │  │
│                      │  │           Pyodide              │  │  │
│                      │  │  ┌──────────────────────────┐  │  │  │
│                      │  │  │      Django WSGI         │  │  │  │
│                      │  │  │  ┌────────┐ ┌────────┐   │  │  │  │
│                      │  │  │  │ Views  │ │ Models │   │  │  │  │
│                      │  │  │  └────────┘ └────────┘   │  │  │  │
│                      │  │  │       ┌──────────┐       │  │  │  │
│                      │  │  │       │  SQLite  │       │  │  │  │
│                      │  │  │       └──────────┘       │  │  │  │
│                      │  │  └──────────────────────────┘  │  │  │
│                      │  └────────────────────────────────┘  │  │
│                      └──────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

1. **Page loads** → Service worker registers
2. **Service worker installs** → Loads Pyodide, installs Django wheel
3. **Page reloads** → All requests now go through service worker
4. **Each request** → Converted to Python, processed by Django, response returned

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Poetry (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/m-butterfield/django_webassembly.git
cd django_webassembly

# Install dependencies
make install
# or manually:
poetry install
npm install
```

### Development

```bash
# Start local server
make serve
# or: python -m http.server 8000

# Open http://localhost:8000 in your browser
```

### Building

When you make changes to the Django application, you need to rebuild the wheel:

```bash
make wheel
```

Then refresh the page (you may need to clear the service worker in DevTools).

## Project Structure

```
django_webassembly/
├── app.js              # Service worker registration
├── worker.js           # Service worker (Pyodide + request handling)
├── init.py             # Python initialization script
├── index.html          # Loading page
├── django_webassembly/ # Django application
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│   └── polls/          # Example polls app
├── wheel/              # Built Python wheel
├── pyproject.toml      # Python dependencies
└── package.json        # Node.js dependencies
```

## Demo Credentials

- **Username:** `demo`
- **Password:** `demo`

These are created automatically on first load. Each user has their own isolated database in their browser.

## Browser Support

| Browser | Support |
|---------|---------|
| Chrome 80+ | ✅ Full |
| Firefox 78+ | ✅ Full |
| Safari 14+ | ✅ Full |
| Edge 80+ | ✅ Full |
| Mobile browsers | ⚠️ Limited (memory constraints) |

Requires: Service Workers, WebAssembly

## Use Cases

- **Demos & Portfolios** - Showcase Django projects without server costs
- **Education** - Learn Django without setting up a development environment
- **Prototyping** - Rapid iteration without deployment
- **Offline Apps** - Build apps that work without connectivity

## Limitations

- **Initial load time** - ~20MB download (Pyodide + packages)
- **Memory usage** - Full Python runtime in browser
- **No shared data** - Each user has their own local database
- **Some packages unavailable** - Not all Python packages work in Pyodide

## Development Commands

```bash
make help         # Show all available commands
make install      # Install dependencies
make serve        # Start development server
make wheel        # Build Python wheel
make fmt          # Format code (Black + ESLint)
make lint         # Run linters
make test         # Run tests
make clean        # Remove build artifacts
```

## Technical Details

### Stack

- **Django 5.2 LTS** - Python web framework
- **Pyodide 0.29** - Python runtime compiled to WebAssembly
- **WebTest** - WSGI testing library (provides request interface)
- **SQLite** - In-browser database

### Security Notes

This application runs entirely in the browser:
- The SECRET_KEY is hardcoded (intentional - no server-side secrets)
- Each user has isolated data (no cross-user access)
- No sensitive data leaves the browser

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE.txt](LICENSE.txt)

## Acknowledgments

- [Pyodide](https://pyodide.org/) - Python in the browser
- [WordPress Playground](https://developer.wordpress.org/playground/) - Inspiration for this approach
- [Django](https://djangoproject.com/) - The web framework for perfectionists with deadlines

## Related Projects

- [Pyodide](https://github.com/pyodide/pyodide) - Python distribution for browser/Node.js
- [JupyterLite](https://github.com/jupyterlite/jupyterlite) - Jupyter in the browser
- [PyScript](https://github.com/pyscript/pyscript) - Python in HTML
