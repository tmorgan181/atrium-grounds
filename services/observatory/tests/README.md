# Observatory Service - Test Strategy

**Purpose**: Clear documentation of test organization, execution, and current limitations

---

## Test Organization

### Directory Structure

```
tests/
├── unit/                    # Fast, isolated unit tests (no external dependencies)
│   ├── test_analyzer.py     # Core analysis logic
│   ├── test_auth.py         # API key generation/validation
│   ├── test_database.py     # Database models
│   ├── test_export.py       # Export functionality
│   ├── test_jobs.py         # Job manager (⚠️ some skipped - timing issues)
│   ├── test_queue.py        # ⚠️ SKIPPED - requires Redis
│   ├── test_ratelimit.py    # Rate limiting logic
│   ├── test_ttl.py          # TTL/cleanup logic
│   └── test_validator.py    # Input validation
├── contract/                # API contract tests (require running server)
│   ├── test_analyze*.py     # Analysis endpoint tests
│   └── test_examples*.py    # Example data endpoint tests
├── integration/             # Full integration tests (all services)
│   └── (future)
├── conftest.py              # Shared pytest fixtures
└── README.md                # This file
```

---

## Test Categories

### Unit Tests (`tests/unit/`)

**What**: Test individual components in isolation
**Dependencies**: None (or mocked)
**Speed**: Fast (~2 seconds for 58 tests)
**Run**: `pytest tests/unit`

**Characteristics**:
- No external services (database is in-memory SQLite)
- No network calls
- Deterministic results
- Fast feedback loop

**Current Status**: ✅ 58 passing, 20 skipped

**Skipped Tests**:
- `test_queue.py` - All tests (requires Redis, should be integration tests)
- `test_jobs.py` - Async timing tests (can hang in test runner)

### Contract Tests (`tests/contract/`)

**What**: Test API contracts and HTTP interfaces
**Dependencies**: Running Observatory server
**Speed**: Medium (~10-30 seconds)
**Run**: `pytest tests/contract`

**Characteristics**:
- Require server on localhost:8000
- Test request/response formats
- Validate HTTP status codes
- Check API contracts

**Current Status**: ⚠️ Some require Redis for batch endpoints

### Integration Tests (`tests/integration/`)

**What**: Test full system with all dependencies
**Dependencies**: Observatory + Ollama + Redis
**Speed**: Slow (minutes)
**Run**: `pytest tests/integration`

**Status**: 🚧 Not yet implemented

---

## Running Tests

### Quick Commands

```powershell
# All unit tests (fast, no dependencies)
.\quick-start.ps1 test

# Or directly with pytest
uv run pytest tests/unit

# Specific test file
uv run pytest tests/unit/test_analyzer.py

# Specific test function
uv run pytest tests/unit/test_analyzer.py::test_analyze_conversation

# With verbose output
uv run pytest tests/unit -v

# With coverage report
uv run pytest tests/unit --cov=app --cov-report=html
```

### Test Filtering (Planned)

```powershell
# Fast unit tests only (current default)
.\quick-start.ps1 test -Unit

# Contract tests (requires server)
.\quick-start.ps1 test -Contract

# Integration tests (requires all services)
.\quick-start.ps1 test -Integration

# Quick essential tests only
.\quick-start.ps1 test -Quick

# With coverage report
.\quick-start.ps1 test -Coverage

# Watch mode (auto-rerun on changes)
.\quick-start.ps1 test -Watch
```

---

## Current Issues & Workarounds

### Issue 1: Queue Tests Require Redis

**Problem**: `tests/unit/test_queue.py` tests Redis job queue but is in unit tests
**Impact**: 10 tests skipped
**Why**: These are actually integration tests misplaced in unit suite

**Workaround**: Tests are marked with `@pytest.mark.skip`

**Proper Fix**:
1. Move to `tests/integration/test_queue.py`
2. Add Redis fixture to `conftest.py`
3. Document Redis setup in integration test docs
4. Run only when Redis is available

**Example Redis Setup**:
```python
# conftest.py
@pytest.fixture
async def redis_queue():
    """Redis job queue for integration tests."""
    # Check if Redis is available
    try:
        queue = JobQueue()
        yield queue
        await queue.shutdown()
    except ConnectionError:
        pytest.skip("Redis not available")
```

### Issue 2: Job Manager Async Timing Issues

**Problem**: Tests in `test_jobs.py` with `asyncio.sleep()` can hang in pytest
**Impact**: 10 tests skipped
**Why**: Async timing tests are fragile in test environments

**Skipped Tests**:
- `test_cancel_job` - 10s sleep, cancellation timing
- `test_cancel_completed_job` - Race condition with completion
- `test_job_result_retrieval` - Async result retrieval timing
- `test_job_error_handling` - Error propagation timing
- `test_multiple_concurrent_jobs` - Concurrent job timing
- `test_job_timeout` - Timeout handling (100s sleep)

**Proper Fix Options**:

**Option A: Mock time** (recommended)
```python
import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_cancel_job_mocked(job_manager):
    """Test job cancellation with mocked sleep."""
    with patch('asyncio.sleep', return_value=None):
        # Test runs instantly, no actual waiting
        ...
```

**Option B: Use asyncio.wait_for with shorter timeouts**
```python
@pytest.mark.asyncio
async def test_cancel_job(job_manager):
    async def long_task():
        await asyncio.sleep(0.1)  # Short enough for tests
        return {"result": "done"}
    
    job_id = await job_manager.create_job(long_task)
    await asyncio.sleep(0.01)  # Just enough to start
    result = await job_manager.cancel_job(job_id)
    assert result is True
```

