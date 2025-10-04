# Getting Started with Atrium Observatory

**Status**: Development Phase (Phase 1-2 Complete, Phase 3 In Progress)

This guide covers how to use the Observatory service in its current state and how it will work in production.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Current Development State](#current-development-state)
3. [API Key Management](#api-key-management)
4. [Testing the Service](#testing-the-service)
5. [Production Deployment Path](#production-deployment-path)
6. [Architecture Overview](#architecture-overview)

---

## Quick Start

### 1. First-Time Setup

```powershell
# Navigate to service directory
cd services/observatory

# Run setup (creates venv, installs dependencies)
.\quick-start.ps1 setup

# Run tests to verify installation
.\quick-start.ps1 test
```

### 2. Start the Development Server

```powershell
# Start server on default port 8000
.\quick-start.ps1 serve

# Or specify a custom port
.\quick-start.ps1 serve -Port 8001
```

### 3. Access the API Documentation

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Current Development State

### ✅ What's Working (Phases 1-2 Complete)

**Phase 1.3 - Database & Endpoints**:
- ✅ Database models with SQLite storage
- ✅ TTL enforcement (30-day results, 90-day metadata)
- ✅ Audit logging system
- ✅ POST `/api/v1/analyze` - Submit analysis requests
- ✅ GET `/api/v1/analyze/{id}` - Retrieve results
- ✅ POST `/api/v1/analyze/{id}/cancel` - Cancel analysis
- ✅ GET `/health` - Health check

**Phase 2 - Authentication & Rate Limiting**:
- ✅ Three-tier access control (public/api_key/partner)
- ✅ Bearer token authentication
- ✅ Rate limiting (10/60/600 req/min by tier)
- ✅ GET `/metrics` - Usage statistics (auth required)

### 🔄 In Progress (Phase 3)

- 🔄 Batch analysis endpoints
- 🔄 Redis job queue
- 🔄 Webhook notifications

### ⏳ Not Yet Implemented (Phases 4-5)

- ⏳ Web interface
- ⏳ Example conversation library
- ⏳ Production deployment
- ⏳ Database-backed API key management
- ⏳ OAuth2 for partner tier

---

## API Key Management

### Current State (Phase 2 - Development)

**Storage**: In-memory dictionary (ephemeral)
**Scope**: Local development and testing only
**Limitation**: Keys reset when server restarts

### How to Generate and Use API Keys (Development)

#### Option 1: Using Python REPL

```powershell
# Start Python in the virtual environment
.\.venv\Scripts\python.exe

# In Python REPL:
from app.middleware.auth import generate_api_key, register_api_key

# Generate a new API key
api_key = generate_api_key()
print(f"Your API Key: {api_key}")

# Register it (tier can be 'api_key' or 'partner')
register_api_key(api_key, tier="api_key")

# Key is now active until server restarts
```

#### Option 2: Add to Startup Script

Create a file `services/observatory/register_keys.py`:

```python
"""Register development API keys on startup."""

from app.middleware.auth import register_api_key, generate_api_key

# Generate and register keys
dev_key = "dev_test_key_12345678901234567890"
partner_key = "partner_test_key_1234567890123456"

register_api_key(dev_key, tier="api_key")
register_api_key(partner_key, tier="partner")

print(f"API Key (60 req/min): {dev_key}")
print(f"Partner Key (600 req/min): {partner_key}")
```

Then import in `app/main.py` after startup:

```python
# After app initialization, before running
if settings.environment == "development":
    import register_keys  # Auto-registers dev keys
```

#### Option 3: Environment Variable

Set in `.env`:

```env
# Development keys (for testing)
DEV_API_KEY=your_dev_key_here_32_characters
```

Then register on startup programmatically.

### Using Your API Key

#### PowerShell:
```powershell
$apiKey = "your_api_key_here"
$headers = @{
    "Authorization" = "Bearer $apiKey"
    "Content-Type" = "application/json"
}

# Test authentication
Invoke-WebRequest -Uri "http://localhost:8000/metrics" -Headers $headers

# Submit analysis with API key
$body = @{
    conversation_text = "Human: Hello\nAI: Hi there!"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/analyze" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

#### cURL:
```bash
# Test authentication
curl -H "Authorization: Bearer your_api_key_here" \
     http://localhost:8000/metrics

# Submit analysis
curl -X POST http://localhost:8000/api/v1/analyze \
     -H "Authorization: Bearer your_api_key_here" \
     -H "Content-Type: application/json" \
     -d '{"conversation_text": "Human: Hello\nAI: Hi there!"}'
```

#### Python:
```python
import httpx

api_key = "your_api_key_here"
headers = {"Authorization": f"Bearer {api_key}"}

async with httpx.AsyncClient() as client:
    # Check metrics
    response = await client.get(
        "http://localhost:8000/metrics",
        headers=headers
    )
    print(response.json())
    
    # Submit analysis
    response = await client.post(
        "http://localhost:8000/api/v1/analyze",
        headers=headers,
        json={"conversation_text": "Human: Hello\nAI: Hi there!"}
    )
    print(response.json())
```

---

## Testing the Service

### Test Without Authentication (Public Tier)

```powershell
# Health check (no auth needed)
.\quick-start.ps1 health

# Public tier allows 10 requests/minute
Invoke-WebRequest -Uri "http://localhost:8000/health"

# Analysis endpoint (public tier)
$body = @{
    conversation_text = "Human: Test\nAI: Response"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/analyze" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### Test With Authentication

```powershell
# Generate and register a test key (in Python REPL first)

# Then use it
$headers = @{"Authorization" = "Bearer your_key_here"}

# Access metrics (requires auth)
Invoke-WebRequest -Uri "http://localhost:8000/metrics" -Headers $headers

# Higher rate limits (60/min vs 10/min for public)
for ($i = 1; $i -le 15; $i++) {
    Invoke-WebRequest -Uri "http://localhost:8000/health" -Headers $headers
}
```

### Run Full Demo

```powershell
# Automated demo of all features
.\quick-start.ps1 demo
```

---

## Production Deployment Path

### Phase 5: Database-Backed API Keys

**Migration Plan**:

1. **Create API Key Model** (`app/models/database.py`):
```python
class ApiKey(Base):
    """API key model for production."""
    __tablename__ = "api_keys"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    key_hash = Column(String(64), unique=True, nullable=False)
    name = Column(String(255), nullable=False)  # User-friendly name
    tier = Column(String(20), nullable=False)  # api_key, partner
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Usage tracking
    request_count = Column(Integer, default=0)
    
    # Metadata
    owner_email = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
```

2. **Create Key Management Endpoints** (`app/api/v1/admin.py`):
```python
@router.post("/admin/api-keys")
async def create_api_key(
    name: str,
    tier: str,
    expires_days: Optional[int] = None,
    # Requires admin authentication
):
    """Generate a new API key."""
    key = generate_api_key()
    key_hash = hash_api_key(key)
    
    # Store in database
    api_key = ApiKey(
        key_hash=key_hash,
        name=name,
        tier=tier,
        expires_at=datetime.utcnow() + timedelta(days=expires_days) if expires_days else None
    )
    db.add(api_key)
    await db.commit()
    
    # Return key ONCE (never shown again)
    return {
        "api_key": key,  # Plain text, show once
        "name": name,
        "tier": tier,
        "expires_at": api_key.expires_at
    }

@router.get("/admin/api-keys")
async def list_api_keys():
    """List all API keys (without secrets)."""
    # Return list of keys with metadata

@router.delete("/admin/api-keys/{key_id}")
async def revoke_api_key(key_id: str):
    """Revoke an API key."""
    # Set is_active = False
```

3. **Update AuthMiddleware** to check database:
```python
async def validate_api_key_db(api_key: str, db: AsyncSession) -> Optional[ApiKey]:
    """Validate API key against database."""
    key_hash = hash_api_key(api_key)
    
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.key_hash == key_hash,
            ApiKey.is_active == True
        )
    )
    api_key_obj = result.scalar_one_or_none()
    
    if api_key_obj:
        # Check expiration
        if api_key_obj.expires_at and datetime.utcnow() > api_key_obj.expires_at:
            return None
        
        # Update last used
        api_key_obj.last_used_at = datetime.utcnow()
        api_key_obj.request_count += 1
        await db.commit()
        
        return api_key_obj
    
    return None
```

### Phase 5: Web Interface for Key Management

**User Dashboard** (`/dashboard`):
- View your API keys
- Generate new keys
- Revoke keys
- View usage statistics
- Set key expiration dates

**Registration Flow**:
1. User visits `/register`
2. Provides email and creates account
3. Email verification
4. Auto-generates first API key
5. Shows key once (download/copy)

### Phase 5: Redis for Distributed Rate Limiting

**Migration from In-Memory**:

```python
class RateLimiter:
    """Redis-backed rate limiter for production."""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)
    
    async def check_rate_limit(self, identifier: str, tier: str) -> Dict:
        """Check rate limit using Redis."""
        limits = TierLimits.get_limits(tier)
        now = time.time()
        
        # Redis key for minute window
        key_minute = f"ratelimit:{identifier}:minute"
        
        # Increment and check
        pipe = self.redis.pipeline()
        pipe.incr(key_minute)
        pipe.expire(key_minute, 60)
        count, _ = await pipe.execute()
        
        if count > limits["requests_per_minute"]:
            return {"allowed": False, ...}
        
        return {"allowed": True, ...}
```

**Benefits**:
- Shared rate limits across multiple server instances
- Persistence across restarts
- Proper distributed system support

### Public Server Deployment

**Infrastructure**:
```yaml
# docker-compose.production.yml
services:
  observatory:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres/observatory
      - REDIS_URL=redis://redis:6379
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - postgres
      - redis
      - ollama
    ports:
      - "8000:8000"
  
  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
  
  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
```

**HTTPS Configuration** (nginx.conf):
```nginx
server {
    listen 443 ssl http2;
    server_name observatory.atrium.ai;
    
    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    
    location / {
        proxy_pass http://observatory:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Deployment Steps**:
```bash
# 1. Build and deploy
docker-compose -f docker-compose.production.yml up -d

# 2. Run migrations
docker-compose exec observatory python -m alembic upgrade head

# 3. Create admin user
docker-compose exec observatory python scripts/create_admin.py

# 4. Generate system API keys
docker-compose exec observatory python scripts/generate_keys.py
```

---

## Architecture Overview

### Current (Development)

```
┌─────────────────────────────────────────────┐
│         Client (Browser/API Consumer)        │
└────────────────┬────────────────────────────┘
                 │ HTTP Request
                 ↓
┌─────────────────────────────────────────────┐
│            FastAPI Application               │
│  ┌─────────────────────────────────────┐    │
│  │     CORS Middleware                 │    │
│  └──────────────┬──────────────────────┘    │
│  ┌──────────────↓──────────────────────┐    │
│  │  Rate Limit Middleware (In-Memory)  │    │
│  └──────────────┬──────────────────────┘    │
│  ┌──────────────↓──────────────────────┐    │
│  │  Auth Middleware (In-Memory Keys)   │    │
│  └──────────────┬──────────────────────┘    │
│  ┌──────────────↓──────────────────────┐    │
│  │         API Endpoints               │    │
│  │  • /health                          │    │
│  │  • /api/v1/analyze                  │    │
│  │  • /api/v1/analyze/{id}             │    │
│  │  • /metrics                         │    │
│  └──────────────┬──────────────────────┘    │
└─────────────────┼────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    ↓             ↓             ↓
┌─────────┐  ┌─────────┐  ┌─────────┐
│ SQLite  │  │ Ollama  │  │ Logging │
│  (DB)   │  │  (AI)   │  │ (Audit) │
└─────────┘  └─────────┘  └─────────┘
```

### Production (Phase 5)

```
┌──────────────────────────────────────────────┐
│              Load Balancer (nginx)            │
│               HTTPS Termination               │
└───────────────────┬──────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
    ┌──────┐   ┌──────┐   ┌──────┐
    │ App  │   │ App  │   │ App  │
    │ #1   │   │ #2   │   │ #3   │
    └──┬───┘   └──┬───┘   └──┬───┘
       │          │          │
       └──────────┼──────────┘
                  │
    ┌─────────────┼─────────────┐
    ↓             ↓             ↓
┌──────────┐  ┌────────┐  ┌─────────┐
│PostgreSQL│  │ Redis  │  │ Ollama  │
│ (Keys,   │  │ (Rate  │  │ (AI)    │
│ Results) │  │ Limit) │  │         │
└──────────┘  └────────┘  └─────────┘
```

---

## Next Steps

1. **Immediate** (for development):
   - Generate test API keys using Python REPL
   - Test endpoints with different tiers
   - Verify rate limiting behavior

2. **Short Term** (Phase 3-4):
   - Wait for batch processing completion
   - Add web interface for key management
   - Create example conversation library

3. **Long Term** (Phase 5):
   - Migrate to PostgreSQL
   - Implement Redis rate limiting
   - Deploy to production infrastructure
   - Set up monitoring and alerts

---

## Troubleshooting

### "Server won't start"
```powershell
# Check for port conflicts
netstat -ano | findstr :8000

# Try different port
.\quick-start.ps1 serve -Port 8001
```

### "API key not working"
- Keys are in-memory only - regenerate after server restart
- Check format: `Authorization: Bearer <key>`
- Verify key was registered with `register_api_key()`

### "Rate limit too strict"
For development, you can temporarily modify limits in `app/core/config.py`:
```python
rate_limit_public: int = 1000  # Increase for testing
```

### "Need to reset everything"
```powershell
.\quick-start.ps1 clean  # Removes venv, data, caches
.\quick-start.ps1 setup  # Fresh start
```

---

## Additional Resources

- **OpenAPI Docs**: http://localhost:8000/docs (when server running)
- **Health Check**: http://localhost:8000/health
- **Source Code**: https://github.com/tmorgan181/atrium-grounds
- **Issues/Questions**: Create GitHub issue with `[Observatory]` prefix

---

**Version**: 0.1.0 (Development)  
**Last Updated**: 2025-10-04  
**Phase**: 2 (Auth & Rate Limiting Complete)
