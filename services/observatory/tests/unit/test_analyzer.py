"""Unit tests for the analyzer engine."""

import pytest
from app.core.analyzer import AnalyzerEngine


@pytest.fixture
async def analyzer():
    """Create analyzer engine instance."""
    return AnalyzerEngine()


@pytest.mark.asyncio
async def test_analyzer_initialization(analyzer):
    """Test that analyzer initializes correctly."""
    assert analyzer is not None
    assert hasattr(analyzer, "analyze")


@pytest.mark.asyncio
async def test_analyze_conversation():
    """Test basic conversation analysis."""
    analyzer = AnalyzerEngine()

    conversation = """
    Human: What is the meaning of life?
    AI: The meaning of life is a philosophical question that has been debated for millennia.
    Human: Can you be more specific?
    AI: From a practical perspective, meaning often comes from relationships, growth, and contribution.
    """

    result = await analyzer.analyze(conversation)

    assert result is not None
    assert "patterns" in result
    assert "confidence_score" in result
    assert 0.0 <= result["confidence_score"] <= 1.0


@pytest.mark.asyncio
async def test_analyze_dialectic_patterns():
    """Test detection of dialectic patterns (question-answer flows)."""
    analyzer = AnalyzerEngine()

    conversation = """
    Human: What is consciousness?
    AI: Consciousness is the state of being aware of one's surroundings and thoughts.
    Human: Is AI conscious?
    AI: Current AI systems lack the subjective experience that characterizes consciousness.
    """

    result = await analyzer.analyze(conversation)

    assert "patterns" in result
    assert "dialectic" in result["patterns"]
    assert len(result["patterns"]["dialectic"]) > 0


@pytest.mark.asyncio
async def test_analyze_sentiment():
    """Test sentiment analysis detection."""
    analyzer = AnalyzerEngine()

    conversation = """
    Human: I'm really frustrated with this problem.
    AI: I understand your frustration. Let's work through it step by step.
    Human: Thank you, that's helpful!
    AI: I'm glad I could help. Feel free to ask more questions.
    """

    result = await analyzer.analyze(conversation)

    assert "patterns" in result
    assert "sentiment" in result["patterns"]
    assert result["patterns"]["sentiment"] is not None


@pytest.mark.asyncio
async def test_analyze_topics():
    """Test topic clustering detection."""
    analyzer = AnalyzerEngine()

    conversation = """
    Human: Let's discuss quantum computing.
    AI: Quantum computing uses quantum mechanics principles for computation.
    Human: How does it differ from classical computing?
    AI: It uses qubits instead of bits, enabling superposition and entanglement.
    """

    result = await analyzer.analyze(conversation)

    assert "patterns" in result
    assert "topics" in result["patterns"]
    assert len(result["patterns"]["topics"]) > 0


@pytest.mark.asyncio
async def test_analyze_interaction_dynamics():
    """Test interaction dynamics detection."""
    analyzer = AnalyzerEngine()

    conversation = """
    Human: Question one?
    AI: Answer one.
    Human: Follow-up question?
    AI: Detailed response with examples.
    Human: Very interesting!
    AI: Thank you for engaging.
    """

    result = await analyzer.analyze(conversation)

    assert "patterns" in result
    assert "dynamics" in result["patterns"]
    assert result["patterns"]["dynamics"] is not None


@pytest.mark.asyncio
async def test_confidence_scoring():
    """Test confidence score calculation based on conversation quality."""
    analyzer = AnalyzerEngine()

    # Short conversation should have lower confidence
    short_conversation = "Human: Hi\nAI: Hello"
    short_result = await analyzer.analyze(short_conversation)

    # Long conversation should have higher confidence
    long_conversation = """
    Human: Let's explore the concept of emergence.
    AI: Emergence refers to complex patterns arising from simple interactions.
    Human: Can you give examples?
    AI: Ant colonies, consciousness, and weather systems are examples.
    Human: How does this relate to AI?
    AI: AI systems exhibit emergent behaviors not explicitly programmed.
    """
    long_result = await analyzer.analyze(long_conversation)

    assert short_result["confidence_score"] < long_result["confidence_score"]


@pytest.mark.asyncio
async def test_analyze_empty_conversation():
    """Test handling of empty conversation."""
    analyzer = AnalyzerEngine()

    with pytest.raises(ValueError, match="empty|invalid"):
        await analyzer.analyze("")


@pytest.mark.asyncio
async def test_analyze_malformed_conversation():
    """Test handling of malformed conversation data."""
    analyzer = AnalyzerEngine()

    # Test with non-string input
    with pytest.raises((ValueError, TypeError)):
        await analyzer.analyze(None)

    with pytest.raises((ValueError, TypeError)):
        await analyzer.analyze(123)
