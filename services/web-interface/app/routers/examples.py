"""
Cached example loader.

Serves pre-generated conversation analysis examples from static JSON files.
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

# Examples directory
EXAMPLES_DIR = Path(__file__).parent.parent / "static" / "examples"


@router.get("/examples/{example_id}")
async def get_example(example_id: str):
    """
    Get cached conversation analysis example.

    Args:
        example_id: Example identifier (alphanumeric + hyphens only)

    Returns:
        JSON with conversation and pre-generated analysis

    Raises:
        HTTPException 400: Invalid example ID format
        HTTPException 404: Example not found
    """
    # Validate ID format (prevent path traversal)
    if not example_id.replace("-", "").isalnum():
        raise HTTPException(
            status_code=400,
            detail="Invalid example ID. Use alphanumeric characters and hyphens only.",
        )

    # Load example file
    example_path = EXAMPLES_DIR / f"{example_id}.json"

    if not example_path.exists():
        raise HTTPException(status_code=404, detail=f"Example '{example_id}' not found")

    try:
        with open(example_path, "r", encoding="utf-8") as f:
            example_data = json.load(f)
        return JSONResponse(content=example_data)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid example data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading example: {str(e)}")
