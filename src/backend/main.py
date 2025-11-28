"""FastAPI backend server for CiteEverythingForMe.

This module provides the REST API endpoints for the citation generation service.
It receives requests from the Chrome extension, orchestrates the citation agent
to process URLs, and returns formatted citations in the requested style.

Workflow:
    1. Frontend sends POST /generate with URLs and citation format
    2. Backend validates request and loops through each URL
    3. For each URL, sets request payload and invokes the citation agent
    4. Agent uses tools to fetch metadata, get citations, and format them
    5. Backend aggregates all citations and returns them to the frontend
"""

from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import CitationRequest, CitationResponse
from src.agent.my_agent.app import citation_agent
from src.agent.tools.request_payload import (
    clear_request_payload,
    set_request_payload,
)

# Initialize FastAPI application
app = FastAPI(
    title="CiteEverythingForMe",
    version="0.1.0",
)

# Configure CORS to allow requests from:
# - Local development servers (localhost:8000, 127.0.0.1:8000)
# - Chrome extensions (any chrome-extension:// origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_origin_regex=r"chrome-extension://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint to verify the service is running."""
    return {"status": "healthy", "service": "CiteEverythingForMe"}


@app.post("/generate", response_model=CitationResponse)
async def generate_citations(request: CitationRequest) -> CitationResponse:
    """Generate formatted citations for up to five URLs.
    
    This is the main endpoint that processes citation requests. It:
    1. Validates the request (URLs and format are checked by Pydantic)
    2. Processes each URL sequentially through the citation agent
    3. Aggregates all formatted citations into a single response
    
    The agent workflow for each URL:
    - Fetches metadata from CiteAs API or web scraping
    - Formats citations according to the requested style (Harvard, MLA, or UNSW)
    - Returns the formatted citation string
    
    Args:
        request: CitationRequest containing:
            - urls: List of 1-5 URLs to cite (validated HttpUrl objects)
            - format: Citation format string ("harvard", "mla", or "unsw")
    
    Returns:
        CitationResponse containing a list of formatted citation strings.
        The list length equals the number of URLs processed.
    
    Raises:
        HTTPException: 
            - 500 if the agent encounters an error
            - 500 if the agent returns invalid JSON
            - 500 if the agent response is malformed
    
    Example:
        >>> POST /generate
        {
            "urls": ["https://example.com/article"],
            "format": "harvard"
        }

        response:
        {
            "citations": ["Author, A. (2024) 'Title', Site, accessed 5 February 2025, <https://example.com/article>."]
        }
    """
    # Command prompt for the citation agent
    prompt = json.dumps({"command": "generate_citations"})
    citations: list[str] = []

    # Process each URL sequentially
    for url in request.urls:
        # Set the request payload so agent tools can access it
        set_request_payload([url], request.format)
        
        try:
            # Run the agent in a thread pool to avoid blocking, other endpoints can still be accessed while the agent is running
            # The agent will use its tools to fetch and format citations
            raw_response = await asyncio.to_thread(citation_agent.input, prompt)
            
            # Parse the agent's JSON response
            parsed = json.loads(raw_response)
            current = parsed.get("citations")
            
            # Validate that citations is a list
            if not isinstance(current, list):
                raise ValueError("Agent response missing citations list.")

            citations.extend(str(item) for item in current)

        except RuntimeError as exc:
            # Agent execution errors (e.g., tool failures, API errors)
            raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc
        except json.JSONDecodeError:
            # Agent returned invalid JSON
            raise HTTPException(status_code=500, detail="Agent returned invalid JSON.")
        except ValueError as exc:
            # Agent response validation errors
            raise HTTPException(status_code=500, detail=str(exc))
        finally:
            # Always clear the request payload after processing each URL
            # This prevents data leakage between requests
            clear_request_payload()

    return CitationResponse(citations=citations)
