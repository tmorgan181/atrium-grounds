"""Examples API endpoints for curated conversation samples."""

import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()

# Path to examples directory
EXAMPLES_DIR = Path(__file__).parent.parent.parent.parent / "examples"
MANIFEST_PATH = EXAMPLES_DIR / "manifest.json"


# Response Models
class ExampleMetadata(BaseModel):
    """Metadata for an example conversation."""

    id: str
    name: str
    category: str
    description: str
    tags: list[str]
    expected_patterns: list[str]
    difficulty: str
    participants: int


class ExampleListResponse(BaseModel):
    """Response for listing examples."""

    examples: list[ExampleMetadata]
    categories: list[dict[str, str]]
    total: int


class ExampleDetailResponse(BaseModel):
    """Response for a specific example."""

    id: str
    content: str
    metadata: ExampleMetadata
    analyze_url: str = Field(..., description="URL to analyze this conversation")


def load_manifest() -> dict[str, Any]:
    """Load the examples manifest."""
    try:
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Manifest not found at {MANIFEST_PATH}")
        raise HTTPException(status_code=500, detail="Examples manifest not found")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid manifest JSON: {e}")
        raise HTTPException(status_code=500, detail="Invalid examples manifest")


@router.get("/examples", response_model=ExampleListResponse)
async def list_examples(
    category: str | None = Query(None, description="Filter by category"),
    difficulty: str | None = Query(
        None, description="Filter by difficulty (beginner, intermediate, advanced)"
    ),
    tag: str | None = Query(None, description="Filter by tag"),
):
    """
    Get list of curated example conversations.

    Returns a list of available conversation examples with metadata.
    Examples can be filtered by category, difficulty, or tags.

    **Categories**:
    - dialectic: Thesis-antithesis explorations
    - sentiment: Emotional content and empathy
    - informational: Knowledge transfer
    - synthesis: Collaborative problem-solving

    **Difficulty Levels**:
    - beginner: Simple, short conversations
    - intermediate: Moderate complexity
    - advanced: Complex, multi-layered discussions
    """
    manifest = load_manifest()
    examples = manifest["examples"]
    categories = manifest["categories"]

    # Apply filters
    filtered_examples = examples

    if category:
        filtered_examples = [e for e in filtered_examples if e["category"] == category]

    if difficulty:
        filtered_examples = [e for e in filtered_examples if e["difficulty"] == difficulty]

    if tag:
        filtered_examples = [e for e in filtered_examples if tag in e["tags"]]

    # Convert to Pydantic models
    example_metadata = [ExampleMetadata(**ex) for ex in filtered_examples]

    return ExampleListResponse(
        examples=example_metadata,
        categories=categories,
        total=len(example_metadata),
    )


@router.get("/examples/{example_id}", response_model=ExampleDetailResponse)
async def get_example(example_id: str):
    """
    Get a specific example conversation by ID.

    Returns the full conversation text along with metadata and
    a link to analyze the conversation.

    **Example IDs**:
    - philosophical-inquiry
    - dialectic-exchange
    - technical-assistance
    - emotional-support
    - collaborative-problem-solving
    """
    manifest = load_manifest()
    examples = manifest["examples"]

    # Find the example
    example = next((e for e in examples if e["id"] == example_id), None)

    if not example:
        raise HTTPException(status_code=404, detail=f"Example '{example_id}' not found")

    # Load the conversation content
    example_file = EXAMPLES_DIR / example["file"]

    try:
        with open(example_file, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        logger.error(f"Example file not found: {example_file}")
        raise HTTPException(
            status_code=500,
            detail=f"Example content file not found: {example['file']}",
        )

    # Build analyze URL
    analyze_url = f"/api/v1/analyze?example={example_id}"

    return ExampleDetailResponse(
        id=example["id"],
        content=content,
        metadata=ExampleMetadata(**example),
        analyze_url=analyze_url,
    )
