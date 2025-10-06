# Feature 004: Quick-Start Script Refactor

**Status**: Proposal  
**Created**: 2025-01-XX  
**Priority**: Medium  

## Overview

Refactor the Observatory service's `quick-start.ps1` script (currently 1,666 lines) into a modular PowerShell module structure while maintaining all existing functionality and creating consistent output patterns across all scripts.

## Current State

**Main Script**: `services/observatory/quick-start.ps1` (1,666 lines)
- Contains all functionality in a single file
- Mixes concerns: UI helpers, business logic, API calls, test orchestration
- Hardcoded configuration values scattered throughout script
- Supporting scripts in `scripts/` directory:
  - `validation.ps1` - API validation suite
  - `performance-validation.ps1` - Performance testing
  - `test-dx-features.ps1` - Developer experience tests

**Key Features to Preserve**:
- All 13 actions: setup, test, serve, demo, health, analyze, keys, validate, lint, format, check, clean, help
- Parameter validation and filtering
- Verbose mode support
- Test filtering (Unit, Contract, Integration, Validation, Coverage)
- API key management
- Server lifecycle management
- Clean logging option
- Rate limit testing
- Authentication testing

## Problems to Solve

1. **Maintainability**: Single 1,666-line file is difficult to navigate and modify
2. **Code Duplication**: Similar output patterns repeated across functions
3. **Inconsistent Output**: Different scripts use different output styles
4. **Testing**: Monolithic structure makes unit testing difficult
5. **Reusability**: Helper functions locked in one script, not available to other scripts
6. **Organization**: Mix of concerns (UI, logic, orchestration) in single file
7. **Hardcoded Configuration**: Values like ports, paths, timeouts scattered throughout code

## Proposed Structure

```
services/observatory/
├── quick-start.ps1                    # Thin orchestrator (~150 lines)
├── observatory.config.json            # Unified configuration file
├── modules/
│   ├── Observatory.UI/
│   │   ├── Observatory.UI.psd1        # Module manifest
│   │   ├── Observatory.UI.psm1        # Main module file
│   │   └── Functions/
│   │       ├── Write-Header.ps1
│   │       ├── Write-Success.ps1
│   │       ├── Write-Error.ps1
│   │       ├── Write-Info.ps1
│   │       ├── Write-Warning.ps1
│   │       ├── Write-Step.ps1
│   │       ├── Write-Result.ps1
│   │       ├── Write-Section.ps1
│   │       ├── Write-ApiCall.ps1
│   │       └── Get-Timestamp.ps1
│   │
│   ├── Observatory.Core/
│   │   ├── Observatory.Core.psd1
│   │   ├── Observatory.Core.psm1
│   │   └── Functions/
│   │       ├── Get-PythonExePath.ps1
│   │       ├── Test-Prerequisites.ps1
│   │       ├── Invoke-CommandWithVerbosity.ps1
│   │       └── Get-ObservatoryConfig.ps1
│   │
│   ├── Observatory.Server/
│   │   ├── Observatory.Server.psd1
│   │   ├── Observatory.Server.psm1
│   │   └── Functions/
│   │       ├── Start-ObservatoryServer.ps1
│   │       ├── Stop-ObservatoryServer.ps1
│   │       ├── Start-TestServer.ps1
│   │       ├── Stop-TestServer.ps1
│   │       └── Stop-AllTestServers.ps1
│   │
│   ├── Observatory.Tests/
│   │   ├── Observatory.Tests.psd1
│   │   ├── Observatory.Tests.psm1
│   │   └── Functions/
│   │       ├── Invoke-TestSuite.ps1
│   │       ├── Invoke-ObservatoryTests.ps1
│   │       └── Invoke-QuickTests.ps1
│   │
│   ├── Observatory.Quality/
│   │   ├── Observatory.Quality.psd1
│   │   ├── Observatory.Quality.psm1
│   │   └── Functions/
│   │       ├── Invoke-Lint.ps1
│   │       ├── Invoke-Format.ps1
│   │       └── Invoke-Check.ps1
│   │
│   ├── Observatory.Api/
│   │   ├── Observatory.Api.psd1
│   │   ├── Observatory.Api.psm1
│   │   └── Functions/
│   │       ├── Test-HealthEndpoint.ps1
│   │       ├── Test-AnalyzeEndpoint.ps1
│   │       ├── Test-RateLimiting.ps1
│   │       ├── Test-AuthenticationMetrics.ps1
│   │       └── Invoke-KeyManagement.ps1
│   │
│   └── Observatory.Setup/
│       ├── Observatory.Setup.psd1
│       ├── Observatory.Setup.psm1
│       └── Functions/
│           ├── Invoke-Setup.ps1
│           └── Invoke-Clean.ps1
│
└── scripts/
    ├── validation.ps1                 # Updated to use modules
    ├── performance-validation.ps1     # Updated to use modules
    └── test-dx-features.ps1          # Updated to use modules
```

