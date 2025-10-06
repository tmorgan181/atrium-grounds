# Claude Code Implementation Guide: Web Interface

**Feature**: 006-unified-microservice-interface
**Agent**: Claude Code (Sonnet 4.5)
**Role**: Primary implementation agent

## Quick Context

You're building a FastAPI web app that acts as a stateless proxy to Observatory API. Think of it as a public-facing demo site that makes conversation analysis accessible to non-technical users.

**Stack**: Python 3.11 + FastAPI + Jinja2 (server-side rendering)
**No**: Database, frontend framework, auth logic, session state
**Yes**: Static JSON caching, API key passthrough, minimal code

## Implementation Priorities

### Phase 1: Core Infrastructure (Day 1)
1. Setup uv project (`pyproject.toml`)
2. Create FastAPI app skeleton (`app/main.py`)
3. Add Observatory client (`app/client.py` with httpx)
4. Create base template (`app/templates/base.html`)
5. Add static file serving

### Phase 2: Cached Demos (Day 2)
1. Create example generator script
2. Generate 5-10 cached examples
3. Implement `/examples/{id}` endpoint
4. Create demo page template
5. Test cached flow (<100ms target)

### Phase 3: Live Proxy (Day 3)
1. Implement `/api/analyze` proxy
2. Add API key passthrough logic
3. Handle Observatory errors gracefully
4. Test live flow (<3s target)
5. Implement rate limit display

### Phase 4: Polish (Day 4-5)
1. Create landing page
2. Add API documentation page
3. Implement health check display
4. Write tests (pytest)
5. Create Dockerfile

## Key Patterns

### 1. Observatory Client (app/client.py)
```python
import httpx
from app.config import settings

class ObservatoryClient:
    def __init__(self):
        self.base_url = settings.observatory_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def analyze(self, conversation: list[dict], api_key: str | None = None):
        headers = {"X-API-Key": api_key} if api_key else {}
        response = await self.client.post(
            f"{self.base_url}/api/v1/analyze",
            json={"conversation": conversation},
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def health(self):
        response = await self.client.get(f"{self.base_url}/health")
        return {
            "status": "operational" if response.status_code == 200 else "offline",
            "response_time_ms": int(response.elapsed.total_seconds() * 1000)
        }
```

### 2. Cached Example Loading (app/routers/examples.py)
```python
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter()
EXAMPLES_DIR = Path(__file__).parent.parent / "static" / "examples"

@router.get("/examples/{example_id}")
async def get_example(example_id: str):
    # Validate ID (prevent path traversal)
    if not example_id.replace("-", "").isalnum():
        raise HTTPException(400, "Invalid example ID")

    example_path = EXAMPLES_DIR / f"{example_id}.json"
    if not example_path.exists():
        raise HTTPException(404, "Example not found")

    with open(example_path) as f:
        return json.load(f)
```

### 3. Page Rendering (app/routers/pages.py)
```python
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "service_name": "Atrium Observatory",
        "tagline": "Conversation analysis made accessible"
    })

@router.get("/demo")
async def demo_page(request: Request):
    # List available examples
    examples = [
        {"id": "dialectic-simple", "title": "Dialectic - Simple"},
        # ... load from EXAMPLES_DIR
    ]
    return templates.TemplateResponse("demo.html", {
        "request": request,
        "examples": examples
    })
```

