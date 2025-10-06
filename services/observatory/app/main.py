"""FastAPI application entrypoint for Observatory service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1 import analyze, batch, examples, health
from app.core.dev_keys import auto_register_dev_keys
from app.middleware import AuthMiddleware, RateLimitMiddleware
from app.models.database import init_database, start_cleanup_scheduler, stop_cleanup_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    # ANSI color codes  # noqa: N806
    cyan = "\033[96m"
    green = "\033[92m"
    yellow = "\033[93m"
    magenta = "\033[95m"
    bold = "\033[1m"
    reset = "\033[0m"

    # Startup banner
    print("\n" + cyan + "=" * 70 + reset)
    print(f"   {bold}{magenta}⚡ ATRIUM OBSERVATORY{reset}")
    print(f"   {cyan}Conversation Analysis Service{reset}")
    print(cyan + "=" * 70 + reset)
    print(f"   {yellow}Version:{reset} {__version__}")
    print(f"   {yellow}API Docs:{reset} http://localhost:8000/docs")
    print(cyan + "=" * 70 + reset + "\n")

    # Startup: Initialize database and start TTL cleanup scheduler
    print(f"{cyan}🔧 Initializing database...{reset}")
    await init_database()
    print(f"{green}✓ Database ready{reset}\n")

    print(f"{cyan}⏰ Starting cleanup scheduler...{reset}")
    start_cleanup_scheduler()
    print(f"{green}✓ TTL cleanup active{reset}\n")

    # Auto-register development API keys if dev-api-keys.txt exists
    dev_keys = auto_register_dev_keys()
    if dev_keys:
        print(f"{yellow}🔑 Development API keys registered:{reset}")
        if "dev_key" in dev_keys:
            print(f"   {green}• API Key tier (60 req/min){reset}")
        if "partner_key" in dev_keys:
            print(f"   {green}• Partner tier (600 req/min){reset}")
        print(f"   {green}✓ Loaded from dev-api-keys.txt{reset}\n")

    print(cyan + "=" * 70 + reset)
    print(f"   {bold}{green}🚀 SERVER READY{reset}")
    print(f"   {yellow}Press CTRL+C to stop{reset}")
    print(cyan + "=" * 70 + reset + "\n")

    yield

    # Shutdown
    print("\n" + yellow + "=" * 70 + reset)
    print(f"   {yellow}⚠ Shutting down...{reset}")
    print(yellow + "=" * 70 + reset + "\n")
    stop_cleanup_scheduler()
    print(f"{green}✓ Cleanup scheduler stopped{reset}")
    print("\n" + cyan + "=" * 70 + reset)
    print(f"   {bold}{magenta}👋 Server stopped{reset}")
    print(cyan + "=" * 70 + reset + "\n")


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
