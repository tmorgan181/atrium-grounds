# Proposal: Fix Feature 001 Integration Test Technical Debt

**Status**: Pending Review
**Created**: 2025-10-05
**Proposed By**: Claude Code
**Branch**: 001-atrium-observatory-service (to be switched to)

---

## Problem Statement

Integration test suite has 12/19 tests failing (37% pass rate) due to technical debt from Feature 001:

1. **httpx 0.28 API Breaking Change** (8 tests failing)
   - `AsyncClient(app=app)` deprecated
   - Requires `AsyncClient(transport=ASGITransport(app=app))`
   - Affects: test_analysis_flow.py (7 tests), test_webhooks.py (1 test)

2. **Incomplete Webhook Implementation** (3 tests failing)
   - Missing timeout parameter in send_batch_complete()
   - Missing max_retries parameter in send_batch_complete()
   - Missing generate_signature() method
   - Affects: test_webhooks.py (3 tests)

3. **Auth Test Hardcoded Failure** (1 test failing)
   - test_auth_public.py line 33 has `assert False`
   - Appears to be incomplete test implementation

---

## Scope Analysis

### Feature 001 Scope (FR-011)
✅ **In Scope**: Webhooks and batch processing are part of Feature 001
- FR-011 explicitly includes batch processing with webhooks
- Webhook implementation is Feature 001 responsibility
- httpx compatibility needed for Feature 001 to be complete

### Feature 002 Scope
❌ **Out of Scope**: Developer experience only
- Test filtering, verbosity control, code quality
- No API compatibility or webhook work

**Conclusion**: These fixes belong in Feature 001 branch, not Feature 002.

---

## Proposed Solution

### Phase 1: httpx 0.28 Compatibility (8 tests)

**Files to Update**:
- `services/observatory/tests/integration/test_analysis_flow.py`
- `services/observatory/tests/integration/test_webhooks.py`

**Change Required**:
```python
# Before (httpx < 0.28)
async with AsyncClient(app=app, base_url="http://test") as client:
    ...

# After (httpx >= 0.28)
from httpx import ASGITransport

async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    ...
```

**Impact**: 8 tests will pass after this change

---

### Phase 2: Complete Webhook Implementation (3 tests)

**File**: `services/observatory/app/core/notifications.py`

**Changes Needed**:

1. Add timeout parameter to send_batch_complete():
```python
async def send_batch_complete(
    batch_id: str,
    callback_url: str,
    results: list,
    timeout: int = 30  # NEW
):
    ...
```

2. Add max_retries parameter:
```python
async def send_batch_complete(
    batch_id: str,
    callback_url: str,
    results: list,
    timeout: int = 30,
    max_retries: int = 3  # NEW
):
    ...
```

3. Implement generate_signature() method:
```python
def generate_signature(payload: dict, secret: str) -> str:
    """Generate HMAC signature for webhook payload."""
    import hmac
    import hashlib
    import json

    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    signature = hmac.new(secret.encode(), payload_bytes, hashlib.sha256)
    return signature.hexdigest()
```

**Impact**: 3 webhook tests will pass

---

### Phase 3: Fix Auth Test (1 test)

**File**: `services/observatory/tests/integration/test_auth_public.py` (line 33)

**Investigation Needed**: Determine why test has `assert False`
- Review test intent
- Complete implementation
- Remove hardcoded failure

**Impact**: 1 test will pass

---

## Implementation Plan

### Option A: Fix in Feature 001 Branch (Recommended)

**Steps**:
1. User completes Feature 002 manual validation and bug fixes
2. Commit and push Feature 002 (if ready)
3. Switch to `001-atrium-observatory-service` branch
4. Implement Phases 1-3 above
5. Run integration tests to verify (expect 19/19 passing)
6. Commit as Feature 001 technical debt resolution
7. Update FEATURE-001-CHECKPOINT.md with completion status

**Pros**:
- Correct scope separation
- Feature 001 marked as truly complete
- Clean git history

**Cons**:
- Requires branch switch
- May conflict with Feature 002 if not merged first

---

### Option B: Fix in Feature 002 Branch (Scope Stretch)

**Steps**:
1. Complete Feature 002 manual validation
2. Fix integration tests in Feature 002 branch
3. Mark as "dependency upgrade" in Feature 002 scope
4. Merge Feature 002 with both sets of fixes

**Pros**:
- No branch switching
- One PR fixes everything

**Cons**:
- Mixes Feature 001 and Feature 002 concerns
- Feature 002 scope creep
- Feature 001 still marked as incomplete

---

### Option C: New Feature 003 (Most Conservative)

**Steps**:
1. Complete Feature 002, merge
2. Create Feature 003: "httpx 0.28 Migration & Webhook Completion"
3. Implement all fixes in new feature
4. Merge as separate feature

**Pros**:
- Clean separation of concerns
- Clear feature boundaries
- Separate testing/validation

**Cons**:
- Most overhead (new feature setup)
- Delays fixing Feature 001 technical debt

---

## Test Impact Summary

### Current State
- Unit: 58/78 passing (74%) - unchanged
- Contract: 38/38 passing (100%) - unchanged
- Integration: 7/19 passing (37%) - **will be fixed**
- Validation: 20/25 passing (80%) - unchanged (Feature 002 scope)

### After Fix (Expected)
- Unit: 58/78 passing (74%) - unchanged
- Contract: 38/38 passing (100%) - unchanged
- Integration: 19/19 passing (100%) - **✅ fixed**
- Validation: 20/25 passing (80%) - unchanged

---

## Recommendation

**Proceed with Option A** (Fix in Feature 001 Branch):

1. This is Feature 001 technical debt, not Feature 002 scope
2. Webhook implementation is FR-011 (Feature 001)
3. httpx compatibility needed for Feature 001 completion
4. Cleanest git history and scope separation

**Prerequisites**:
- ✅ Feature 002 manual validation complete
- ✅ Any Feature 002 bugs fixed
- ✅ Feature 002 ready to merge or pause

**Timeline**: 1-2 hours for implementation, testing, and documentation update

---

## Questions for Review

1. **Scope Decision**: Confirm Option A (Feature 001 branch) is correct approach?
2. **Feature 002 Status**: Is Feature 002 ready to merge/pause before switching?
3. **Webhook Security**: Should generate_signature() use configurable hash algorithm or hardcode SHA256?
4. **Auth Test**: Should we investigate test_auth_public.py failure or skip/remove test?

---

## References

- Feature 001 Spec: `specs/001-atrium-observatory-service/spec.md` (FR-011)
- Feature 001 Checkpoint: `specs/001-atrium-observatory-service/collaboration/FEATURE-001-CHECKPOINT.md`
- Integration Test Files: `services/observatory/tests/integration/`
- httpx 0.28 Migration Guide: https://www.python-httpx.org/compatibility/#async-client-instantiation

---

**Next Steps**: Await user decision on approach (Option A, B, or C) and proceed accordingly.

**Blockers**: Feature 002 manual validation must complete before switching branches.

---

**Maintained By**: Claude Code
**Last Updated**: 2025-10-05
