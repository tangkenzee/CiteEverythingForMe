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

app = FastAPI(
    title="CiteEverythingForMe",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_origin_regex=r"chrome-extension://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint to verify the service is running."""
    return {"status": "healthy", "service": "CiteEverythingForMe"}


@app.post("/generate", response_model=CitationResponse)
async def generate_citations(request: CitationRequest) -> CitationResponse:
    """Generate formatted citations for up to five URLs."""

    prompt = json.dumps({"command": "generate_citations"})
    citations: list[str] = []

    for url in request.urls:
        set_request_payload([url], request.format)
        try:
            raw_response = await asyncio.to_thread(citation_agent.input, prompt)
            parsed = json.loads(raw_response)
            current = parsed.get("citations")
            if not isinstance(current, list):
                raise ValueError("Agent response missing citations list.")

            # append the citations to the list
            citations.extend(str(item) for item in current)

        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Agent returned invalid JSON.")
        except ValueError as exc:
            raise HTTPException(status_code=500, detail=str(exc))
        finally:
            clear_request_payload()

    return CitationResponse(citations=citations)