### 4. Template Pattern (app/templates/base.html)
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Atrium Grounds{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    {% include "components/nav.html" %}

    <main>
        {% block content %}{% endblock %}
    </main>

    {% block scripts %}{% endblock %}
</body>
</html>
```

## Testing Strategy

### Contract Tests (tests/test_contract.py)
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_landing_page_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_example_endpoint_returns_json():
    response = client.get("/examples/dialectic-simple")
    assert response.status_code == 200
    data = response.json()
    assert "conversation" in data
    assert "analysis" in data
```

### Integration Tests (tests/test_integration.py)
```python
@pytest.mark.asyncio
async def test_full_user_flow():
    # 1. Visit landing page
    response = client.get("/")
    assert "Observatory" in response.text

    # 2. Load cached example
    response = client.get("/examples/dialectic-simple")
    example = response.json()

    # 3. View demo page
    response = client.get("/demo")
    assert response.status_code == 200

    # 4. Check health
    response = client.get("/api/health")
    assert response.status_code in [200, 503]  # Allow Observatory to be down
```

## Configuration (app/config.py)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    observatory_url: str = "http://localhost:8000"
    app_host: str = "0.0.0.0"
    app_port: int = 8080

    class Config:
        env_file = ".env"

settings = Settings()
```

## File Checklist

**Core** (must have):
- [ ] app/main.py (FastAPI app)
- [ ] app/config.py (settings)
- [ ] app/client.py (Observatory HTTP client)
- [ ] app/routers/pages.py (HTML routes)
- [ ] app/routers/proxy.py (API proxy)
- [ ] app/templates/base.html (layout)
- [ ] app/templates/index.html (landing)
- [ ] app/templates/demo.html (demo interface)

**Static** (must have):
- [ ] app/static/examples/*.json (5-10 cached examples)
- [ ] app/static/css/style.css (minimal styling)

**Infrastructure** (must have):
- [ ] Dockerfile
- [ ] pyproject.toml
- [ ] .env.example
- [ ] README.md

**Tests** (must have):
- [ ] tests/test_pages.py (page routes)
- [ ] tests/test_proxy.py (API proxy)
- [ ] tests/test_integration.py (full flows)

## Common Pitfalls

❌ **Don't** add a database (stateless principle)
❌ **Don't** implement auth logic (passthrough only)
❌ **Don't** cache user-submitted data (privacy)
❌ **Don't** use frontend frameworks (SSR only)
❌ **Don't** add complex state management

✅ **Do** keep it minimal (~500 LOC total)
✅ **Do** use Observatory API key passthrough
✅ **Do** cache only curated examples (static JSON)
✅ **Do** handle Observatory errors gracefully
✅ **Do** test with actual Observatory service

## Example Generator Script (scripts/generate_examples.py)
```python
import asyncio
import json
from pathlib import Path
from app.client import ObservatoryClient

CURATED_CONVERSATIONS = [
    {
        "id": "dialectic-simple",
        "title": "Dialectic Pattern - Simple",
        "conversation": [
            {"speaker": "A", "content": "Truth is objective..."},
            {"speaker": "B", "content": "But perception shapes reality..."}
        ]
    },
    # ... more examples
]

async def generate_examples():
    client = ObservatoryClient()
    output_dir = Path("app/static/examples")
    output_dir.mkdir(parents=True, exist_ok=True)

    for item in CURATED_CONVERSATIONS:
        print(f"Generating {item['id']}...")
        analysis = await client.analyze(item["conversation"])

        example = {
            **item,
            "analysis": analysis,
            "metadata": {
                "type": "dialectic",  # categorize
                "complexity": "simple"
            }
        }

        with open(output_dir / f"{item['id']}.json", "w") as f:
            json.dump(example, f, indent=2)

    print(f"Generated {len(CURATED_CONVERSATIONS)} examples")

if __name__ == "__main__":
    asyncio.run(generate_examples())
```

## Constitution Alignment

Every line of code should align with constitution v1.3.1:

- **I. Language**: No technical jargon in user-facing HTML
- **II. Boundaries**: No private data access, Observatory API only
- **III. Progressive Disclosure**: Cached → Live → Custom tiers
- **IV. Multi-Interface**: Web (humans) + API passthrough (developers)
- **V. Invitation**: "Try it now", no barriers
- **VI. Independence**: Separate service, clean boundaries
- **VII. Stewardship**: Quality examples, curator-controlled
- **VIII. Pragmatism**: Minimal code, justified choices

### Technical Documentation Exception

**Constitution I** (Language & Tone) applies to public pages ONLY:
- `/` (landing) - ❌ No technical jargon (say "Try conversation analysis" not "POST to /api/v1/analyze")
- `/demo` (demo interface) - ❌ No technical jargon (say "Example results" not "JSON response from REST endpoint")
- `/docs` (API documentation) - ✅ Technical terms allowed (developer-facing content)

**Why this matters**: API documentation at `/docs` is explicitly for developers who need precise technical language. Using "endpoint", "REST", "JSON schema" is appropriate and expected in this context. This does not violate Constitution I because:
1. Docs are opt-in (not landing page)
2. Target audience is technical (developers integrating with API)
3. Precision required for correct API usage

**Example**:
```python
# Landing page template - NO jargon
<h1>Explore Conversation Patterns</h1>
<p>See how ideas develop and connect in dialogue</p>

# API docs template - Technical terms OK
<h1>API Reference</h1>
<p>POST /api/v1/analyze - Submit conversation for pattern analysis</p>
<code>Content-Type: application/json</code>
```

## Success Metrics

- ✅ Cached demos <100ms
- ✅ Live demos <3s
- ✅ 10 concurrent users comfortable
- ✅ Zero private data exposure
- ✅ ~500 LOC total
- ✅ All tests pass
- ✅ No dependencies on Observatory internals

---

**For Claude Code agents**: Follow quickstart.md for validation, prioritize minimal code, align with constitution, test thoroughly
