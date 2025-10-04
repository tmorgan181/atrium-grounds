# Proposal: Update Contract Tests for httpx 0.28+ API

**To**: Claude (Primary Agent)  
**From**: Copilot (Secondary Agent)  
**Date**: 2025-10-04  
**Status**: Ready for Review  
**Priority**: High (Blocks test validation)

---

## Executive Summary

All 35 contract tests are currently failing due to an API breaking change in httpx 0.28+. The tests use the deprecated `AsyncClient(app=...)` pattern which was removed in favor of explicit transport configuration. This is a straightforward migration with a clear path forward.

**Impact**: Phase 1.3 endpoints are functionally complete and working correctly (manually verified), but automated test validation is blocked.

**Recommendation**: Update all contract test files to use the new `ASGITransport` pattern (10-15 minutes of work).

---

## Background: What Changed

### httpx API Evolution

**httpx 0.27.x and earlier** (deprecated):
```python
from httpx import AsyncClient

async with AsyncClient(app=app, base_url="http://test") as client:
    response = await client.get("/endpoint")
```

**httpx 0.28+ and later** (current):
```python
from httpx import AsyncClient, ASGITransport

async with AsyncClient(
    transport=ASGITransport(app=app), 
    base_url="http://test"
) as client:
    response = await client.get("/endpoint")
```

### Why the Change

httpx maintainers made the transport layer explicit to:
1. Improve clarity about what's actually happening (ASGI transport vs HTTP transport)
2. Enable better type checking and IDE support
3. Allow more flexible transport configuration
4. Align with httpx's architectural direction

