#!/bin/bash
# TDD Gate Validator - Run before Phase 3.3 implementation
# Ensures tests exist and fail (TDD principle: tests before implementation)

set -e

echo "🔍 TDD Gate Validation"
echo "====================="
echo ""

# Navigate to web-interface directory
cd "$(dirname "$0")/../services/web-interface" || {
    echo "❌ FAIL: services/web-interface directory not found"
    echo "Run this script from project root or create service directory first (T001)"
    exit 1
}

# Check tests exist
echo "Step 1: Verify tests exist..."
TEST_COUNT=$(uv run pytest tests/ --collect-only -q 2>/dev/null | grep -c "test_" || echo "0")

if [ "$TEST_COUNT" -lt 7 ]; then
    echo "❌ FAIL: Found $TEST_COUNT tests, need at least 7"
    echo ""
    echo "Expected tests (T004-T010):"
    echo "  - test_landing_page_* (2 tests)"
    echo "  - test_demo_page_* (1 test)"
    echo "  - test_examples_endpoint_* (2 tests)"
    echo "  - test_analyze_proxy_* (2 tests)"
    echo "  - test_health_endpoint_* (1 test)"
    echo "  - test_integration_* (2 tests)"
    echo ""
    echo "Action: Write tests T004-T010 first!"
    exit 1
fi
echo "✅ Found $TEST_COUNT tests"
echo ""

# Check tests fail (implementation missing)
echo "Step 2: Verify tests fail (no implementation)..."

# Run tests and capture output
TEST_OUTPUT=$(uv run pytest tests/ -v 2>&1 || true)

# Check if any tests passed
PASSED_COUNT=$(echo "$TEST_OUTPUT" | grep -c "PASSED" || echo "0")

if [ "$PASSED_COUNT" -gt 0 ]; then
    echo "❌ FAIL: $PASSED_COUNT tests passing - implementation may already exist"
    echo ""
    echo "TDD principle violated: Tests should fail before implementation"
    echo ""
    echo "Possible causes:"
    echo "  1. Implementation already written (check app/ directory)"
    echo "  2. Tests mocking/stubbing instead of testing real code"
    echo "  3. Tests are trivial (e.g., 'assert True')"
    echo ""
    echo "Action: Review test files and ensure they test real functionality"
    exit 1
fi

# Check tests fail with correct error types (import or attribute errors expected)
IMPORT_ERRORS=$(echo "$TEST_OUTPUT" | grep -c "ImportError\|ModuleNotFoundError\|AttributeError" || echo "0")

if [ "$IMPORT_ERRORS" -eq 0 ]; then
    echo "⚠️  WARNING: Tests failing but not with Import/AttributeError"
    echo ""
    echo "Expected: Tests fail because app modules don't exist yet"
    echo "Actual: Tests failing for other reasons"
    echo ""
    echo "Review test output:"
    echo "$TEST_OUTPUT" | grep -A 3 "FAILED"
    echo ""
    echo "This may be acceptable if tests have proper mocking structure"
    echo "Continue? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "Action: Review and fix test failures"
        exit 1
    fi
else
    echo "✅ Tests fail as expected (no implementation yet)"
    echo "   Found $IMPORT_ERRORS import/attribute errors"
fi

echo ""
echo "🎉 TDD Gate PASSED - Proceed to implementation (T011+)"
echo ""
echo "Next steps:"
echo "  1. Create FastAPI app skeleton (T011)"
echo "  2. Implement core functionality (T012-T021)"
echo "  3. Run tests again - they should pass"
echo ""
