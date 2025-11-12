"""ConnectOnion AI agent helper functions."""

import asyncio
from pathlib import Path
from typing import List

from connectonion import Agent
from shared.citation_generator import CitationGenerator

# Resolve prompt path (supports prompt in agent/src/prompt.md or docs/prompt.md)
_PROJECT_ROOT = Path(__file__).parent.parent
_PROMPT_CANDIDATES = [
    Path(__file__).parent / "src" / "prompt.md",
    _PROJECT_ROOT / "docs" / "prompt.md",
]
for candidate in _PROMPT_CANDIDATES:
    if candidate.exists():
        _PROMPT_PATH = candidate
        break
else:  # pragma: no cover - should not happen in normal usage
    raise FileNotFoundError("Prompt file not found. Expected at agent/src/prompt.md or docs/prompt.md")


async def generate_citation_ai_with_urls(
    query: str, urls: List[str], citation_gen: CitationGenerator
) -> str:
    """Use ConnectOnion agent to generate citations via natural language."""
    temp_agent = Agent(
        name="citation_generator",
        system_prompt=_PROMPT_PATH,
        tools=[citation_gen],
        max_iterations=15,
        model="co/gpt-5-nano",
    )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, temp_agent.input, query)
