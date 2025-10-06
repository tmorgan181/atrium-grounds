# Atrium Grounds - Web Interface

Public web interface for exploring the Observatory conversation analysis API.

## Overview

A stateless web application that provides:
- **Instant demos**: Pre-cached conversation analysis examples (no signup required)
- **Live exploration**: Try real-time analysis with Observatory API
- **Progressive access**: Public → API Key → Partner tiers

## Quick Start

### Prerequisites

- Python 3.11+
- uv package manager
- Observatory service running at http://localhost:8000
- Observatory API key (for live demos)

### Setup

```bash
# Install dependencies
uv sync

# Configure Observatory connection
cp .env.example .env
# Edit .env and set OBSERVATORY_URL and OBSERVATORY_API_KEY

# Generate cached examples (first time only)
uv run python scripts/generate_examples.py

# Start development server
uv run uvicorn app.main:app --reload --port 8080
```

Visit http://localhost:8080

### Validation

```bash
# Run tests
uv run pytest

# Run quickstart validation (6 curl tests)
# See specs/006-unified-microservice-interface/quickstart.md
curl http://localhost:8080/
curl http://localhost:8080/examples/dialectic-simple
curl http://localhost:8080/api/health
```

## Architecture

- **FastAPI**: Async web framework (server-side rendering)
- **Jinja2**: HTML templates
- **httpx**: Observatory API client
- **Static JSON**: Cached demo results (no database)

**Key principle**: Stateless proxy to Observatory API

## Project Structure

```
app/
├── main.py              # FastAPI application
├── config.py            # Settings (Observatory URL, port)
├── client.py            # Observatory HTTP client
├── routers/
│   ├── pages.py         # HTML routes (/, /demo, /docs)
│   ├── examples.py      # Cached example loader
│   └── proxy.py         # Observatory API proxy
├── templates/
│   ├── base.html        # Layout
│   ├── index.html       # Landing page
│   ├── demo.html        # Demo interface
│   └── components/      # Reusable components
└── static/
    ├── css/             # Minimal styling
    └── examples/        # Cached JSON files

tests/
├── test_pages.py        # Page route tests
├── test_examples.py     # Example endpoint tests
├── test_proxy.py        # Proxy endpoint tests
└── test_integration.py  # Integration tests

scripts/
└── generate_examples.py # Example generator
```

## Development

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_pages.py

# With coverage
uv run pytest --cov=app
```

### TDD Workflow

This project follows Test-Driven Development:

1. Write tests first (tests should fail initially)
2. Validate TDD gate: `bash ../../scripts/validate-tdd-gate.sh`
3. Implement functionality (tests should pass)
4. Refactor if needed

### Adding New Examples

1. Add conversation to `specs/006-unified-microservice-interface/example-conversations.md`
2. Run generator: `uv run python scripts/generate_examples.py`
3. Verify: Check `app/static/examples/{id}.json` exists
4. Test: `curl http://localhost:8080/examples/{id}`

## Configuration

### Environment Variables

- `OBSERVATORY_URL`: Observatory API base URL (default: http://localhost:8000)
- `APP_HOST`: Web interface host (default: 0.0.0.0)
- `APP_PORT`: Web interface port (default: 8080)

### Example `.env`

```
OBSERVATORY_URL=http://localhost:8000
APP_HOST=0.0.0.0
APP_PORT=8080
```

## Performance

- **Cached demos**: <100ms (static JSON files)
- **Live demos**: <3s (depends on Observatory)
- **Concurrent users**: Designed for 100, comfortable with 10

## Deployment

### Docker

```bash
# Build image
docker build -t atrium-web-interface .

# Run container
docker run -p 8080:8080 \
  -e OBSERVATORY_URL=http://observatory:8000 \
  atrium-web-interface
```

### Production Checklist

- [ ] Environment variables configured
- [ ] Cached examples generated
- [ ] CORS origins set (if needed)
- [ ] Health check endpoint responding
- [ ] SSL/TLS configured (reverse proxy)

## Constitution Compliance

This service aligns with Atrium Grounds Constitution v1.3.1:

- **I. Language**: No technical jargon in public pages
- **II. Boundaries**: No private data access
- **III. Progressive Disclosure**: Public → API Key → Partner tiers
- **VI. Independence**: Separate service, clean API boundary
- **VIII. Pragmatism**: Minimal code (~500 LOC)

## Links

- **Specification**: `../../specs/006-unified-microservice-interface/spec.md`
- **Implementation Plan**: `../../specs/006-unified-microservice-interface/plan.md`
- **Tasks**: `../../specs/006-unified-microservice-interface/tasks.md`
- **Validation Guide**: `../../specs/006-unified-microservice-interface/quickstart.md`

## License

Part of the Atrium Grounds project.