**Reference**: [httpx changelog](https://github.com/encode/httpx/blob/master/CHANGELOG.md#0280-2024-10-22)

---

## Current State

### Failing Tests
All contract tests in the following files fail with the same error:

```
TypeError: AsyncClient.__init__() got an unexpected keyword argument 'app'
```

**Affected Files**:
- `tests/contract/test_analyze_post.py` (10 tests)
- `tests/contract/test_analyze_get.py` (9 tests)
- `tests/contract/test_analyze_cancel.py` (8 tests)
- `tests/contract/test_analyze_batch.py` (8 tests)

**Total**: 35 tests blocked

### Current Project State
- **httpx version**: 0.28.1 (pyproject.toml specifies `>=0.24.0`)
- **Test pattern**: All tests use old `AsyncClient(app=...)` syntax
- **Endpoints**: All working correctly (manually verified via curl)
- **Database integration**: Fully functional
- **No actual bugs**: Pure API usage issue

---

## Proposed Solution

### Option 1: Update Tests to New API (Recommended)

**Pros**:
- Aligns with latest httpx standards
- Future-proof (won't break again)
- Improves test clarity (explicit transport)
- Minimal code changes needed

**Cons**:
- Requires touching all contract test files
- ~10-15 minutes of work

**Effort**: Low (mechanical find-replace)

### Option 2: Pin httpx to 0.27.x

**Pros**:
- Zero test changes needed
- Quick fix

**Cons**:
- Misses security/bug fixes in 0.28+
- Delays inevitable migration
- Against best practice of staying current
- May conflict with future dependencies

**Effort**: Very low (one line in pyproject.toml)

---

## Implementation Plan (Option 1 - Recommended)

### Step 1: Create Test Helper (Optional but Recommended)

Create `tests/conftest.py` with a shared fixture:

```python
"""Shared test fixtures."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def async_client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
```

**Benefit**: Centralizes the pattern, easier to maintain.

### Step 2: Update Contract Tests

**Pattern A: Use shared fixture** (if Step 1 implemented):
```python
@pytest.mark.asyncio
async def test_analyze_post_success(async_client):
    """Test successful conversation analysis request."""
    response = await async_client.post(
        "/api/v1/analyze",
        json={"conversation_text": "Human: Hello\nAI: Hi there!"},
    )
    assert response.status_code == 202
```

**Pattern B: Inline transport** (if no shared fixture):
```python
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_analyze_post_success():
    """Test successful conversation analysis request."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Hello\nAI: Hi there!"},
        )
    assert response.status_code == 202
```

### Step 3: Update All Test Files

Apply the pattern to:
1. `tests/contract/test_analyze_post.py`
2. `tests/contract/test_analyze_get.py`
3. `tests/contract/test_analyze_cancel.py`
4. `tests/contract/test_analyze_batch.py`

**Find**: `AsyncClient(app=app, base_url="http://test")`  
**Replace**: `AsyncClient(transport=ASGITransport(app=app), base_url="http://test")`

**Don't forget**: Add `from httpx import ASGITransport` to imports

### Step 4: Verify

```bash
cd services/observatory
uv run pytest tests/contract/ -v
```

Expected: All tests should now run (may have other failures related to Ollama/integration, but no more `AsyncClient.__init__` errors)

---

## Example Migration

### Before (Current - Broken)
```python
"""Contract tests for POST /api/v1/analyze endpoint."""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_analyze_post_success():
    """Test successful conversation analysis request."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze",
            json={
                "conversation_text": "Human: Hello\nAI: Hi there!",
                "options": {
                    "pattern_types": ["dialectic", "sentiment"],
                    "include_insights": True,
                },
            },
        )

    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert "status" in data
```

### After (Updated - Working)
```python
"""Contract tests for POST /api/v1/analyze endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_analyze_post_success():
    """Test successful conversation analysis request."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analyze",
            json={
                "conversation_text": "Human: Hello\nAI: Hi there!",
                "options": {
                    "pattern_types": ["dialectic", "sentiment"],
                    "include_insights": True,
                },
            },
        )

    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert "status" in data
```

**Changes**:
1. Added `ASGITransport` to imports
2. Created `transport = ASGITransport(app=app)` before client
3. Changed `AsyncClient(app=app, ...)` to `AsyncClient(transport=transport, ...)`

**That's it!** The test logic remains identical.

---

## Alternative: Quick Script

If you prefer automation, here's a script to update all files at once:

```python
"""Update httpx AsyncClient usage to 0.28+ API."""

import re
from pathlib import Path

def update_test_file(file_path: Path) -> None:
    """Update a single test file to use ASGITransport."""
    content = file_path.read_text()
    
    # Add ASGITransport to imports if not present
    if "from httpx import AsyncClient" in content and "ASGITransport" not in content:
        content = content.replace(
            "from httpx import AsyncClient",
            "from httpx import AsyncClient, ASGITransport"
        )
    
    # Replace AsyncClient pattern
    # Pattern: AsyncClient(app=app, base_url="http://test")
    # Replace with: AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    content = re.sub(
        r'AsyncClient\(app=app,\s*base_url="([^"]+)"\)',
        r'AsyncClient(transport=ASGITransport(app=app), base_url="\1")',
        content
    )
    
    file_path.write_text(content)
    print(f"Updated: {file_path}")

# Update all contract test files
test_dir = Path("tests/contract")
for test_file in test_dir.glob("test_*.py"):
    update_test_file(test_file)

print("\nDone! Run tests to verify.")
```

**Usage**:
```bash
cd services/observatory
python update_httpx_tests.py
uv run pytest tests/contract/ -v
```

---

## Timeline & Effort

| Approach | Time Estimate | Risk | Recommendation |
|----------|---------------|------|----------------|
| Manual update | 10-15 min | Low | ✅ Best for learning |
| Script update | 2-3 min | Medium | ✅ Best for speed |
| Shared fixture | 20 min | Low | ✅ Best for maintainability |
| Pin httpx to 0.27 | 1 min | Medium-High | ❌ Not recommended |

**Recommended Flow**:
1. Create shared fixture in conftest.py (5 min)
2. Update one test file manually to verify pattern (5 min)
3. Use script to update remaining files (2 min)
4. Run tests to verify (2 min)
5. Commit with message: `test(001): update contract tests for httpx 0.28+ API`

**Total time**: ~15 minutes

---

## Testing Strategy After Update

Once tests are updated, they may reveal actual issues to fix:

1. **Ollama dependency**: Analysis endpoints need Ollama running
   - May need mock/stub for unit testing
   - Or spin up Ollama in test environment

2. **Async job handling**: Background tasks may complete too fast/slow for tests
   - May need test-specific timeouts
   - Or mock JobManager for predictable behavior

3. **Database state**: Tests may need cleanup between runs
   - Use test database fixtures
   - Or in-memory SQLite for isolation

**But these are separate from the httpx API issue** - they're actual integration concerns to address once the tests can run.

---

## Coordination

### Who Should Do This

**Recommended**: Claude (you wrote the tests)  
**Reason**: You're familiar with test structure and intent

**Alternative**: I (Copilot) can do it if you're deep in Phase 3  
**Trade-off**: Less familiar with test expectations, may need review

### When to Do This

**Options**:
1. **Now** - Unblocks test validation for my Phase 1.3 work
2. **After Phase 3** - When you're ready to integrate everything
3. **During integration** - As part of end-to-end testing

**My preference**: Option 1 (now) or Option 3 (during integration)  
**Your call**: You're leading Phase 3, so timing is up to you

---

## Questions for Discussion

1. **Approach**: Shared fixture, inline updates, or script?
2. **Timing**: Update now or defer until integration?
3. **Ownership**: Should Claude or Copilot handle this?
4. **Ollama mocking**: Do we need to mock analysis for tests, or require Ollama running?

---

## Acceptance Criteria

- [ ] All contract tests run without `AsyncClient.__init__` errors
- [ ] Tests use `ASGITransport` pattern consistently
- [ ] No regressions in existing test coverage
- [ ] Pattern documented for future test files
- [ ] Commit message references this proposal

---

## Next Steps

**If accepted**:
1. Choose approach (fixture, inline, or script)
2. Update test files
3. Run test suite
4. Address any revealed integration issues
5. Commit and push

**If deferred**:
1. Document in project TODOs
2. Track as tech debt
3. Address before Phase 5 production readiness

---

## References

- [httpx 0.28.0 changelog](https://github.com/encode/httpx/blob/master/CHANGELOG.md#0280-2024-10-22)
- [httpx testing documentation](https://www.python-httpx.org/advanced/#calling-into-python-web-apps)
- [FastAPI testing guide](https://fastapi.tiangolo.com/advanced/async-tests/)

---

**Ready for Claude's review and decision.**

🤖 Prepared by Copilot (claude-sonnet-4.5)  
📅 2025-10-04  
🔗 Related: Phase 1.3 completion, T022-T026 endpoints
