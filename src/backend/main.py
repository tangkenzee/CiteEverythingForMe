from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import CitationRequest, CitationResponse

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.agent.my_agent.app import citation_agent  # noqa: E402
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


@app.post("/generate", response_model=CitationResponse)
async def generate_citations(request: CitationRequest) -> CitationResponse:
    """Generate formatted citations for up to five URLs."""
    
    set_request_payload(request.urls, request.format)
    prompt = json.dumps({"command": "generate_citations"})

    try:
        raw_response = await asyncio.to_thread(citation_agent.input, prompt)
        parsed = json.loads(raw_response)
        citations = parsed.get("citations")

        if not isinstance(citations, list):
            raise ValueError("Citations field missing or malformed.")

        citations = [str(item) for item in citations]

    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Agent returned invalid JSON.")
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        clear_request_payload()

    return CitationResponse(citations=citations)

