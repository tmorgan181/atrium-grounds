"""
HTML page routes.

Serves landing page, demo interface, and API documentation.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.config import settings

router = APIRouter()

# Templates directory
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """
    Landing page - Explains Atrium Grounds value proposition.

    No technical jargon (Constitution I compliance).
    """
    return templates.TemplateResponse("index.html", {
        "request": request,
    })


@router.get("/demo", response_class=HTMLResponse)
async def demo_page(request: Request):
    """
    Demo interface page.

    Shows cached examples and provides interface for live analysis.
    """
    # List available examples (static for now, could be dynamic)
    examples = [
        {
            "id": "dialectic-simple",
            "title": "Truth and Perception",
            "description": "Two perspectives on objective vs. subjective truth",
            "type": "dialectic"
        },
        {
            "id": "dialectic-complex",
            "title": "Free Will Paradox",
            "description": "Determinism vs. agency in decision-making",
            "type": "dialectic"
        },
        {
            "id": "collaborative-simple",
            "title": "Building on Ideas",
            "description": "Co-creating a solution through mutual contribution",
            "type": "collaborative"
        },
        {
            "id": "collaborative-complex",
            "title": "System Architecture Design",
            "description": "Collaborative technical design with building consensus",
            "type": "collaborative"
        },
        {
            "id": "debate-simple",
            "title": "Privacy vs. Security",
            "description": "Competing values in technology policy",
            "type": "debate"
        },
        {
            "id": "debate-complex",
            "title": "AI Regulation Approaches",
            "description": "Competing regulatory frameworks for AI development",
            "type": "debate"
        },
        {
            "id": "exploration-simple",
            "title": "Understanding Consciousness",
            "description": "Open-ended inquiry into the nature of awareness",
            "type": "exploration"
        },
        {
            "id": "exploration-complex",
            "title": "The Nature of Mathematical Truth",
            "description": "Philosophical inquiry into mathematical foundations",
            "type": "exploration"
        },
    ]

    return templates.TemplateResponse("demo.html", {
        "request": request,
        "examples": examples,
    })


@router.get("/docs", response_class=HTMLResponse)
async def docs_page(request: Request):
    """
    API documentation page.

    Technical terminology allowed here (developer-facing content).
    """
    return templates.TemplateResponse("docs.html", {
        "request": request,
        "observatory_url": settings.observatory_url,
    })
