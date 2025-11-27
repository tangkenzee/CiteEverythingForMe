from __future__ import annotations

from pathlib import Path

from connectonion import Agent, load_dotenv
load_dotenv();
from src.agent.tools.request_payload import fetch_request_payload
from src.agent.tools.format_citations import format_citations
from src.agent.tools.get_citation import get_citation

_PROMPT_PATH = Path(__file__).resolve().parent / "agent_prompt.md"

tools = [
    fetch_request_payload, 
    get_citation, 
    format_citations
]

citation_agent = Agent(
    name="cite_everything_for_me",
    tools= tools,
    system_prompt=str(_PROMPT_PATH),
    max_iterations=15,
    model="co/gpt-4o-mini",
)

