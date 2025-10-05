# Dual-Agent Workflow Proposal: Atrium Observatory Service

## Objective
Extract the Observatory functionality from the monolithic Flask app into a standalone FastAPI microservice, leveraging the strengths of two AI agents (Claude and Copilot) for efficient development and high code quality.

## Agent Roles and Responsibilities

### Claude (Primary Agent)
- Architect the overall service structure and interfaces
- Design and implement core algorithmic components:
  - Pattern analyzer (`app/core/analyzer.py`)
  - Input validator (`app/core/validator.py`)
  - Job management system (`app/core/jobs.py`)
- Coordinate task delegation and integration with Copilot
- Perform code reviews and ensure compliance with Atrium's constitution
- Make key architectural decisions and resolve blockers

### Copilot (Secondary Agent)
- Set up project infrastructure and development environment:
  - FastAPI project structure and dependencies (`pyproject.toml`)
  - Dockerfile and docker-compose configuration
  - Environment variable management (`.env` files)
- Implement API endpoints and middleware:
  - Authentication and authorization (`app/middleware/auth.py`)
  - Rate limiting using Redis (`app/middleware/ratelimit.py`)
  - Health check and metrics endpoints (`app/api/v1/health.py`)
- Write comprehensive test suites:
  - Unit tests for core components (`tests/unit/`)
  - Integration tests for API flows (`tests/integration/`)
  - Contract tests for endpoint behavior (`tests/contract/`)
- Assist with batch processing and async worker management:
  - Redis-based job queue (`app/core/queue.py`)
  - Async worker process (`app/core/worker.py`)
  - Webhook notifications (`app/core/notifications.py`)
- Handle production readiness tasks:
  - Logging configuration (`app/core/logging.py`)
  - Prometheus metrics collection (`app/core/metrics.py`)
  - API documentation (OpenAPI spec, README)
  - Deployment guides (`DEPLOY.md`)

## Collaboration Workflow

1. Task Planning and Delegation
   - Claude reviews the full task breakdown (`tasks.md`) and identifies parallelizable work streams
   - Infrastructure setup, boilerplate code, and testing tasks are delegated to Copilot
   - Core algorithmic components are assigned to Claude for focused development

2. Parallel Development and Regular Check-ins
   - Claude implements the analyzer, validator, and job system with regular check-ins
   - Copilot sets up the FastAPI project, Dockerfiles, and base endpoint structure
   - Frequent commits and descriptive pull requests keep the work aligned
   - Daily stand-ups or async status updates ensure smooth coordination

3. Code Integration and Review
   - API implementation and middleware integration is done via pair programming sessions
   - Claude reviews Copilot's infrastructure and endpoint code for quality and consistency
   - Copilot reviews Claude's core component code and suggests optimizations
   - Blockers and architectural decisions are discussed in GitHub issues

4. Testing and Quality Assurance
   - Copilot writes comprehensive unit, integration, and contract tests
   - All tests are run automatically via GitHub Actions on each pull request
   - Claude conducts manual testing and edge case analysis
   - Any issues or bugs found are logged and assigned for resolution

5. Production Readiness and Documentation
   - Copilot handles logging, metrics, and error reporting setup
   - API documentation is generated from code and reviewed by Claude
   - Deployment guides are written collaboratively and tested on staging
   - Final code review and testing is done before production release

## Key Milestones and Timeline

- Week 1: Core service setup and analysis engine implementation
  - FastAPI project structure and dependencies set up
  - Dockerfiles and docker-compose configuration created
  - Analyzer, validator, and job system components implemented
  - Unit tests for core components written and passing

- Week 2: Authentication, rate limiting, and API endpoint integration
  - Authentication middleware and API key management implemented  
  - Redis-based rate limiter middleware added
  - Core API endpoints (analyze, cancel, get) implemented
  - Integration and contract tests for API flows passing

- Week 3: Batch processing and async job management
  - Redis job queue and async worker process implemented
  - Batch analysis endpoint and job status tracking added
  - Webhook notification system for job updates created
  - Batch processing integration tests passing

- Week 4: Example conversations, web interface, and export functionality
  - Example conversation manifest and endpoints implemented
  - Web interface for exploring examples and documentation added
  - Export functionality for analysis results (JSON, CSV, Markdown) 
  - End-to-end tests for example flows and export passing

- Week 5: Production readiness, final polish, and documentation
  - Structured logging and Prometheus metrics added
  - Deployment guides written and tested on staging environment
  - API documentation finalized and published
  - Final code review, testing, and optimization completed
  - Production deployment and smoke tests

## Roles and Permissions

To enable smooth collaboration while maintaining security, we propose the following GitHub permissions:

- Claude (Primary Agent)
  - Admin access to the repository
  - Ability to push to main branch (with branch protection rules)
  - Code owner for core components (`app/core/`)
  - Required approver for all pull requests

- Copilot (Secondary Agent)  
  - Write access to the repository
  - Cannot push directly to main branch
  - Code owner for tests (`tests/`) and API (`app/api/`)
  - Can create and push to feature branches
  - Can request reviews and merge pull requests with Claude's approval

Both agents will follow the branch naming convention `feature/OBS-<task-id>-<description>` for all feature work. Commits will include task IDs in the message for traceability.

## Open Questions and Risks

1. **Ollama Model Compatibility**: The current specification assumes Ollama models can be integrated into the FastAPI service using either a REST client or a Python SDK. If the integration mechanism changes, the implementation tasks may need to be adjusted.

2. **Private Archive Access**: The workflow is designed to avoid direct access to private archives by focusing on the public-facing API. However, if any backend tasks require archive access, additional security measures and access controls will need to be put in place.

3. **Testing Complexity**: Writing comprehensive tests for all components and API flows may take more time than anticipated. We may need to adjust the timeline or prioritize certain test cases if the testing phase starts to impact the overall schedule.

4. **Performance and Scalability**: While the proposed architecture is designed for scalability, the actual performance characteristics will depend on the choice of cloud platform, instance sizes, and database configurations. Rigorous performance testing and optimization may be required before production deployment.

5. **Continuous Integration and Deployment**: The workflow assumes a CI/CD pipeline will be set up to automatically run tests, build the service, and deploy to staging and production environments. The specifics of this pipeline will need to be defined and implemented in addition to the service code.

## Conclusion

By leveraging the unique strengths of Claude and Copilot, this dual-agent workflow aims to efficiently and effectively extract the Observatory functionality into a standalone microservice. The clear division of responsibilities, frequent collaboration, and iterative development process will help ensure a high-quality, maintainable, and scalable service that adheres to the Atrium's architectural principles and ethical guidelines.

We believe this proposal strikes a balance between autonomy and coordination, enabling both agents to contribute meaningfully while maintaining a cohesive vision for the service. With well-defined tasks, milestones, and communication channels, we are confident in our ability to deliver the Observatory service on schedule and to the highest standards of quality.

As always, we welcome feedback and suggestions from the Atrium's leadership and the developer community. We look forward to working together to bring this critical piece of infrastructure to life.
