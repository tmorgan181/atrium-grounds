"""FastAPI application entrypoint for Observatory service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.models.database import init_database, start_cleanup_scheduler, stop_cleanup_scheduler
from app.api.v1 import analyze, health, batch, examples
from app.middleware import AuthMiddleware, RateLimitMiddleware
from app.core.dev_keys import auto_register_dev_keys


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    # Startup banner
    print("\n" + "=" * 70)
    print("   ⚡ ATRIUM OBSERVATORY")
    print("   Conversation Analysis Service")
    print("=" * 70)
    print(f"   Version: {__version__}")
    print(f"   API Docs: http://localhost:8000/docs")
    print("=" * 70 + "\n")
    
    # Startup: Initialize database and start TTL cleanup scheduler
    print("🔧 Initializing database...")
    await init_database()
    print("✓ Database ready\n")
    
    print("⏰ Starting cleanup scheduler...")
    start_cleanup_scheduler()
    print("✓ TTL cleanup active\n")

    # Auto-register development API keys if dev-api-keys.txt exists
    dev_keys = auto_register_dev_keys()
    if dev_keys:
        print("🔑 Development API keys registered:")
        if "dev_key" in dev_keys:
            print("   • API Key tier (60 req/min)")
        if "partner_key" in dev_keys:
            print("   • Partner tier (600 req/min)")
        print(f"   ✓ Loaded from dev-api-keys.txt\n")

    print("=" * 70)
    print("   🚀 SERVER READY")
    print("   Press CTRL+C to stop")
    print("=" * 70 + "\n")

    yield
    
    # Shutdown
    print("\n" + "=" * 70)
    print("   ⚠ Shutting down...")
    print("=" * 70 + "\n")
    stop_cleanup_scheduler()
    print("✓ Cleanup scheduler stopped")
    print("\n" + "=" * 70)
    print("   👋 Server stopped")
    print("=" * 70 + "\n")


app = FastAPI(
    title="Atrium Observatory API",
    description="Conversation analysis service for detecting patterns, themes, and insights",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication and rate limiting middleware
# Order matters: Rate limiting -> Auth (applied in reverse order)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(analyze.router, prefix="/api/v1", tags=["analysis"])
app.include_router(batch.router, prefix="/api/v1", tags=["batch"])
app.include_router(examples.router, tags=["examples"])
app.include_router(health.router, tags=["health"])


@app.get("/")
async def root():
    """Root endpoint - service information."""
    return {
        "service": "Atrium Observatory",
        "version": __version__,
        "status": "operational",
        "docs": "/docs",
    }
