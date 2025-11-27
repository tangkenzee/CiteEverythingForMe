from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from connectonion import Agent

from src.agent.tools.format_citations import format_citations
from src.agent.tools.get_citation import get_citation

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "agent_prompt.md"

citation_agent = Agent(
    name="cite_everything_for_me",
    tools=[get_citation, format_citations],
    system_prompt=str(_PROMPT_PATH),
    max_iterations=15,
    model="co/gpt-4o-mini",
)

def build_agent_prompt(urls: Sequence[str], citation_format: str) -> str:
    """Create the user prompt that drives the ConnectOnion agent."""
    url_texts = [str(entry) for entry in urls]
    formatted_urls = "\n".join(f"- {entry}" for entry in url_texts)
    payload = {"urls": url_texts, "format": citation_format}

    return (
        "Process the following citation request without deviation. "
        "Call get_citation once per URL (the tool itself pauses for 0.5 seconds). "
        "For formats 'harvard' or 'mla', use the citation string found inside the citations array returned by get_citation. "
        "For 'unsw harvard', build the citation by calling format_citations with the metadata dictionary. "
        "Never invent citation text; only tools may produce the formatted strings. "
        "Work sequentially through the URLs in the order listed below and, once all tools have returned, "
        "sort the formatted citations alphabetically by the first author's first name. "
        "Respond with a single JSON object that has one key named \"citations\" whose value is the ordered array of strings.\n"
        f"Payload:\n{json.dumps(payload, indent=2)}\n"
        f"URL order:\n{formatted_urls}\n"
        f"Requested style: {citation_format}\n"
        "Return only the JSON object; no explanations or annotations."
    )