## Module Responsibilities

### Observatory.UI
**Purpose**: Consistent console output across all Observatory scripts  
**Exports**: All Write-* functions for colored, formatted output  
**State**: `$Script:Verbose` flag for verbosity control  

### Observatory.Core
**Purpose**: Shared utilities and configuration management  
**Exports**: Path helpers, config management, command execution  
**Configuration**: Loads and manages `observatory.config.json`  
**Dependencies**: None

### Observatory.Server
**Purpose**: Server lifecycle management  
**Exports**: Functions to start/stop servers (test and dev)  
**Dependencies**: Observatory.Core, Observatory.UI  

### Observatory.Tests
**Purpose**: Test orchestration and execution  
**Exports**: Test suite runners with filtering support  
**Dependencies**: Observatory.Core, Observatory.UI, Observatory.Server  

### Observatory.Quality
**Purpose**: Code quality checks (lint, format, type check)  
**Exports**: Quality action functions  
**Dependencies**: Observatory.Core, Observatory.UI  

### Observatory.Api
**Purpose**: API testing and key management  
**Exports**: Endpoint testing and authentication functions  
**Dependencies**: Observatory.Core, Observatory.UI  

### Observatory.Setup
**Purpose**: Environment setup and cleanup  
**Exports**: Setup and clean actions  
**Dependencies**: Observatory.Core, Observatory.UI, Observatory.Api  

## Unified Configuration

### Configuration File: `observatory.config.json`

All configurable values should be centralized in a single JSON configuration file:

```json
{
  "service": {
    "name": "Atrium Observatory",
    "version": "0.1.0"
  },
  "server": {
    "default_port": 8000,
    "default_host": "127.0.0.1",
    "startup_wait_seconds": 3,
    "health_check_timeout_seconds": 10,
    "health_check_interval_ms": 500
  },
  "paths": {
    "venv": ".venv/Scripts",
    "data": "data",
    "api_keys": "dev-api-keys.txt",
    "modules": "modules"
  },
  "testing": {
    "unit_path": "tests/unit/",
    "contract_path": "tests/contract/",
    "integration_path": "tests/integration/",
    "quick_test_files": [
      "tests/unit/test_database.py",
      "tests/unit/test_auth.py",
      "tests/unit/test_ratelimit.py",
      "tests/unit/test_validator.py"
    ],
    "pytest_quiet_args": ["-q", "--tb=line"],
    "pytest_verbose_args": ["-v", "--tb=short"]
  },
  "quality": {
    "linter": "ruff",
    "formatter": "ruff",
    "type_checker": "mypy",
    "type_check_path": "app/"
  },
  "demo": {
    "conversation_sample_path": null,
    "rate_limit_test_count": 12,
    "rate_limit_delay_ms": 100
  },
  "terminal": {
    "windows_terminal_profile": "Orion"
  }
}
```

### Configuration Management

**Observatory.Core module** will provide:
- `Get-ObservatoryConfig`: Load and cache configuration
- `Get-ConfigValue`: Get specific config value with dot notation (e.g., "server.default_port")
- `Set-ConfigValue`: Update config value programmatically (for testing/automation)
- `Reset-ConfigCache`: Clear cached config (for testing)

**Benefits**:
- Single source of truth for all configurable values
- Easy to customize for different environments
- No code changes needed for configuration adjustments
- Config can be version controlled with sensible defaults
- Supports environment-specific overrides (e.g., `observatory.local.config.json`)

## Implementation Plan

### Phase 1: Foundation (Create Module Structure)
**Tasks**:
1. Create `observatory.config.json` with all current hardcoded values
2. Create module directory structure
3. Create module manifests (.psd1) with metadata
4. Create Observatory.UI module (most reusable, no dependencies)
5. Create Observatory.Core module with config management functions
6. Update quick-start.ps1 to import modules and use config file

**Validation**:
- Config file loads successfully
- Quick-start.ps1 still runs all actions
- Output looks identical to current version
- All helper functions work through modules
- Configuration values read from JSON, not hardcoded

### Phase 2: Extract Domain Logic
**Tasks**:
1. Create Observatory.Server module (server management)
2. Create Observatory.Setup module (setup/clean actions)
3. Create Observatory.Quality module (lint/format/check)
4. Update quick-start.ps1 to use new modules

**Validation**:
- setup, clean, lint, format, check actions work identically
- serve action works in all modes (foreground, background, new window)

### Phase 3: Test & API Modules
**Tasks**:
1. Create Observatory.Tests module (test orchestration)
2. Create Observatory.Api module (API testing, key management)
3. Update quick-start.ps1 to use remaining modules
4. Extract Invoke-Demo to use modules

**Validation**:
- test action with all filters works identically
- demo action runs complete workflow
- keys, health, analyze actions work

