from __future__ import annotations

from pathlib import Path

from connectonion import Agent, load_dotenv

from src.agent.tools.request_payload import fetch_request_payload
from src.agent.tools.scrape_metadata import get_metadata
from src.agent.tools.format_citations import format_UNSW
from src.agent.tools.get_citation import fetch_cites

load_dotenv()

_PROMPT_PATH = Path(__file__).resolve().parent / "agent_prompt.md"

# connectonion best practice
tools = [
    fetch_request_payload,
    fetch_cites,
    format_UNSW,
    get_metadata,
]

# spin up an instance of the agent
citation_agent = Agent(
    name="cite_everything_for_me",
    tools=tools,
    system_prompt=str(_PROMPT_PATH),
    max_iterations=10,
    model="co/gpt-4o-mini",
)
