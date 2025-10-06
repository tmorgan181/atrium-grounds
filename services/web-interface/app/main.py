"""
Atrium Grounds - Web Interface

FastAPI application serving as public-facing interface to Observatory API.
Provides cached demos, live analysis proxy, and API documentation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Application metadata
app = FastAPI(
    title="Atrium Grounds - Web Interface",
    description="Public web interface for exploring Observatory conversation analysis",
    version="0.1.0",
    docs_url=None,  # Disable default docs (we'll serve custom docs page)
    redoc_url=None,
)

# CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for public demo site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Import and include routers
from app.routers import pages, examples, proxy  # noqa: E402

app.include_router(pages.router)
app.include_router(examples.router)
app.include_router(proxy.router)


@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    print("Atrium Web Interface starting...")
    print(f"Static files: {static_path}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    print("Atrium Web Interface shutting down...")


# Health check endpoint (basic, will be enhanced in proxy router)
@app.get("/ping")
async def ping():
    """Basic health check for web interface itself."""
    return {"status": "ok", "service": "atrium-web-interface"}
