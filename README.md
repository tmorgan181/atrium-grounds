# Atrium Grounds

[![CI](https://github.com/tmorgan181/atrium-grounds/actions/workflows/ci.yml/badge.svg)](https://github.com/tmorgan181/atrium-grounds/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Public service layer for the Atrium ecosystem. Provides curated access to AI collaboration research tools without exposing private archives.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Services](#services)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Overview

Atrium Grounds is the **public gateway** to Atrium's human-AI collaboration tools. It provides independent microservices that offer access to conversation analysis, dialectic frameworks, and AI exploration capabilities through progressive disclosure—sharing value without compromising privacy.

### Core Principles

- **Progressive Disclosure**: Reveal capabilities in trust layers
- **Ethical Boundaries**: Never access private archives directly
- **Multi-Interface Access**: Serve both humans and AI systems
- **Service Independence**: Enable multi-agent collaboration
- **Groundskeeper Stewardship**: Quality over growth

## Architecture

The project follows a three-layer model:

1. **Public Services** (this repo): APIs, web interfaces, CLI tools
2. **Private Playground**: Experimental research space (separate repo)
3. **Raw Archives**: Protected conversation data (never exposed)

Each service is:
- Self-contained and independently deployable
- Containerized with Docker
- API-first with OpenAPI documentation
- Technology-agnostic (Python/FastAPI recommended)

## Services

### Planned Services

- **Observatory**: Conversation analysis and pattern detection
- **Dialectic Engine**: Framework for exploring ideas through dialogue
- **Model Proxy**: Unified interface for AI model interactions
- **Memory API**: Structured access to curated conversation insights

*Services are added organically as needs emerge, not on fixed timelines.*

## Development

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package and project manager)
- Docker
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/tmorgan181/atrium-grounds.git
cd atrium-grounds

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Each service has its own setup - see service directories
# Typical service setup:
# cd services/<service-name>
# uv sync
# uv run python main.py
```

### Multi-Agent Collaboration

This project is developed collaboratively with AI assistants. See coordination protocols:

- `.github/copilot-instructions.md` - Development guidelines
- `.github/prompts/orient.prompt.md` - Orientation protocol
- `.specify/memory/constitution.md` - Project philosophy

### Workflows

- **CI**: Automated linting, testing, type checking, and commit attribution tracking
- **Claude Code**: AI assistance via `@claude` mentions
- **Claude Code Review**: Automated PR reviews

### Commit Attribution

AI agents include model and interface info for transparency:
```
<commit message>

via <model> @ <interface>
```

Examples: `via claude-sonnet-4.5 @ claude-code` or `via gpt-4 @ github-copilot`

CI automatically tracks and verifies agent attribution.

## Contributing

Contributions are welcome as the project matures. Current phase: establishing foundation patterns.

See `.specify/memory/constitution.md` for philosophical principles and technical standards.

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

*"The grounds need tending. The house remains private. The archives stay protected. And still, we welcome those who knock softly."*
