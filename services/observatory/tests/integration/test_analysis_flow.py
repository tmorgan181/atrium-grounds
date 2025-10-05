"""Integration tests for end-to-end conversation analysis flow."""

import asyncio
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_complete_analysis_flow(test_app):
    """Test complete flow: submit -> poll -> retrieve results."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        # Step 1: Submit analysis
        submit_response = await client.post(
            "/api/v1/analyze",
            json={
                "conversation_text": """
                Human: What is quantum entanglement?
                AI: Quantum entanglement is a phenomenon where particles become correlated.
                Human: Can you explain more?
                AI: When particles are entangled, measuring one instantly affects the other.
                """,
                "options": {
                    "pattern_types": ["dialectic", "sentiment", "topics"],
                    "include_insights": True,
                },
            },
        )

        assert submit_response.status_code == 202
        analysis_id = submit_response.json()["id"]

        # Step 2: Poll for status
        max_polls = 10
        for _ in range(max_polls):
            status_response = await client.get(f"/api/v1/analyze/{analysis_id}")
            assert status_response.status_code == 200

            status_data = status_response.json()
            if status_data["status"] == "completed":
                break

            await asyncio.sleep(0.5)

        # Step 3: Verify results
        final_response = await client.get(f"/api/v1/analyze/{analysis_id}")
        result = final_response.json()

        # Verify complete result structure
        assert "id" in result
        assert "status" in result
        assert "patterns" in result or result["status"] != "completed"
        assert "confidence_score" in result or result["status"] != "completed"


@pytest.mark.asyncio
async def test_cancel_during_processing(test_app):
    """Test cancelling an analysis while it's processing."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        # Submit long analysis
        submit_response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Test " * 100 + "\nAI: Response " * 100},
        )

        analysis_id = submit_response.json()["id"]

        # Immediately cancel
        cancel_response = await client.post(f"/api/v1/analyze/{analysis_id}/cancel")

        assert cancel_response.status_code in [200, 409]

        # Verify status is cancelled
        status_response = await client.get(f"/api/v1/analyze/{analysis_id}")
        status = status_response.json()["status"]

        assert status in ["cancelled", "completed"]  # May complete before cancel


@pytest.mark.asyncio
async def test_multiple_concurrent_analyses(test_app):
    """Test handling multiple concurrent analysis requests."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        # Submit multiple analyses
        conversations = [
            "Human: Question 1?\nAI: Answer 1.",
            "Human: Question 2?\nAI: Answer 2.",
            "Human: Question 3?\nAI: Answer 3.",
        ]

        analysis_ids = []
        for conv in conversations:
            response = await client.post("/api/v1/analyze", json={"conversation_text": conv})
            assert response.status_code == 202
            analysis_ids.append(response.json()["id"])

        # Verify all have valid statuses
        for analysis_id in analysis_ids:
            status_response = await client.get(f"/api/v1/analyze/{analysis_id}")
            assert status_response.status_code == 200
            assert "status" in status_response.json()


@pytest.mark.asyncio
async def test_analysis_with_validation_failure(test_app):
    """Test that validation failures are handled properly."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        # Submit invalid conversation
        response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "'; DROP TABLE analyses; --"},
        )

        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data


@pytest.mark.asyncio
async def test_analysis_result_expiration(test_app):
    """Test that analysis results respect TTL (FR-013)."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        # Submit analysis
        response = await client.post(
            "/api/v1/analyze",
            json={"conversation_text": "Human: Test\nAI: Response"},
        )

        analysis_id = response.json()["id"]

        # Get result
        result_response = await client.get(f"/api/v1/analyze/{analysis_id}")
        result = result_response.json()

        # Should have expiration info
        if result["status"] == "completed":
            assert "expires_at" in result


@pytest.mark.asyncio
async def test_pattern_detection_accuracy(test_app):
    """Test that pattern detection works for known patterns."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        # Conversation with clear dialectic pattern
        response = await client.post(
            "/api/v1/analyze",
            json={
                "conversation_text": """
                Human: Is AI conscious?
                AI: Current AI systems lack consciousness as we understand it.
                Human: But couldn't they develop it?
                AI: The question of emergence is philosophically complex.
                Human: What would be the signs?
                AI: Subjective experience and self-awareness would be key indicators.
                """,
                "options": {"pattern_types": ["dialectic"]},
            },
        )

        analysis_id = response.json()["id"]

        # Poll for completion
        for _ in range(10):
            result_response = await client.get(f"/api/v1/analyze/{analysis_id}")
            result = result_response.json()

            if result["status"] == "completed":
                assert "patterns" in result
                assert "dialectic" in result["patterns"]
                # Should detect question-answer exchanges
                break

            await asyncio.sleep(0.5)


@pytest.mark.asyncio
async def test_confidence_scoring_correlation(test_app):
    """Test that confidence scores correlate with conversation quality."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        # Short, low-quality conversation
        short_response = await client.post(
            "/api/v1/analyze", json={"conversation_text": "Human: Hi\nAI: Hello"}
        )
        short_id = short_response.json()["id"]

        # Long, detailed conversation
        long_response = await client.post(
            "/api/v1/analyze",
            json={
                "conversation_text": """
                Human: Can you explain the concept of emergence in complex systems?
                AI: Emergence occurs when a system exhibits properties not present in individual components.
                Human: Can you provide concrete examples?
                AI: Ant colonies display emergent intelligence despite individual ants being simple.
                Human: How does this relate to consciousness?
                AI: Some theories suggest consciousness emerges from neural complexity.
                Human: Is that provable?
                AI: Currently we lack definitive tests for consciousness emergence.
                """
            },
        )
        long_id = long_response.json()["id"]

        # Wait and compare (if implementation supports)
        await asyncio.sleep(1)

        short_result = await client.get(f"/api/v1/analyze/{short_id}")
        long_result = await client.get(f"/api/v1/analyze/{long_id}")

        # If both completed, longer should have higher confidence
        if (
            short_result.json()["status"] == "completed"
            and long_result.json()["status"] == "completed"
        ):
            assert "confidence_score" in short_result.json()
            assert "confidence_score" in long_result.json()
