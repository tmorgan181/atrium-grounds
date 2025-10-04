"""FastAPI application entrypoint for Observatory service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.models.database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    # Startup: Initialize database
    await init_database()
    yield
    # Shutdown: cleanup if needed
    pass


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


@app.get("/")
async def root():
    """Root endpoint - service information."""
    return {
        "service": "Atrium Observatory",
        "version": __version__,
        "status": "operational",
        "docs": "/docs",
    }
