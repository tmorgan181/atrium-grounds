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
    # ANSI color codes
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    
    # Startup banner
    print("\n" + CYAN + "=" * 70 + RESET)
    print(f"   {BOLD}{MAGENTA}⚡ ATRIUM OBSERVATORY{RESET}")
    print(f"   {CYAN}Conversation Analysis Service{RESET}")
    print(CYAN + "=" * 70 + RESET)
    print(f"   {YELLOW}Version:{RESET} {__version__}")
    print(f"   {YELLOW}API Docs:{RESET} http://localhost:8000/docs")
    print(CYAN + "=" * 70 + RESET + "\n")
    
    # Startup: Initialize database and start TTL cleanup scheduler
    print(f"{CYAN}🔧 Initializing database...{RESET}")
    await init_database()
    print(f"{GREEN}✓ Database ready{RESET}\n")
    
    print(f"{CYAN}⏰ Starting cleanup scheduler...{RESET}")
    start_cleanup_scheduler()
    print(f"{GREEN}✓ TTL cleanup active{RESET}\n")

    # Auto-register development API keys if dev-api-keys.txt exists
    dev_keys = auto_register_dev_keys()
    if dev_keys:
        print(f"{YELLOW}🔑 Development API keys registered:{RESET}")
        if "dev_key" in dev_keys:
            print(f"   {GREEN}• API Key tier (60 req/min){RESET}")
        if "partner_key" in dev_keys:
            print(f"   {GREEN}• Partner tier (600 req/min){RESET}")
        print(f"   {GREEN}✓ Loaded from dev-api-keys.txt{RESET}\n")

    print(CYAN + "=" * 70 + RESET)
    print(f"   {BOLD}{GREEN}🚀 SERVER READY{RESET}")
    print(f"   {YELLOW}Press CTRL+C to stop{RESET}")
    print(CYAN + "=" * 70 + RESET + "\n")

    yield
    
    # Shutdown
    print("\n" + YELLOW + "=" * 70 + RESET)
    print(f"   {YELLOW}⚠ Shutting down...{RESET}")
    print(YELLOW + "=" * 70 + RESET + "\n")
    stop_cleanup_scheduler()
    print(f"{GREEN}✓ Cleanup scheduler stopped{RESET}")
    print("\n" + CYAN + "=" * 70 + RESET)
    print(f"   {BOLD}{MAGENTA}👋 Server stopped{RESET}")
    print(CYAN + "=" * 70 + RESET + "\n")


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
