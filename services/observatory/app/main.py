"""FastAPI application entrypoint for Observatory service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.models.database import init_database, start_cleanup_scheduler, stop_cleanup_scheduler
from app.api.v1 import analyze, health, batch, examples
from app.middleware import AuthMiddleware, RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    # Startup: Initialize database and start TTL cleanup scheduler
    await init_database()
    start_cleanup_scheduler()
    yield
    # Shutdown: Stop scheduler
    stop_cleanup_scheduler()


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