**Option C: Move to integration tests**
Accept these as slow tests and run them separately

### Issue 3: Contract Tests Mix Unit and Integration

**Problem**: Some contract tests require Redis (batch endpoints)
**Impact**: Tests fail without Redis running
**Why**: Batch processing uses Redis queue

**Workaround**: Skip tests when Redis unavailable

**Proper Fix**:
```python
# tests/contract/test_analyze_batch.py
@pytest.mark.redis_required
async def test_batch_submit_success(client, api_key):
    """Test batch submission (requires Redis)."""
    ...

# conftest.py
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "redis_required: test requires Redis to be running"
    )

# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
markers = [
    "redis_required: mark test as requiring Redis",
]

# Run without Redis tests
pytest -m "not redis_required"
```

---

## Test Configuration

### pytest.ini / pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"

# Markers
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "redis_required: test requires Redis",
    "ollama_required: test requires Ollama",
    "integration: integration test requiring all services",
]

# Coverage
addopts = [
    "--strict-markers",
    "--strict-config",
    "--tb=short",
]
```

### Running Tests with Markers

```powershell
# Skip slow tests
uv run pytest -m "not slow"

# Run only Redis tests (when Redis is up)
uv run pytest -m "redis_required"

# Skip integration tests
uv run pytest -m "not integration"

# Run only unit tests (no external dependencies)
uv run pytest tests/unit -m "not redis_required"
```

---

## Writing New Tests

### Unit Test Template

```python
"""Unit tests for [module/component]."""

import pytest
from app.module import Component


@pytest.fixture
def component():
    """Create component instance for testing."""
    return Component()


def test_basic_functionality(component):
    """Test basic operation."""
    result = component.do_something("input")
    assert result == "expected"


def test_edge_case_empty_input(component):
    """Test handling of empty input."""
    with pytest.raises(ValueError, match="cannot be empty"):
        component.do_something("")


@pytest.mark.asyncio
async def test_async_operation(component):
    """Test async functionality."""
    result = await component.async_method()
    assert result is not None
```

### Contract Test Template

```python
"""Contract tests for [endpoint]."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_endpoint_success(client: AsyncClient, api_key: str):
    """Test successful endpoint call."""
    response = await client.post(
        "/api/v1/endpoint",
        headers={"X-API-Key": api_key},
        json={"data": "value"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_endpoint_auth_required(client: AsyncClient):
    """Test endpoint requires authentication."""
    response = await client.post(
        "/api/v1/endpoint",
        json={"data": "value"}
    )
    
    assert response.status_code == 401
    assert "API key required" in response.json()["detail"]
```

---

## Test Fixtures

### Available Fixtures (conftest.py)

- `test_db_session` - In-memory SQLite database session
- `client` - Async HTTP client for contract tests
- `api_key` - Valid API key for authenticated tests
- `sample_conversation` - Example conversation data

### Adding New Fixtures

```python
# tests/conftest.py
import pytest


@pytest.fixture
async def your_fixture():
    """Description of what this fixture provides."""
    # Setup
    resource = create_resource()
    
    yield resource
    
    # Teardown
    await resource.cleanup()
```

---

## Coverage Reports

### Generate Coverage

```powershell
# HTML report (opens in browser)
uv run pytest tests/unit --cov=app --cov-report=html
Start-Process htmlcov/index.html

# Terminal report
uv run pytest tests/unit --cov=app --cov-report=term

# Both
uv run pytest tests/unit --cov=app --cov-report=html --cov-report=term
```

### Coverage Goals

- **Unit Tests**: Aim for 80%+ coverage of core logic
- **Critical Paths**: 100% coverage (auth, validation, security)
- **Integration**: Focus on user journeys, not coverage %

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install dependencies
        run: |
          cd services/observatory
          uv sync --dev
      
      - name: Run unit tests
        run: |
          cd services/observatory
          uv run pytest tests/unit --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./services/observatory/coverage.xml

  integration-tests:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
    steps:
      # ... similar setup ...
      
      - name: Run integration tests
        run: |
          cd services/observatory
          uv run pytest tests/integration -v
```

---

## Troubleshooting

### Tests Hang Indefinitely

**Cause**: Async tests with actual sleep() calls or waiting for external services
**Solution**: 
1. Use pytest timeout: `pytest --timeout=10`
2. Mock time in tests
3. Check for Redis/Ollama connection attempts

### Import Errors

**Cause**: Module not in PYTHONPATH
**Solution**: Run from repository root or use `uv run pytest`

### Database Errors in Tests

**Cause**: Previous test didn't clean up properly
**Solution**: Use fixtures with proper teardown, or delete `test.db` files

### Redis Connection Refused

**Expected**: Unit tests shouldn't need Redis
**Solution**: Skip Redis tests or start Redis:
```powershell
# Windows (if installed)
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:7
```

---

## Next Steps

### Immediate
1. ✅ Document current test strategy (this file)
2. ⏳ Implement test filtering in quick-start.ps1
3. ⏳ Move Redis tests to integration/
4. ⏳ Fix async timing issues in job tests

### Short-term
1. Add integration test suite
2. Add Redis/Ollama health checks
3. Add test markers for dependencies
4. Generate coverage reports in CI

### Long-term
1. Property-based testing with Hypothesis
2. Load testing for production readiness
3. Security testing (OWASP, penetration testing)
4. Performance regression testing

---

**Last Updated**: 2025-01-04  
**Maintained By**: Development Team  
**Questions**: See main README.md or open an issue
