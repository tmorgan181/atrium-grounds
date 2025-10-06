"""
Example generator script.

Generates cached conversation analysis examples by:
1. Loading curated conversations from spec
2. Calling Observatory /analyze for each
3. Saving results to app/static/examples/

Run: uv run python scripts/generate_examples.py
"""
import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.client import ObservatoryClient
from app.config import settings


# Curated conversation examples (from example-conversations.md)
EXAMPLES = [
    {
        "id": "dialectic-simple",
        "title": "Truth and Perception",
        "description": "Two perspectives on objective vs. subjective truth",
        "type": "dialectic",
        "complexity": "simple",
        "conversation": [
            {"speaker": "A", "content": "Truth is objective and exists independently of our perceptions. Mathematical proofs demonstrate this - 2+2=4 regardless of belief."},
            {"speaker": "B", "content": "But our perception shapes what we recognize as truth. Different cultures have different 'truths' about morality and meaning."},
            {"speaker": "A", "content": "Cultural truths are values, not truths. Values vary, but facts remain constant across contexts."},
            {"speaker": "B", "content": "Yet quantum physics shows observation affects reality itself. The observer and observed are inseparable."}
        ]
    },
    {
        "id": "dialectic-complex",
        "title": "Free Will Paradox",
        "description": "Determinism vs. agency in decision-making",
        "type": "dialectic",
        "complexity": "complex",
        "conversation": [
            {"speaker": "A", "content": "If the universe is deterministic, free will is an illusion. Every choice is predetermined by prior causes."},
            {"speaker": "B", "content": "Determinism and free will aren't mutually exclusive. We can be determined to make genuine choices."},
            {"speaker": "A", "content": "That's compatibilism, but it redefines 'free will' to mean something less than true agency."},
            {"speaker": "B", "content": "True agency may be incoherent. What would uncaused choices even mean? Random isn't free."},
            {"speaker": "A", "content": "Perhaps freedom exists in the meta-level - we can reflect on and reshape our decision-making processes."},
            {"speaker": "B", "content": "But that reflection is also determined. We're circles reasoning about our own circumference."}
        ]
    },
    {
        "id": "collaborative-simple",
        "title": "Building on Ideas",
        "description": "Co-creating a solution through mutual contribution",
        "type": "collaborative",
        "complexity": "simple",
        "conversation": [
            {"speaker": "A", "content": "We need a better way to organize these notes. Maybe tags?"},
            {"speaker": "B", "content": "Tags help, but we also need hierarchy. What about nested tags?"},
            {"speaker": "A", "content": "Nested tags could work. We could have 'Project > Phase > Task' structure."},
            {"speaker": "B", "content": "And make tags auto-suggest based on content analysis. Less manual tagging."},
            {"speaker": "A", "content": "Perfect. So: hierarchical tags + AI suggestions + manual override. I'll sketch the UI."}
        ]
    },
    {
        "id": "collaborative-complex",
        "title": "System Architecture Design",
        "description": "Collaborative technical design with building consensus",
        "type": "collaborative",
        "complexity": "complex",
        "conversation": [
            {"speaker": "A", "content": "For the API layer, I'm thinking REST with JSON. Simple and familiar to most developers."},
            {"speaker": "B", "content": "REST works, but have you considered GraphQL? Clients could request exactly the data they need."},
            {"speaker": "A", "content": "GraphQL adds complexity. What if we start with REST and add GraphQL later if needed?"},
            {"speaker": "B", "content": "Good call. Let's optimize for shipping fast. We can always add a GraphQL wrapper on top of REST endpoints."},
            {"speaker": "C", "content": "I like that approach. Should we use OpenAPI specs from the start for documentation?"},
            {"speaker": "A", "content": "Absolutely. OpenAPI gives us docs, client generation, and validation. Worth the initial setup cost."},
            {"speaker": "B", "content": "Agreed. REST + OpenAPI for MVP, GraphQL as future enhancement if user feedback demands it."}
        ]
    },
    {
        "id": "debate-simple",
        "title": "Privacy vs. Security",
        "description": "Competing values in technology policy",
        "type": "debate",
        "complexity": "simple",
        "conversation": [
            {"speaker": "A", "content": "Encryption backdoors are necessary for law enforcement to prevent terrorism and serious crime."},
            {"speaker": "B", "content": "Backdoors compromise everyone's security. Criminals will just use non-backdoored tools anyway."},
            {"speaker": "A", "content": "But without access, we can't investigate serious crimes. Public safety outweighs individual privacy."},
            {"speaker": "B", "content": "History shows governments abuse surveillance powers. Privacy is a fundamental right, not a luxury."}
        ]
    },
    {
        "id": "debate-complex",
        "title": "AI Regulation Approaches",
        "description": "Competing regulatory frameworks for AI development",
        "type": "debate",
        "complexity": "complex",
        "conversation": [
            {"speaker": "A", "content": "We need comprehensive AI regulation now, before the technology becomes too powerful to control."},
            {"speaker": "B", "content": "Premature regulation will stifle innovation. We don't understand AI well enough to regulate it effectively yet."},
            {"speaker": "A", "content": "Waiting for perfect understanding means waiting until it's too late. Look at social media - we waited and now face massive harm."},
            {"speaker": "B", "content": "Social media regulation wouldn't have prevented the problems. Markets and norms adapt faster than laws."},
            {"speaker": "A", "content": "But AI poses existential risks, not just social harms. The precautionary principle demands action."},
            {"speaker": "B", "content": "Existential risk arguments assume capabilities we haven't seen. Let's regulate proven harms, not hypothetical scenarios."},
            {"speaker": "A", "content": "By the time harms are proven, it may be irreversible. We need proactive governance, not reactive cleanup."}
        ]
    },
    {
        "id": "exploration-simple",
        "title": "Understanding Consciousness",
        "description": "Open-ended inquiry into the nature of awareness",
        "type": "exploration",
        "complexity": "simple",
        "conversation": [
            {"speaker": "A", "content": "What makes something conscious? Is it just information processing?"},
            {"speaker": "B", "content": "Computers process information but don't seem conscious. Maybe it's about integration?"},
            {"speaker": "A", "content": "Integrated Information Theory suggests that. But how do we measure integration meaningfully?"},
            {"speaker": "B", "content": "And does integration alone create experience, or just the appearance of it?"},
            {"speaker": "A", "content": "Perhaps consciousness is more fundamental than we think - not created but revealed by certain structures."}
        ]
    },
    {
        "id": "exploration-complex",
        "title": "The Nature of Mathematical Truth",
        "description": "Philosophical inquiry into mathematical foundations",
        "type": "exploration",
        "complexity": "complex",
        "conversation": [
            {"speaker": "A", "content": "Are mathematical truths discovered or invented? Does the number 7 exist independently of minds?"},
            {"speaker": "B", "content": "Platonism says yes, mathematical objects exist in abstract realm. But that realm seems mysterious."},
            {"speaker": "A", "content": "Formalism avoids that - math is just symbol manipulation according to rules. No mystical realm needed."},
            {"speaker": "B", "content": "But formalism can't explain why math describes physical reality so well. There's something more than symbols."},
            {"speaker": "A", "content": "Maybe math is the structure of possibility itself. Not invented, not exactly discovered, but... the grammar of what can be."},
            {"speaker": "B", "content": "That's beautiful. Math as possibility-space rather than objects. It bridges platonism and formalism."},
            {"speaker": "A", "content": "Though it still leaves the hard question: why does one possibility-space manifest as physical reality?"}
        ]
    },
]


