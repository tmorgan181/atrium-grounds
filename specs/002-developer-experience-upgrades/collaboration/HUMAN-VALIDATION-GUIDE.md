# Human Validation Guide - Feature 002 Developer Experience Upgrades

**Feature**: 002 Developer Experience Upgrades
**Version**: v0.1.0
**Date**: 2025-10-04
**Constitution**: v1.3.0

---

## Overview

This guide provides step-by-step validation procedures for all Feature 002 enhancements. Use this to verify that the developer experience upgrades are working correctly.

**Total Test Time**: ~15-20 minutes
**Prerequisites**: Windows 10/11 with PowerShell 5.1+ or PowerShell Core 7+

---

## Quick Reference

### New Parameters Added (T001)
- `-Clean` - ANSI-free logging for Windows
- `-Unit` - Run only unit tests
- `-Contract` - Run only contract tests
- `-Integration` - Run only integration tests
- `-Validation` - Run only validation suite
- `-Coverage` - Generate coverage report
- `-Detail` - Detailed output with diagnostics (pre-existing, enhanced)

### New Behaviors
- **Default Mode**: Minimal, scannable output (~8 lines)
- **Detail Mode**: Full diagnostic output with progress steps
- **Test Filtering**: Run specific test suites individually
- **Verbosity Control**: Suppress external tool output by default
- **Venv Check**: Skip redundant virtual environment creation

---

## Validation Checklist

### ✅ Phase 1: Foundation (T001-T002)

#### Test 1.1: New Parameters Exist
**Objective**: Verify all 6 new parameters are recognized

```powershell
# Navigate to observatory directory
cd services/observatory

# Test help text (should not error)
.\quick-start.ps1 help
```

**Expected Output**:
- Help text displays without errors
- OPTIONS section includes:
  - `-Detail` - Enable detailed output with progress steps
  - Test Filtering section with `-Unit`, `-Contract`, `-Integration`, `-Validation`, `-Coverage`
- EXAMPLES section shows test filtering examples

**Pass Criteria**: ✅ All parameters documented, no PowerShell errors

---

#### Test 1.2: Parameter Parsing
**Objective**: Verify parameters don't cause parsing errors

```powershell
# Test each parameter individually (dry run with -WhatIf if available)
.\quick-start.ps1 help -Detail
.\quick-start.ps1 help -Clean
.\quick-start.ps1 help -Unit
.\quick-start.ps1 help -Contract
.\quick-start.ps1 help -Integration
.\quick-start.ps1 help -Validation
.\quick-start.ps1 help -Coverage
```

**Expected Output**: Help text displays normally for each

**Pass Criteria**: ✅ No parsing errors, no "parameter not recognized" messages

---

### ✅ Phase 2: Verbosity Control (T003-T007)

#### Test 2.1: Default Mode (Minimal Output)
**Objective**: Verify setup action produces scannable output

```powershell
# Clean environment first
.\quick-start.ps1 clean

# Run setup in default mode
.\quick-start.ps1 setup
```

**Expected Output**:
```
===============================================================
  Setting Up Observatory Environment
===============================================================

[OK] Virtual environment created
[OK] Dependencies installed
[OK] Development dependencies installed
[OK] API keys already exist

[OK] Setup complete!
[INFO] Run '.\quick-start.ps1 test' to verify installation
[INFO] Run '.\quick-start.ps1 validate' to test the service
```

**Pass Criteria**:
- ✅ Output is ~8-12 lines total
- ✅ No verbose tool output (uv, pip)
- ✅ Clear [OK] success indicators
- ✅ Scannable in <5 seconds (NFR-001)

---

#### Test 2.2: Detail Mode (Full Diagnostics)
**Objective**: Verify -Detail flag shows full output

```powershell
# Clean environment first
.\quick-start.ps1 clean

# Run setup with -Detail flag
.\quick-start.ps1 setup -Detail
```

**Expected Output**:
```
===============================================================
  Setting Up Observatory Environment
===============================================================

-> Creating virtual environment with uv...
Using Python 3.11.9 interpreter at: C:\Python311\python.exe
Creating virtualenv at: .venv
[... full uv output ...]

-> Installing dependencies...
Looking in indexes: https://pypi.org/simple
[... full pip output ...]

-> Installing development dependencies...
[... full pip dev output ...]

-> Checking for development API keys...
[OK] API keys already exist

[OK] Setup complete!
[INFO] Run '.\quick-start.ps1 test' to verify installation
[INFO] Run '.\quick-start.ps1 validate' to test the service
```