### Phase 4: Refactor Supporting Scripts
**Tasks**:
1. Update `scripts/validation.ps1` to use Observatory modules
2. Update `scripts/performance-validation.ps1` to use modules
3. Update `scripts/test-dx-features.ps1` to use modules
4. Ensure output consistency across all scripts

**Validation**:
- All scripts in `scripts/` use consistent output patterns
- No functionality regression in any script
- Verbose mode works consistently

### Phase 5: Finalization & Documentation
**Tasks**:
1. Add Pester tests for key module functions
2. Update module documentation (comment-based help)
3. Create developer guide for module usage
4. Clean up any remaining duplication
5. Final validation of all actions and scripts

**Validation**:
- Complete test pass of all actions
- All flags and parameters work
- Documentation is accurate and complete

## Benefits

### Maintainability
- Each module has single responsibility (~200 lines max per module)
- Easy to locate and modify specific functionality
- Clear dependency tree

### Consistency
- All scripts use same UI functions from Observatory.UI
- Standardized error handling and verbosity control
- Uniform output patterns

### Reusability
- Other Observatory scripts can import modules
- Future features can leverage existing modules
- External automation can use modules directly

### Testability
- Functions can be unit tested with Pester
- Mocking and injection easier with modules
- Clear interfaces between modules

### Extensibility
- New actions can be added as new modules
- Existing modules can be enhanced without touching others
- Third-party scripts can extend Observatory functionality

## Non-Functional Requirements

### NFR-001: Zero Regression
All existing functionality must work identically after refactoring. No behavior changes.

### NFR-002: Output Consistency
All scripts must use Observatory.UI module for consistent output formatting.

### NFR-003: Performance
Module loading overhead must be <100ms. No noticeable slowdown in script execution.

### NFR-004: Backward Compatibility
quick-start.ps1 command-line interface must remain unchanged. All existing parameters work.

### NFR-005: Documentation
All exported functions must have comment-based help with examples.

### NFR-006: Configuration Centralization
Zero hardcoded configuration values in code. All config must be in `observatory.config.json`.

## Success Criteria

1. ✅ quick-start.ps1 reduced from 1,666 lines to ~150 lines
2. ✅ All 13 actions work identically to current version
3. ✅ All parameters and flags validated and functional
4. ✅ Supporting scripts (validation, performance, test-dx) use modules
5. ✅ Consistent output patterns across all scripts
6. ✅ Module documentation complete with examples
7. ✅ No performance regression (script execution time within 10%)
8. ✅ All existing tests pass without modification
9. ✅ All configuration centralized in observatory.config.json
10. ✅ Zero hardcoded config values in any script

## Migration Strategy

### For Users
No changes required. quick-start.ps1 interface remains identical.

### For Developers
1. Import Observatory modules in new scripts:
   ```powershell
   Import-Module .\modules\Observatory.UI
   Import-Module .\modules\Observatory.Core
   ```
2. Use standard UI functions instead of custom Write-Host calls
3. Reference module documentation for available functions

### For Future Features
1. Create new module if functionality is substantial
2. Add to existing module if it fits the responsibility
3. Always use Observatory.UI for output
4. Follow existing patterns for verbosity control

## Risks & Mitigations

### Risk: Breaking Changes
**Mitigation**: Comprehensive testing at each phase. Keep original script until full validation.

### Risk: Module Loading Overhead
**Mitigation**: Profile module load time. Lazy load modules only when needed.

### Risk: Increased Complexity
**Mitigation**: Clear module organization. Good documentation. Consistent patterns.

### Risk: Difficult Debugging
**Mitigation**: Modules make call stack deeper. Add debug logging. Use -Verbose mode.

## Open Questions

1. Should we create a single Observatory module with sub-modules or keep them separate?
2. Where should module tests live? Adjacent to modules or in tests/ directory?
3. Should we version the modules independently or as a suite?
4. Do we need a module loader/bootstrap script for external use?
5. Should we support environment-specific config overrides (e.g., `.local.config.json`)?
6. Should config support environment variable interpolation (e.g., `${ENV_VAR}`)?

## Related Work

- **Feature 001**: Observatory service implementation
- **Feature 002**: Developer experience upgrades (current quick-start.ps1 features)
- **Feature 003**: Multi-agent collaboration (would benefit from module structure)

## Acceptance Criteria

- [ ] Configuration file created with all settings
- [ ] All modules created with manifests
- [ ] quick-start.ps1 reduced to ~150 lines
- [ ] All 13 actions work identically
- [ ] Supporting scripts use modules
- [ ] Output consistency validated
- [ ] Module documentation complete
- [ ] No test failures
- [ ] Performance validated (no slowdown)
- [ ] No hardcoded config in any script
- [ ] Config management functions tested
- [ ] Code review passed

---

**Next Steps**: Review and approve proposal, then begin Phase 1 implementation.
