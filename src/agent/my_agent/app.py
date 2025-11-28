"""Citation agent setup and configuration.

This module initializes the ConnectOnion agent that orchestrates the citation
generation workflow.
"""

from __future__ import annotations

from pathlib import Path

from connectonion import Agent, load_dotenv

from src.agent.tools.request_payload import fetch_request_payload
from src.agent.tools.scrape_metadata import get_metadata
from src.agent.tools.format_citations import format_UNSW
from src.agent.tools.get_citation import fetch_cites

# Load environment variables
load_dotenv()

# Path to the agent's system prompt/instructions
_PROMPT_PATH = Path(__file__).resolve().parent / "agent_prompt.md"

# Function/Tools available to the agent for citation generation

tools = [
    fetch_request_payload,  # Get the URLs and format from the request
    fetch_cites,  # Fetch citations from CiteAs API
    format_UNSW,  # Format citations in UNSW style
    get_metadata,  # Scrape metadata from web pages
]

# Initialize the citation agent
# It reads instructions from agent_prompt.md and can use the tools above
citation_agent = Agent(
    name="cite_everything_for_me",
    tools=tools,
    system_prompt=str(_PROMPT_PATH),
    max_iterations=10,  # Maximum agent reasoning steps
    model="co/gpt-4o-mini",
)