**Pass Criteria**:
- ✅ All `->` step messages visible
- ✅ Full uv and pip output shown
- ✅ Useful for troubleshooting
- ✅ More verbose than default mode

---

#### Test 2.3: Venv Existence Check (T005)
**Objective**: Verify setup skips creating venv if it already exists

```powershell
# Run setup again (venv already exists from Test 2.2)
.\quick-start.ps1 setup
```

**Expected Output** (default mode):
```
===============================================================
  Setting Up Observatory Environment
===============================================================

[OK] Dependencies installed
[OK] Development dependencies installed
[OK] API keys already exist

[OK] Setup complete!
[INFO] Run '.\quick-start.ps1 test' to verify installation
[INFO] Run '.\quick-start.ps1 validate' to test the service
```

**Expected Output** (detail mode):
```powershell
.\quick-start.ps1 setup -Detail
```
```
===============================================================
  Setting Up Observatory Environment
===============================================================

[INFO] Virtual environment already exists (skipping creation)

-> Installing dependencies...
[... full output ...]
```

**Pass Criteria**:
- ✅ Default mode: No venv creation message
- ✅ Detail mode: Shows "Virtual environment already exists (skipping creation)"
- ✅ No redundant venv creation

---

### ✅ Phase 3: Test Filtering (T008-T010)

#### Test 3.1: Run All Tests (Default Behavior)
**Objective**: Verify default test action runs all suites

```powershell
.\quick-start.ps1 test
```

**Expected Output** (default mode):
```
===============================================================
  Running Observatory Test Suite
===============================================================

[OK] Unit tests passed
[OK] Contract tests passed
[WARN] Integration tests failed (exit code: 1)
[INFO] Some integration tests may require the server running
[INFO] Validation suite failed (exit code: 1)

-------------------------------------------------------------
Test Summary
-------------------------------------------------------------
[OK] Unit tests passed
[OK] Contract tests passed
[FAIL] Integration tests failed
[FAIL] Validation tests failed

[WARN] Failed test suites: integration, validation
[INFO] Run with -Detail flag for more information
```

**Pass Criteria**:
- ✅ Runs all 4 test suites (unit, contract, integration, validation)
- ✅ Minimal output in default mode
- ✅ Test summary at end

---

#### Test 3.2: Unit Tests Only
**Objective**: Verify -Unit flag runs only unit tests

```powershell
.\quick-start.ps1 test -Unit
```

**Expected Output** (default mode):
```
===============================================================
  Running Unit Tests
===============================================================

[OK] Unit tests passed
```

**Pass Criteria**:
- ✅ Only runs unit tests
- ✅ Fast execution (~2-5 seconds)
- ✅ No contract, integration, or validation tests run

---

#### Test 3.3: Contract Tests Only
**Objective**: Verify -Contract flag runs only contract tests

```powershell
.\quick-start.ps1 test -Contract
```

**Expected Output**:
```
===============================================================
  Running Contract Tests
===============================================================

[OK] Contract tests passed
```

**Pass Criteria**:
- ✅ Only runs contract tests
- ✅ No other test suites run

---

#### Test 3.4: Multiple Filters (Unit + Contract)
**Objective**: Verify multiple test filters work together

```powershell
# This should work if implemented (check spec)
.\quick-start.ps1 test -Unit -Contract
```

**Expected Output**:
```
===============================================================
  Running Unit + Contract Tests
===============================================================

[OK] Unit tests passed
[OK] Contract tests passed

-------------------------------------------------------------
Test Summary
-------------------------------------------------------------
[OK] Unit tests passed
[OK] Contract tests passed

[OK] All tests passed! 🎉
```

**Pass Criteria**:
- ✅ Runs both unit and contract tests
- ✅ No integration or validation tests

---

#### Test 3.5: Coverage Report
**Objective**: Verify -Coverage flag generates coverage report

```powershell
.\quick-start.ps1 test -Unit -Coverage
```

**Expected Output** (includes coverage table):
```
===============================================================
  Running Unit Tests
===============================================================

[... pytest output ...]

---------- coverage: platform win32, python 3.11.9 -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
app\__init__.py                       5      0   100%
app\core\analyze.py                 120     12    90%   45-48, 67-70
[... more coverage lines ...]
---------------------------------------------------------------
TOTAL                              1234    123    90%

[OK] Unit tests passed
```

**Pass Criteria**:
- ✅ Coverage report visible in output
- ✅ Shows statement coverage percentages
- ✅ Works with any test type (unit, contract, etc.)

