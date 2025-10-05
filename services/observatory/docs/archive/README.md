# Documentation Archive

This directory contains documentation that has been superseded or is no longer actively maintained but kept for historical reference.

---

## Archived Documents

### FEATURE-001-CHECKPOINT.md
**Status**: Superseded by Feature 002 completion
**Date**: 2025-01-04
**Reason**: Feature 001 checkpoint taken, now in main branch. Feature 002 is the active development branch.

**Historical Context**: Documents the completion state of the Observatory service's initial implementation, including:
- Core analysis engine
- REST API with authentication
- Rate limiting and security
- Testing infrastructure status

**Replacement**: See `README.md` in root and `VALIDATION-CHECKLIST-002.md` for current status.

---

### LINTING.md
**Status**: Superseded by Feature 002 implementation
**Date**: Planning document, implemented in T013-T015
**Reason**: Linting, formatting, and type checking now integrated into `quick-start.ps1`

**Historical Context**: Planning document for code quality tooling integration.

**Replacement**:
- `README.md` - Quick reference for `lint`, `format`, `check` commands
- `WORKFLOW.md` - Detailed workflow examples
- `MIGRATION-002.md` - Migration guide for new code quality features

---

### TEST-FILTERING.md
**Status**: Superseded by Feature 002 implementation
**Date**: Planning document, implemented in T008-T011
**Reason**: Test filtering now fully implemented with `-Unit`, `-Contract`, `-Integration`, `-Validation`, `-Coverage` flags

**Historical Context**: Planning document for test filtering feature.

**Replacement**:
- `README.md` - Quick reference for test filtering
- `WORKFLOW.md` - Detailed test filtering examples
- `MIGRATION-002.md` - Migration guide showing test filtering usage

---

### NEXT-STEPS.md
**Status**: Superseded by Feature 002 completion
**Date**: 2025-01-04
**Reason**: Priority 1 items (test filtering, linting, verbosity control) completed in Feature 002

**Historical Context**: Development roadmap created after Feature 001 completion, identified Feature 002 priorities.

**Replacement**:
- Feature 002 planning documents in `/specs/002-developer-experience-upgrades/`
- `VALIDATION-CHECKLIST-002.md` for completion status

---

## Why Keep These Files?

1. **Historical Reference** - Shows the evolution of the project
2. **Design Decisions** - Documents why certain approaches were chosen
3. **Learning Resource** - Demonstrates planning process
4. **Audit Trail** - Proof of thorough documentation practices

---

## Current Documentation

For active, up-to-date documentation, see:

**Root Level**:
- `README.md` - Main service documentation
- `WORKFLOW.md` - Developer workflow guide

**docs/**:
- `CLEAN-LOGGING.md` - Clean logging feature guide
- `MIGRATION-002.md` - Feature 002 migration guide
- `VALIDATION-CHECKLIST-002.md` - Feature 002 validation results

**docs/guides/**:
- `ENCODING-GUIDE.md` - PowerShell encoding best practices

**specs/**:
- `/specs/002-developer-experience-upgrades/` - Feature 002 specifications

---

**Last Updated**: 2025-10-05
**Maintained By**: Atrium Grounds Team
