"""Unit tests for export functionality (FR-014)."""

import csv
import json
from io import StringIO

import pytest

from app.core.export import ExportFormat, ExportFormatter


@pytest.fixture
def sample_analysis_data():
    """Sample analysis result for testing."""
    return {
        "id": "test-123",
        "status": "completed",
        "conversation_text": "Human: Hello\nAI: Hi there!",
        "patterns": {
            "dialectic": {"present": True, "confidence": 0.8},
            "sentiment": {"overall": "positive", "score": 0.7},
            "topics": ["greeting", "communication"],
            "dynamics": {"turn_count": 2, "balance": 0.5},
        },
        "confidence_score": 0.75,
        "processing_time": 1.23,
        "created_at": "2025-10-04T12:00:00",
        "expires_at": "2025-11-03T12:00:00",
    }


def test_export_to_json(sample_analysis_data):
    """Test exporting analysis to JSON format."""
    formatter = ExportFormatter()
    result = formatter.to_json(sample_analysis_data)

    # Should be valid JSON
    parsed = json.loads(result)

    assert parsed["id"] == "test-123"
    assert parsed["status"] == "completed"
    assert "patterns" in parsed
    assert parsed["confidence_score"] == 0.75


def test_export_to_json_pretty(sample_analysis_data):
    """Test JSON export with pretty printing."""
    formatter = ExportFormatter()
    result = formatter.to_json(sample_analysis_data, pretty=True)

    # Pretty printed should have newlines and indentation
    assert "\n" in result
    assert "  " in result or "\t" in result


def test_export_to_csv(sample_analysis_data):
    """Test exporting analysis to CSV format."""
    formatter = ExportFormatter()
    result = formatter.to_csv(sample_analysis_data)

    # Parse CSV
    reader = csv.DictReader(StringIO(result))
    rows = list(reader)

    assert len(rows) == 1
    row = rows[0]

    assert row["id"] == "test-123"
    assert row["status"] == "completed"
    assert row["confidence_score"] == "0.75"


def test_export_to_csv_patterns_flattened(sample_analysis_data):
    """Test that complex patterns are flattened in CSV."""
    formatter = ExportFormatter()
    result = formatter.to_csv(sample_analysis_data)

    reader = csv.DictReader(StringIO(result))
    row = list(reader)[0]

    # Patterns should be in JSON format or flattened
    assert "patterns" in row or "patterns.dialectic.present" in row


def test_export_to_markdown(sample_analysis_data):
    """Test exporting analysis to Markdown format."""
    formatter = ExportFormatter()
    result = formatter.to_markdown(sample_analysis_data)

    # Should contain Markdown formatting
    assert "#" in result  # Headers
    assert "**" in result or "*" in result  # Bold/italic
    assert "test-123" in result
    assert "0.75" in result


def test_export_to_markdown_structure(sample_analysis_data):
    """Test Markdown export has correct structure."""
    formatter = ExportFormatter()
    result = formatter.to_markdown(sample_analysis_data)

    # Should have sections
    assert "Analysis Results" in result or "# Analysis" in result
    assert "Patterns" in result or "## Patterns" in result
    assert "Confidence" in result


def test_export_format_detection():
    """Test export format detection from string."""
    assert ExportFormatter.detect_format("json") == ExportFormat.JSON
    assert ExportFormatter.detect_format("csv") == ExportFormat.CSV
    assert ExportFormatter.detect_format("markdown") == ExportFormat.MARKDOWN
    assert ExportFormatter.detect_format("md") == ExportFormat.MARKDOWN


def test_export_format_invalid():
    """Test handling of invalid export format."""
    with pytest.raises(ValueError):
        ExportFormatter.detect_format("invalid")


def test_export_empty_patterns():
    """Test exporting when patterns are empty."""
    data = {
        "id": "test-456",
        "status": "pending",
        "patterns": None,
        "confidence_score": None,
    }

    formatter = ExportFormatter()

    # Should not crash
    json_result = formatter.to_json(data)
    csv_result = formatter.to_csv(data)
    md_result = formatter.to_markdown(data)

    assert json_result
    assert csv_result
    assert md_result