---

#### Test 3.6: Test Verbosity Control
**Objective**: Verify -Detail flag with tests shows full pytest output

```powershell
.\quick-start.ps1 test -Unit -Detail
```

**Expected Output** (verbose pytest):
```
===============================================================
  Running Unit Tests
===============================================================

-> Running unit tests...

============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-7.4.3, pluggy-1.3.0 -- C:\...\python.exe
cachedir: .pytest_cache
rootdir: C:\...\services\observatory
plugins: asyncio-0.21.1, cov-4.1.0
collected 58 items

tests/unit/test_auth.py::test_generate_api_key PASSED                   [  1%]
tests/unit/test_auth.py::test_register_api_key PASSED                   [  3%]
[... all test names with PASSED/FAILED ...]

============================== 58 passed in 2.34s ==============================
```

**Pass Criteria**:
- ✅ Full pytest verbose output (`-v`)
- ✅ Shows each test name with result
- ✅ Includes full tracebacks on failure (`--tb=short`)

---

### ✅ Phase 4: Clean Logging (T012)

#### Test 4.1: Server with Clean Logging
**Objective**: Verify -Clean flag removes ANSI codes

```powershell
# Start server with clean logging
.\quick-start.ps1 serve -Clean -NewWindow
```

**Expected Behavior**:
- Server starts in new window
- Log output has no color codes or ANSI escape sequences
- Logs are plain text (suitable for Windows PowerShell 5.1)

**Manual Verification**:
1. Check new PowerShell window
2. Verify logs are plain text (no `[33m`, `[0m`, etc.)
3. Logs should be readable in Windows PowerShell 5.1

**Pass Criteria**:
- ✅ Server starts successfully
- ✅ No ANSI codes in log output
- ✅ Logs are clean and readable

---

### ✅ Phase 5: Backward Compatibility

#### Test 5.1: Existing Commands Still Work
**Objective**: Verify all pre-existing commands function normally

```powershell
# Test each existing action
.\quick-start.ps1 setup
.\quick-start.ps1 test
.\quick-start.ps1 serve -NewWindow
.\quick-start.ps1 keys
.\quick-start.ps1 health
.\quick-start.ps1 validate
.\quick-start.ps1 clean
.\quick-start.ps1 help
```

**Pass Criteria**:
- ✅ All commands execute without errors
- ✅ Same final results as before Feature 002
- ✅ No breaking changes to existing workflows

---

#### Test 5.2: Existing Flags Still Work
**Objective**: Verify pre-existing flags function correctly

```powershell
# Test existing flags
.\quick-start.ps1 serve -Port 8001
.\quick-start.ps1 serve -NewWindow
.\quick-start.ps1 setup -Detail  # Detail existed before, now enhanced
```

**Pass Criteria**:
- ✅ `-Port` works (server starts on specified port)
- ✅ `-NewWindow` works (server starts in new window)
- ✅ `-Detail` works (enhanced with more verbosity control)

---

### ✅ Phase 6: Performance Validation (NFR-005)

#### Test 6.1: Overhead Measurement
**Objective**: Verify verbosity control adds <100ms overhead

```powershell
# Measure execution time with default mode
Measure-Command { .\quick-start.ps1 setup }

# Measure execution time with detail mode
Measure-Command { .\quick-start.ps1 setup -Detail }
```

**Expected Results**:
- Default mode overhead: <50ms (typically ~30-50ms)
- Detail mode overhead: <50ms (typically ~30-50ms)
- Difference between modes: Minimal (<20ms)

**Pass Criteria**:
- ✅ Overhead is imperceptible (<100ms, NFR-005)
- ✅ No significant performance degradation
- ✅ Both modes complete in reasonable time

---

### ✅ Phase 7: Output Scanability (NFR-001)

#### Test 7.1: Scannable Output
**Objective**: Verify default mode output is scannable in <5 seconds

**Procedure**:
1. Run `.\quick-start.ps1 setup` in default mode
2. Time how long it takes to:
   - Identify if setup succeeded or failed
   - Understand what actions were performed
   - Determine next steps

**Expected Output Line Count**:
- Setup: ~8-12 lines
- Test (all): ~15-20 lines
- Test (single suite): ~5-8 lines

**Pass Criteria**:
- ✅ User can scan output in <5 seconds
- ✅ Clear success/failure indicators
- ✅ No unnecessary verbose output
- ✅ Output fits on single screen (~50 lines max)

---

## Edge Cases & Error Handling

