# Atrium Observatory Service

**Version**: 0.1.0 (Development)  
**Status**: Phase 1-2 Complete, Phase 3 In Progress

Conversation analysis API service providing pattern detection, theme extraction, and insights for human-AI dialogues.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Current State](#current-state)
- [API Key Management](#api-key-management)
- [Development](#development)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Production Deployment](#production-deployment)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **[uv](https://github.com/astral-sh/uv)** package manager
- **Ollama** with Observer model (for analysis)
- **Redis** (optional, for production)

### Installation

```bash
# Navigate to service directory
cd services/observatory

# Run automated setup
.\quick-start.ps1 setup

# Or manual setup
uv venv
uv pip install -e ".[dev]"
```

### Start the Server

```powershell
# Using quick-start script (recommended)
.\quick-start.ps1 serve

# Or manually
uv run uvicorn app.main:app --reload

# Custom port
.\quick-start.ps1 serve -Port 8001
```

### Test the Service

```powershell
# Run full test suite
.\quick-start.ps1 test

# NEW: Run specific test types (much faster!)
.\quick-start.ps1 test -Unit        # ~2 seconds
.\quick-start.ps1 test -Coverage    # With coverage report

# NEW: Code quality checks
.\quick-start.ps1 lint              # Check code style
.\quick-start.ps1 format            # Auto-format code
.\quick-start.ps1 check             # Lint + type check (pre-commit)

# Test health endpoint
.\quick-start.ps1 health

# Test analysis endpoint
.\quick-start.ps1 analyze

# Run complete demo
.\quick-start.ps1 demo
```

**Feature 002 Upgrade**: All commands now support `-Detail` flag for verbose output!

### Access Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Current State

### ✅ Phase 1.3 Complete - Database & Endpoints

- **Database**: SQLite with async SQLAlchemy
  - Analysis model with TTL support
  - 30-day result retention, 90-day metadata
  - Scheduled cleanup with APScheduler
  
- **API Endpoints**:
  - `POST /api/v1/analyze` - Submit conversation for analysis
  - `GET /api/v1/analyze/{id}` - Retrieve analysis results
  - `POST /api/v1/analyze/{id}/cancel` - Cancel ongoing analysis
  - `GET /health` - Service health check
  
- **Features**:
  - Async job management for analysis
  - TTL enforcement with automated cleanup
  - Comprehensive audit logging
  - Pattern detection (dialectic, sentiment, topics, dynamics)
  - Confidence scoring (0.0-1.0)

### ✅ Phase 2 Complete - Authentication & Rate Limiting

- **Authentication**:
  - Three-tier access control (public/api_key/partner)
  - Bearer token authentication
  - API key generation and validation
  - Secure hashing (SHA256 + salt)

- **Rate Limiting**:
  - Public: 10 requests/minute
  - API Key: 60 requests/minute
  - Partner: 600 requests/minute
  - Rate limit headers (X-RateLimit-*)
  - 429 Too Many Requests enforcement

### ⚡ NEW - Developer Experience Enhancements (Feature 002)

**Faster Development Cycle**:
- **Test Filtering**: Run unit tests in ~2 seconds (60x faster than full suite)
- **Verbosity Control**: Minimal output by default, `-Detail` for diagnostics
- **Code Quality**: Integrated linting, formatting, and type checking
- **Clean Logging**: ANSI-free output for Windows PowerShell 5.1

**Key Features**:
```powershell
# Fast iteration
.\quick-start.ps1 test -Unit          # 60x faster

# Quality checks
.\quick-start.ps1 check               # Lint + type check

# Clean output
.\quick-start.ps1 setup               # ~8 lines vs 100+ before
.\quick-start.ps1 setup -Detail       # Full diagnostics when needed

# Windows compatibility
.\quick-start.ps1 serve -Clean        # ANSI-free logs
```

**Performance**: <100ms overhead, <5 seconds to scan output ✅

- **Metrics**: `GET /metrics` (authenticated)
  - Current tier information
  - Rate limit configuration
  - Database statistics
  - Usage tracking

### 🔄 Phase 3 In Progress - Batch Processing

- Batch analysis endpoints
- Redis job queue
- Webhook notifications

### ⏳ Phase 4-5 Planned

- Web interface for key management
- Example conversation library
- Production deployment infrastructure
- OAuth2 for partner tier
- Database-backed API key management

---

## API Key Management

### Development (Current State)

**Storage**: In-memory dictionary (ephemeral, resets on server restart)  
**Purpose**: Local development and testing only

#### Quick Method: Use the Script! ⚡

```powershell
# One command to generate and register keys
.\quick-start.ps1 keys
```

This will:
- Generate a development API key (60 req/min)
- Generate a partner API key (600 req/min)
- Save keys to `dev-api-keys.txt`
- Create `register_dev_keys.py` for auto-registration
- Show usage examples

**Output includes**:
- Both keys displayed clearly
- PowerShell usage examples
- Copy-paste ready commands
- Auto-registration instructions

#### Manual Generation (Alternative)

**Option 1: Python REPL** (Quick Test)
```powershell
.\.venv\Scripts\python.exe

# In Python:
>>> from app.middleware.auth import generate_api_key, register_api_key
>>> 
>>> api_key = generate_api_key()
>>> print(f"Your API Key: {api_key}")
>>> 
>>> # Register it (tier: 'api_key' or 'partner')
>>> register_api_key(api_key, tier="api_key")
>>> 
>>> # Key is now active until server restarts
```

**Option 2: Startup Script** (Persistent Dev Keys)

Create `services/observatory/register_dev_keys.py`:
```python
"""Register development API keys on startup."""
from app.middleware.auth import register_api_key

# Development keys (replace with your own)
DEV_KEY = "dev_test_key_12345678901234567890"
PARTNER_KEY = "partner_key_09876543210987654321"

register_api_key(DEV_KEY, tier="api_key")
register_api_key(PARTNER_KEY, tier="partner")

print(f"✓ API Key registered (60 req/min)")
print(f"✓ Partner Key registered (600 req/min)")
```

Import in `app/main.py` after app initialization:
```python
# Development key registration
if settings.environment == "development":
    import register_dev_keys
```

#### Use Your API Key

**PowerShell**:
```powershell
$apiKey = "your_api_key_here"
$headers = @{
    "Authorization" = "Bearer $apiKey"
    "Content-Type" = "application/json"
}

# Access metrics (requires auth)
Invoke-WebRequest -Uri "http://localhost:8000/metrics" -Headers $headers

# Submit analysis with higher rate limits
$body = @{
    conversation_text = "Human: Hello\nAI: Hi there!"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/analyze" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

**cURL**:
```bash
# Check metrics
curl -H "Authorization: Bearer your_api_key_here" \
     http://localhost:8000/metrics

# Submit analysis
curl -X POST http://localhost:8000/api/v1/analyze \
     -H "Authorization: Bearer your_api_key_here" \
     -H "Content-Type: application/json" \
     -d '{"conversation_text": "Human: Hello\nAI: Hi there!"}'
```

**Python (httpx)**:
```python
import httpx

async with httpx.AsyncClient() as client:
    headers = {"Authorization": "Bearer your_api_key_here"}
    
    response = await client.post(
        "http://localhost:8000/api/v1/analyze",
        headers=headers,
        json={"conversation_text": "Human: Hello\nAI: Hi there!"}
    )
    
    print(response.json())
```

### Production (Phase 5 Planned)

**Storage**: PostgreSQL with web-based management UI

**User Flow**:
1. Visit `/register` and create account
2. Email verification
3. Auto-generated first API key (shown once)
4. Manage keys via `/dashboard`:
   - Generate new keys with custom names
   - Set expiration dates
   - View usage statistics
   - Revoke compromised keys

**Admin Flow**:
```bash
# Create key via admin API
POST /admin/api-keys
{
  "name": "Production Key",
  "tier": "api_key",
  "expires_days": 365
}

# Returns key once (never shown again)
{
  "api_key": "generated_key_here",
  "key_id": "uuid",
  "expires_at": "2026-01-01T00:00:00Z"
}
```

**Database Schema** (planned):
```python
class ApiKey(Base):
    id: UUID
    key_hash: str (SHA256)
    name: str
    tier: str (api_key, partner)
    created_at: datetime
    expires_at: datetime | None
    last_used_at: datetime | None
    is_active: bool
    request_count: int
    owner_email: str
```

---

## Development

### Quick-Start Script

The `quick-start.ps1` script provides a professional developer experience:

```powershell
# Setup
.\quick-start.ps1 setup       # Install dependencies
.\quick-start.ps1 clean       # Clean environment

# API Keys (NEW!)
.\quick-start.ps1 keys        # Generate & register API keys

# Testing
.\quick-start.ps1 test        # Run all tests
.\quick-start.ps1 health      # Test health endpoint
.\quick-start.ps1 analyze     # Test analysis endpoint

# Server
.\quick-start.ps1 serve       # Start dev server
.\quick-start.ps1 serve -Port 8001  # Custom port

# Demo
.\quick-start.ps1 demo        # Full demonstration

# Help
.\quick-start.ps1 help        # Show all options
```

### Manual Development

```bash
# Lint code
uv run ruff check .
uv run ruff format .

# Type check
uv run mypy app/

# Run specific tests
uv run pytest tests/unit/test_analyzer.py -v
uv run pytest tests/integration/ -v

# With coverage
uv run pytest --cov=app --cov-report=term-missing

# Development server with auto-reload
uv run uvicorn app.main:app --reload --port 8000
```

---

## Testing

### Test Structure

```
tests/
├── unit/              # Unit tests (27 passing)
│   ├── test_analyzer.py      # Pattern analysis (9 tests)
│   ├── test_validator.py     # Input validation (13 tests)
│   ├── test_jobs.py          # Job management
│   ├── test_database.py      # Database models (7 tests)
│   ├── test_ttl.py           # TTL enforcement (6 tests)
│   ├── test_auth.py          # Authentication (6 tests)
│   └── test_ratelimit.py     # Rate limiting (8 tests)
├── contract/          # API contract tests
│   ├── test_analyze_post.py
│   ├── test_analyze_get.py
│   ├── test_analyze_cancel.py
│   └── test_analyze_batch.py
└── integration/       # End-to-end tests
    ├── test_analysis_flow.py
    └── test_auth_public.py
```

### Test Without Authentication (Public Tier)

```powershell
# Health check (no auth, 10 req/min limit)
Invoke-WebRequest http://localhost:8000/health

# Submit analysis (public tier)
$body = @{
    conversation_text = "Human: Test\nAI: Response"
    options = @{
        pattern_types = @("dialectic", "sentiment")
        include_insights = $true
    }
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/analyze" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### Test With Authentication

```powershell
# Generate key first (see API Key Management section)

$headers = @{"Authorization" = "Bearer your_key_here"}

# Higher rate limits (60/min vs 10/min)
1..15 | ForEach-Object {
    Invoke-WebRequest -Uri "http://localhost:8000/health" -Headers $headers
}

# Access metrics (requires auth)
Invoke-WebRequest -Uri "http://localhost:8000/metrics" -Headers $headers
```

---

## Project Structure

```
services/observatory/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── analyze.py      # Analysis endpoints
│   │       ├── health.py       # Health & metrics
│   │       └── batch.py        # Batch processing
│   ├── core/
│   │   ├── analyzer.py         # Pattern analysis engine
│   │   ├── validator.py        # Input validation
│   │   ├── jobs.py            # Job management
│   │   ├── config.py          # Configuration
│   │   └── logging.py         # Audit logging
│   ├── models/
│   │   ├── database.py        # SQLAlchemy models
│   │   └── schemas.py         # Pydantic schemas
│   ├── middleware/
│   │   ├── auth.py           # Authentication
│   │   └── ratelimit.py      # Rate limiting
│   └── main.py               # FastAPI app
├── tests/                    # Test suite
├── examples/                 # Sample conversations
├── data/                    # SQLite database (gitignored)
├── quick-start.ps1          # Developer tool
├── pyproject.toml           # Project config
├── docker-compose.yml       # Docker setup
├── Dockerfile
└── README.md               # This file
```

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env`:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite:///./data/observatory.db
# Production: postgresql://user:pass@host/db

# Redis (optional in dev, required in production)
REDIS_URL=redis://localhost:6379

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=observer

# Security
API_KEY_SALT=change-this-in-production-to-random-string

# Rate Limits (requests per minute)
RATE_LIMIT_PUBLIC=10
RATE_LIMIT_API_KEY=60
RATE_LIMIT_PARTNER=600

# TTL (days)
TTL_RESULTS=30
TTL_METADATA=90

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Analysis
MAX_CONVERSATION_LENGTH=10000
ANALYSIS_TIMEOUT=30
MAX_BATCH_SIZE=1000
```

### Settings Reference

| Setting | Default | Description |
|---------|---------|-------------|
| `database_url` | `sqlite:///./data/observatory.db` | Database connection string |
| `redis_url` | `redis://localhost:6379` | Redis for rate limiting (Phase 5) |
| `ollama_base_url` | `http://localhost:11434` | Ollama server URL |
| `ollama_model` | `observer` | Model for analysis |
| `rate_limit_public` | `10` | Public tier requests/minute |
| `rate_limit_api_key` | `60` | API key tier requests/minute |
| `rate_limit_partner` | `600` | Partner tier requests/minute |
| `ttl_results` | `30` | Days to retain analysis results |
| `ttl_metadata` | `90` | Days to retain analysis metadata |
| `max_conversation_length` | `10000` | Max conversation characters |
| `analysis_timeout` | `30` | Analysis timeout (seconds) |

---

## Production Deployment

### Docker Compose (Development)

```bash
# Start all services
docker-compose up --build

# Services:
# - Observatory API (port 8000)
# - Redis (port 6379)
# - SQLite database
```

### Docker Compose (Production)

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  observatory:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres/observatory
      - REDIS_URL=redis://redis:6379
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - postgres
      - redis
      - ollama
    restart: unless-stopped
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: observatory
      POSTGRES_USER: observatory_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
  
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - observatory
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  ollama_data:
```

### Deployment Steps

```bash
# 1. Clone repository
git clone https://github.com/tmorgan181/atrium-grounds.git
cd atrium-grounds/services/observatory

# 2. Configure environment
cp .env.example .env
# Edit .env with production values

# 3. Build and start
docker-compose -f docker-compose.production.yml up -d

# 4. Run database migrations (when available)
docker-compose exec observatory alembic upgrade head

# 5. Create admin user (Phase 5)
docker-compose exec observatory python scripts/create_admin.py

# 6. Verify health
curl https://your-domain.com/health
```

### Scaling

For load balancing across multiple instances:

```yaml
# docker-compose.production.yml (excerpt)
observatory:
  build: .
  deploy:
    replicas: 3  # Run 3 instances
    resources:
      limits:
        cpus: '1'
        memory: 2G
```

With nginx as load balancer:

```nginx
# nginx.conf
upstream observatory_backend {
    least_conn;
    server observatory_1:8000;
    server observatory_2:8000;
    server observatory_3:8000;
}

server {
    listen 443 ssl http2;
    server_name observatory.atrium.ai;
    
    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    
    location / {
        proxy_pass http://observatory_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Architecture Evolution

**Development (Current)**:
```
Client → FastAPI (single instance)
         ├─ SQLite (local DB)
         ├─ In-memory rate limits
         ├─ In-memory API keys
         └─ Ollama (local)
```

**Production (Phase 5)**:
```
Internet → nginx (HTTPS, load balancer)
           ├─ Observatory Instance #1
           ├─ Observatory Instance #2
           └─ Observatory Instance #3
                ├─ PostgreSQL (keys, results, users)
                ├─ Redis (rate limits, sessions)
                └─ Ollama (AI analysis cluster)
```

---

## API Documentation

### Core Endpoints

#### POST /api/v1/analyze
Submit a conversation for analysis.

**Request**:
```json
{
  "conversation_text": "Human: Hello\nAI: Hi there!",
  "options": {
    "pattern_types": ["dialectic", "sentiment", "topics", "dynamics"],
    "include_insights": true
  }
}
```

**Response** (202 Accepted):
```json
{
  "id": "uuid",
  "status": "pending",
  "created_at": "2025-10-04T10:00:00Z",
  "expires_at": "2025-11-03T10:00:00Z"
}
```

#### GET /api/v1/analyze/{id}
Retrieve analysis results.

**Response** (200 OK):
```json
{
  "id": "uuid",
  "status": "completed",
  "observer_output": "Analysis text...",
  "patterns": {
    "dialectic": [...],
    "sentiment": {...},
    "topics": [...],
    "dynamics": {...}
  },
  "confidence_score": 0.85,
  "processing_time": 12.5,
  "created_at": "2025-10-04T10:00:00Z",
  "expires_at": "2025-11-03T10:00:00Z"
}
```

#### GET /health
Service health check.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-10-04T10:00:00Z"
}
```

#### GET /metrics
Usage metrics (requires authentication).

**Response** (200 OK):
```json
{
  "tier": "api_key",
  "rate_limits": {
    "requests_per_minute": 60,
    "requests_per_day": 5000
  },
  "database_stats": {
    "total_analyses": 1234,
    "completed_analyses": 1200,
    "avg_processing_time": 15.3
  },
  "timestamp": "2025-10-04T10:00:00Z"
}
```

### Rate Limit Headers

All responses include:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1728048000
```

When rate limited (429):
```
Retry-After: 42
```

---

## Troubleshooting

### Server Won't Start

```powershell
# Check for port conflicts
netstat -ano | findstr :8000

# Try different port
.\quick-start.ps1 serve -Port 8001

# Check logs
uv run uvicorn app.main:app --log-level debug
```

### API Key Not Working

- **Keys are ephemeral**: Regenerate after server restart
- **Check format**: `Authorization: Bearer <key>`
- **Verify registration**: Ensure `register_api_key()` was called
- **Check tier**: Use correct endpoint for tier (e.g., `/metrics` requires auth)

### Rate Limit Too Strict

For development, temporarily modify `app/core/config.py`:
```python
rate_limit_public: int = 1000  # Increase for testing
```

Or use API key for higher limits (60/min vs 10/min).

### Database Issues

```powershell
# Reset database
Remove-Item data/observatory.db
.\quick-start.ps1 serve  # Recreates tables

# Check database
sqlite3 data/observatory.db ".tables"
```

### Tests Failing

```powershell
# Clean environment
.\quick-start.ps1 clean
.\quick-start.ps1 setup

# Run specific test
uv run pytest tests/unit/test_database.py -v

# Verbose output
uv run pytest -vv --tb=short
```

### Complete Reset

```powershell
# Nuclear option - remove everything
.\quick-start.ps1 clean

# Fresh start
.\quick-start.ps1 setup
.\quick-start.ps1 test
.\quick-start.ps1 serve
```

---

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for development guidelines and [constitution.md](../../.specify/memory/constitution.md) for architectural principles.

### Development Workflow

1. Create feature branch from `main`
2. Make changes with tests (TDD preferred)
3. Run tests: `.\quick-start.ps1 test`
4. Lint code: `uv run ruff check .`
5. Submit PR with clear description

### Commit Convention

```
feat(001): Add feature
fix(001): Fix bug
docs(001): Update documentation
test(001): Add tests
chore(001): Maintenance task
```

Include model attribution:
```
Co-authored-by: GitHub Copilot CLI <noreply@github.com>
Model: claude-sonnet-4.5 via GitHub Copilot CLI
```

---

## License

See [LICENSE](../../LICENSE) for details.

---

## Additional Resources

- **OpenAPI Docs**: http://localhost:8000/docs (interactive)
- **ReDoc**: http://localhost:8000/redoc (alternative)
- **Project Repository**: https://github.com/tmorgan181/atrium-grounds
- **Issues**: Create with `[Observatory]` prefix
- **Constitution**: `.specify/memory/constitution.md`
- **Spec**: `specs/001-atrium-observatory-service/spec.md`

---

**Maintainers**: Claude (Primary), Copilot (Secondary)  
**Phase**: 2 Complete (Auth & Rate Limiting)  
**Next**: Phase 3 (Batch Processing)  
**Last Updated**: 2025-10-04
