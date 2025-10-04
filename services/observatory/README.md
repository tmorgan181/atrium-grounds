# Atrium Observatory Service

Conversation analysis API service providing pattern detection, theme extraction, and insights for human-AI dialogues.

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Redis (for job queue)
- Ollama with Observer model (for analysis)

### Installation

```bash
# Install dependencies with uv
cd services/observatory
uv sync

# Or install with dev dependencies
uv sync --dev
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_analyzer.py -v

# Run only unit tests
uv run pytest tests/unit/ -v

# Run only integration tests
uv run pytest tests/integration/ -v
```

### Development

```bash
# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Type check
uv run mypy app/

# Run development server
uv run uvicorn app.main:app --reload
```

### Docker

```bash
# Build and run with docker-compose
docker-compose up --build

# Run just the service
docker build -t observatory .
docker run -p 8000:8000 observatory
```

## Project Structure

```
services/observatory/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Core logic (analyzer, validator, jobs)
│   ├── models/          # Data models (Pydantic, SQLAlchemy)
│   ├── middleware/      # Auth, rate limiting
│   └── main.py          # FastAPI app
├── tests/
│   ├── unit/            # Unit tests
│   ├── contract/        # API contract tests
│   └── integration/     # End-to-end tests
├── examples/            # Curated conversation examples
├── pyproject.toml       # Project configuration
└── docker-compose.yml   # Docker setup
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key settings:
- `OLLAMA_BASE_URL`: Ollama server URL
- `DATABASE_URL`: SQLite/PostgreSQL connection
- `REDIS_URL`: Redis server for job queue
- Rate limits, TTLs, and analysis parameters

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for development guidelines.