async def generate_examples():
    """Generate all cached examples."""
    print("Generating cached conversation examples...")
    print(f"Observatory URL: {settings.observatory_url}")

    # Create output directory
    output_dir = Path(__file__).parent.parent / "app" / "static" / "examples"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Initialize Observatory client
    client = ObservatoryClient()

    generated_count = 0
    failed_count = 0

    for example in EXAMPLES:
        print(f"\nGenerating: {example['id']}")
        print(f"   Type: {example['type']}, Complexity: {example['complexity']}")
        print(f"   Turns: {len(example['conversation'])}")

        try:
            # Call Observatory for analysis
            analysis = await client.analyze(
                conversation=example["conversation"],
                api_key=settings.observatory_api_key  # Optional
            )

            # Build complete example with metadata
            cached_example = {
                "id": example["id"],
                "title": example["title"],
                "description": example["description"],
                "conversation": example["conversation"],
                "analysis": analysis,
                "metadata": {
                    "type": example["type"],
                    "complexity": example["complexity"],
                    "generated_at": datetime.now().isoformat()
                }
            }

            # Save to file
            output_file = output_dir / f"{example['id']}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(cached_example, f, indent=2, ensure_ascii=False)

            print(f"   [OK] Saved to {output_file.name}")
            generated_count += 1

        except Exception as e:
            print(f"   [FAIL] Failed: {str(e)}")
            failed_count += 1

    # Close client
    await client.close()

    # Summary
    print(f"\n{'='*60}")
    print(f"Generation complete:")
    print(f"   Generated: {generated_count}")
    print(f"   Failed: {failed_count}")
    print(f"   Location: {output_dir}")

    if failed_count > 0:
        print(f"\nWARNING: Some examples failed to generate.")
        print(f"   Check that Observatory is running at {settings.observatory_url}")
        print(f"   Run: curl {settings.observatory_url}/health")

    return generated_count


if __name__ == "__main__":
    count = asyncio.run(generate_examples())
    sys.exit(0 if count > 0 else 1)