### Edge Case 1: Missing Prerequisites
```powershell
# Remove .venv and try running tests
.\quick-start.ps1 clean
.\quick-start.ps1 test  # Should error gracefully
```

**Expected Output**:
```
-------------------------------------------------------------
Checking Prerequisites
-------------------------------------------------------------
[OK] Python found: Python 3.11.9
[OK] uv found: uv 0.1.23
[WARN] Virtual environment not found. Run: .\quick-start.ps1 setup

[FAIL] Prerequisites not met. Run: .\quick-start.ps1 setup
```

**Pass Criteria**: ✅ Clear error message, guidance to run setup

---

### Edge Case 2: Conflicting Flags
```powershell
# Test mutually exclusive flags (if validation implemented)
.\quick-start.ps1 test -Unit -Coverage -Integration
```

**Expected Behavior**:
- Should run unit AND integration tests with coverage
- Or warn about conflicting flags (if T024 validation implemented)

**Pass Criteria**: ✅ Either works correctly or shows clear error

---

### Edge Case 3: Invalid Action
```powershell
.\quick-start.ps1 invalid-action
```

**Expected Output**:
```
[Shows help text]
```

**Pass Criteria**: ✅ Falls back to help text gracefully

---

## Validation Completion Checklist

Use this checklist to track your validation progress:

### Foundation
- [ ] Test 1.1: New parameters exist in help
- [ ] Test 1.2: Parameters parse without errors

### Verbosity Control
- [ ] Test 2.1: Default mode produces minimal output
- [ ] Test 2.2: Detail mode shows full diagnostics
- [ ] Test 2.3: Venv existence check works

### Test Filtering
- [ ] Test 3.1: Run all tests (default)
- [ ] Test 3.2: Unit tests only (-Unit)
- [ ] Test 3.3: Contract tests only (-Contract)
- [ ] Test 3.4: Multiple filters work
- [ ] Test 3.5: Coverage report generation
- [ ] Test 3.6: Test verbosity control (-Detail)

### Clean Logging
- [ ] Test 4.1: Server with clean logging (-Clean)

### Backward Compatibility
- [ ] Test 5.1: Existing commands still work
- [ ] Test 5.2: Existing flags still work

### Performance
- [ ] Test 6.1: Overhead measurement (<100ms)

### Scanability
- [ ] Test 7.1: Output scannable in <5 seconds

### Edge Cases
- [ ] Edge Case 1: Missing prerequisites
- [ ] Edge Case 2: Conflicting flags
- [ ] Edge Case 3: Invalid action

---

## Success Criteria

**Feature 002 is VALIDATED when**:
- ✅ All 28 tests pass
- ✅ All checkboxes above are checked
- ✅ No regressions in existing functionality
- ✅ Performance overhead <100ms (NFR-005)
- ✅ Output scannable in <5 seconds (NFR-001)
- ✅ All 6 new parameters work correctly
- ✅ Test filtering works for all suite types
- ✅ Verbosity control works in both modes
- ✅ Backward compatibility maintained

---

## Reporting Issues

If you encounter issues during validation:

1. **Document the issue**:
   - What test failed?
   - Expected vs actual output?
   - Error messages or screenshots?

2. **Check known issues** in `FEATURE-001-CHECKPOINT.md`:
   - Are these expected failures?
   - Is there a workaround?

3. **Report to development team**:
   - File issue in GitHub or collaboration/decisions/
   - Include full error output
   - Include PowerShell version: `$PSVersionTable.PSVersion`

---

## Quick Validation Script

For rapid validation, run this test sequence:

```powershell
# Quick validation (5 minutes)
cd services/observatory

# Test help
.\quick-start.ps1 help | Select-String -Pattern "Unit|Contract|Integration|Coverage"

# Test setup (default mode)
.\quick-start.ps1 clean
.\quick-start.ps1 setup

# Test setup (detail mode)
.\quick-start.ps1 setup -Detail

# Test filtering
.\quick-start.ps1 test -Unit
.\quick-start.ps1 test -Unit -Coverage

# Test verbosity
.\quick-start.ps1 test -Unit -Detail

# Verify backward compatibility
.\quick-start.ps1 keys
.\quick-start.ps1 health

Write-Host "`n✅ Quick validation complete!" -ForegroundColor Green
```

---

## Version History

| Version | Date       | Changes                                      |
|---------|------------|----------------------------------------------|
| 1.0.0   | 2025-10-04 | Initial validation guide for Feature 002     |

---

**End of Validation Guide**
