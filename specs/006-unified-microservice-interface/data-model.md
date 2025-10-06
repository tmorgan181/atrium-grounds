# Data Model: Unified Microservice Interface

**Feature**: 006-unified-microservice-interface
**Date**: 2025-01-05
**Type**: Stateless proxy service (minimal data entities)

## Overview

The web interface is a stateless proxy to Observatory API. It maintains no persistent data. All entities below are runtime representations only (no database).

## Entities

### 1. CachedExample

**Purpose**: Pre-generated conversation analysis stored as static JSON

**Fields**:
- `id` (string): Unique identifier (e.g., "dialectic-simple")
- `title` (string): Display name (e.g., "Dialectic Pattern - Simple")
- `description` (string): Brief explanation for users
- `conversation` (list[dict]): Original conversation turns
- `analysis` (dict): Pre-generated Observatory response
  - `patterns` (list[dict]): Detected patterns
  - `sentiment` (dict): Sentiment analysis
  - `topics` (list[str]): Extracted topics
- `metadata` (dict):
  - `type` (string): Category (dialectic, collaborative, exploration)
  - `complexity` (string): simple | moderate | complex
  - `generated_at` (datetime): When analysis was cached

**Storage**: `app/static/examples/{id}.json`

**Validation**:
- `id` must be alphanumeric + hyphens only
- `conversation` must have ≥2 turns
- `analysis` must match Observatory response schema

**Conversation Format** (required for all examples):
- Each turn: `{"speaker": str, "content": str}`
- Speaker IDs: Single capital letter (A, B, C...) or role name ("User", "Assistant")
- Content: 50-500 characters per turn recommended
- Total turns: 2-20 (optimized for analysis)
- Character whitelist: UTF-8 alphanumeric + standard punctuation

**Example**:
```json
{
  "id": "dialectic-simple",
  "title": "Dialectic Pattern - Simple",
  "description": "Two perspectives exploring truth through dialogue",
  "conversation": [
    {"speaker": "A", "content": "Truth is objective..."},
    {"speaker": "B", "content": "But perception shapes..."}
  ],
  "analysis": {
    "patterns": [{"type": "dialectic", "confidence": 0.89}],
    "sentiment": {"overall": "neutral", "trajectory": "stable"},
    "topics": ["epistemology", "perception"]
  },
  "metadata": {
    "type": "dialectic",
    "complexity": "simple",
    "generated_at": "2025-01-05T10:00:00Z"
  }
}
```

### 2. DemoRequest

**Purpose**: User-initiated LIVE demo request (not for cached examples)

**Fields**:
- `conversation` (list[dict]): Conversation from cached example OR user-provided
- `source` (string): "cached_example" | "user_input"
- `example_id` (string | null): ID if source is cached_example
- `api_key` (string | null): Optional Observatory API key
- `timestamp` (datetime): When request was made

**Lifecycle**:
- **Cached demo flow**: User clicks "Try Live" → Load example conversation → Create DemoRequest with source="cached_example" → Call Observatory → Render → Discard
- **Custom input flow**: User pastes conversation → Create DemoRequest with source="user_input" → Call Observatory → Render → Discard

**Validation**:
- If source="cached_example", example_id MUST be valid
- If source="user_input", conversation MUST be provided
- api_key optional for both flows

### 3. AnalysisRequest

**Purpose**: Custom user conversation analysis (authenticated)

**Fields**:
- `conversation` (list[dict]): User-provided conversation
  - Each turn: `{"speaker": str, "content": str}`
- `api_key` (string): Required Observatory API key
- `timestamp` (datetime): When request was made

**Lifecycle**: User submits form → proxied to Observatory → response rendered → discarded

**Validation**:
- `conversation` max 10k characters total
- `conversation` must have ≥2 turns
- `api_key` required (validated by Observatory)
- Character whitelist: alphanumeric, spaces, punctuation only

### 4. AnalysisResult

**Purpose**: Observatory API response (runtime only, not stored)

**Fields** (matches Observatory /analyze response):
- `id` (string): Analysis ID from Observatory
- `patterns` (list[dict]): Detected patterns
  - `type` (string): Pattern name
  - `confidence` (float): 0.0 - 1.0
  - `description` (string)
- `sentiment` (dict):
  - `overall` (string): positive | negative | neutral
  - `trajectory` (string): ascending | descending | stable
  - `turns` (list[dict]): Per-turn sentiment
- `topics` (list[str]): Extracted topics
- `metadata` (dict):
  - `duration_ms` (int): Analysis time
  - `model_version` (string): Observatory version

**Lifecycle**: Received from Observatory → rendered in template → discarded

**Example**:
```json
{
  "id": "analysis_abc123",
  "patterns": [
    {
      "type": "dialectic",
      "confidence": 0.89,
      "description": "Thesis-antithesis structure detected"
    }
  ],
  "sentiment": {
    "overall": "neutral",
    "trajectory": "stable",
    "turns": [
      {"turn": 1, "sentiment": "neutral", "score": 0.02},
      {"turn": 2, "sentiment": "neutral", "score": -0.01}
    ]
  },
  "topics": ["epistemology", "perception", "truth"],
  "metadata": {
    "duration_ms": 1823,
    "model_version": "observatory-v1"
  }
}
```

### 5. HealthStatus

**Purpose**: Observatory service health (runtime only)

**Fields** (from Observatory /health endpoint):
- `status` (string): operational | degraded | offline
- `response_time_ms` (int): Health check duration
- `last_checked` (datetime): When status was retrieved

**Lifecycle**: Fetched on page load → displayed → discarded

**Example**:
```json
{
  "status": "operational",
  "response_time_ms": 45,
  "last_checked": "2025-01-05T14:32:10Z"
}
```

## Data Flow

### Cached Demo Flow
```
User clicks "Try Example"
  → Load CachedExample from static JSON
  → Render analysis in template
  → Display (no API call)
```

### Live Demo Flow
```
User clicks "Try Live"
  → Create DemoRequest (ephemeral)
  → Call Observatory /analyze with example conversation
  → Receive AnalysisResult
  → Render in template
  → Discard all objects
```

### Custom Analysis Flow
```
User submits conversation + API key
  → Create AnalysisRequest (ephemeral)
  → Proxy to Observatory /analyze with auth header
  → Receive AnalysisResult
  → Render in template
  → Discard all objects (no caching of user data)
```

### Health Check Flow
```
Page load
  → Call Observatory /health
  → Receive HealthStatus
  → Display status badge
  → Discard
```

## State Management

**No persistent state**. Web interface is stateless:
- No database
- No session storage
- No user data retention
- API keys stored in browser localStorage only (client-side)

**Implications**:
- Horizontal scaling trivial (any instance serves any request)
- No data migration needed
- No backup/restore concerns
- Privacy by design (no user data stored)

## Validation Rules

**Input Sanitization** (all user inputs):
- Max length enforcement
- Character whitelist (prevent injection)
- HTML escaping in templates
- CORS headers restrict origins

**Observatory Response Trust**:
- Assume Observatory validates and sanitizes
- No additional validation of analysis results
- Trust rate limiting enforcement from Observatory

## Schema Versioning

**Current Version**: v1 (MVP)

**Future Considerations**:
- If Observatory API changes, update proxy layer only
- Static examples can be regenerated with new schema
- No database migrations (stateless)

---

**Data model by**: Claude Code (Sonnet 4.5)
**Schema source**: Observatory API documentation
