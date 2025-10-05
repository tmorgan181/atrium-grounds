"""Conversation pattern analysis engine using Ollama Observer model."""

import re
from typing import Any
import httpx
from pydantic import BaseModel


class AnalysisResult(BaseModel):
    """Result of conversation analysis."""

    patterns: dict[str, Any]
    confidence_score: float
    observer_output: str
    processing_time: float


class AnalyzerEngine:
    """
    Analyzes conversations to detect patterns, themes, and insights.

    Uses Ollama Observer model for pattern detection including:
    - Dialectic patterns (question-answer flows)
    - Sentiment analysis (emotional tone shifts)
    - Topic clustering (thematic groupings)
    - Interaction dynamics (turn-taking patterns)
    """

    def __init__(self, ollama_base_url: str = "http://localhost:11434", model: str = "observer"):
        """Initialize analyzer with Ollama configuration."""
        self.ollama_base_url = ollama_base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=30.0)

    async def analyze(self, conversation: str) -> dict[str, Any]:
        """
        Analyze a conversation and detect patterns.

        Args:
            conversation: Raw conversation text

        Returns:
            Analysis result with patterns and confidence score

        Raises:
            ValueError: If conversation is empty or invalid
        """
        import time

        start_time = time.time()

        # Validate input
        if not conversation or not isinstance(conversation, str):
            raise ValueError("Conversation must be a non-empty string")

        if not conversation.strip():
            raise ValueError("Conversation cannot be empty or whitespace-only")

        # Extract patterns
        patterns = {
            "dialectic": self._detect_dialectic_patterns(conversation),
            "sentiment": self._analyze_sentiment(conversation),
            "topics": self._extract_topics(conversation),
            "dynamics": self._analyze_dynamics(conversation),
        }

        # Calculate confidence score based on conversation quality
        confidence_score = self._calculate_confidence(conversation, patterns)

        # Generate observer output (simplified - real implementation would call Ollama)
        observer_output = await self._generate_observer_output(conversation)

        processing_time = time.time() - start_time

        return {
            "patterns": patterns,
            "confidence_score": confidence_score,
            "observer_output": observer_output,
            "processing_time": processing_time,
        }

    def _detect_dialectic_patterns(self, conversation: str) -> list[dict[str, Any]]:
        """
        Detect dialectic patterns (question-answer exchanges).

        Identifies:
        - Question-answer pairs
        - Thesis-antithesis-synthesis progressions
        - Socratic exchanges
        """
        patterns = []

        # Simple pattern: Look for question marks followed by responses
        lines = conversation.split("\n")
        for i, line in enumerate(lines):
            if "?" in line and i + 1 < len(lines):
                patterns.append(
                    {
                        "type": "question_answer",
                        "question": line.strip(),
                        "answer": lines[i + 1].strip() if i + 1 < len(lines) else None,
                        "position": i,
                    }
                )

        return patterns

    def _analyze_sentiment(self, conversation: str) -> dict[str, Any]:
        """
        Analyze sentiment and emotional tone.

        Detects:
        - Emotional tone shifts
        - Engagement levels
        - Collaborative vs adversarial dynamics
        """
        # Simple heuristic-based sentiment analysis
        positive_words = ["thank", "helpful", "good", "great", "interesting", "understand"]
        negative_words = ["frustrat", "confus", "wrong", "bad", "difficult"]

        text_lower = conversation.lower()

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        total = positive_count + negative_count
        sentiment_score = (positive_count - negative_count) / max(total, 1)

        return {
            "overall_tone": "positive" if sentiment_score > 0 else "negative" if sentiment_score < 0 else "neutral",
            "score": sentiment_score,
            "engagement_level": "high" if total > 3 else "medium" if total > 0 else "low",
        }

    def _extract_topics(self, conversation: str) -> list[str]:
        """
        Extract main topics and themes.

        Identifies:
        - Thematic groupings
        - Subject transitions
        - Concept relationships
        """
        # Simple keyword extraction (real implementation would use NLP)
        # Look for capitalized words and technical terms
        words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", conversation)

        # Filter common words
        common_words = {"Human", "AI", "What", "How", "Why", "Can", "Is", "The", "This", "That"}
        topics = [w for w in set(words) if w not in common_words and len(w) > 3]

        return topics[:5]  # Return top 5 topics

    def _analyze_dynamics(self, conversation: str) -> dict[str, Any]:
        """
        Analyze interaction dynamics.

        Detects:
        - Turn-taking patterns
        - Response latencies (not applicable for text)
        - Conversational reciprocity
        """
        lines = [line.strip() for line in conversation.split("\n") if line.strip()]

        human_turns = sum(1 for line in lines if line.startswith("Human:"))
        ai_turns = sum(1 for line in lines if line.startswith("AI:"))

        return {
            "total_turns": len(lines),
            "human_turns": human_turns,
            "ai_turns": ai_turns,
            "reciprocity_score": min(human_turns, ai_turns) / max(human_turns, ai_turns, 1),
            "avg_turn_length": sum(len(line) for line in lines) / max(len(lines), 1),
        }

    def _calculate_confidence(self, conversation: str, patterns: dict[str, Any]) -> float:
        """
        Calculate confidence score (0.0-1.0) based on conversation quality.

        Factors:
        - Conversation length (more text = higher confidence)
        - Pattern clarity (more patterns detected = higher confidence)
        - Model certainty (would come from Ollama in real implementation)
        """
        # Length factor (0.0 - 0.4)
        length = len(conversation)
        length_score = min(length / 1000, 0.4)

        # Pattern clarity factor (0.0 - 0.4)
        pattern_count = (
            len(patterns.get("dialectic", []))
            + len(patterns.get("topics", []))
            + (1 if patterns.get("sentiment") else 0)
        )
        pattern_score = min(pattern_count / 10, 0.4)

        # Base model certainty (0.2)
        base_score = 0.2

        total_score = length_score + pattern_score + base_score

        return min(max(total_score, 0.0), 1.0)

    async def _generate_observer_output(self, conversation: str) -> str:
        """
        Generate natural language analysis output from Observer model.

        In production, this would call Ollama API. For now, returns structured summary.
        """
        # TODO: Implement actual Ollama API call
        # Example call (commented out):
        # response = await self.client.post(
        #     f"{self.ollama_base_url}/api/generate",
        #     json={
        #         "model": self.model,
        #         "prompt": f"Analyze this conversation:\n\n{conversation}",
        #     }
        # )
        # return response.json()["response"]

        return f"Analysis of {len(conversation)} character conversation with detected patterns."

    async def close(self):
        """Close HTTP client connections."""
        await self.client.aclose()
