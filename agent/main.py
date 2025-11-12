"""FastAPI application entry point for CiteEverythingForMe."""

import io
from typing import Dict, List

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agent.agent_setup import generate_citation_ai_with_urls
from agent.models import CitationRequest
from shared.citation_generator import CitationGenerator

app = FastAPI(title="CiteEverythingForMe API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; use ["chrome-extension://<id>"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api/citations", tags=["citations"])


def _remove_html_tags(text: str) -> str:
    """Strip HTML tags and entities from citation strings."""
    import re

    cleaned_text = re.sub(r"<[^>]+>", "", text)
    return (
        cleaned_text.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .strip()
    )


def _build_text_file_contents(citations: List[Dict[str, str]], style: str) -> str:
    """Convert citation dictionaries into a downloadable text payload."""
    lines = [
        "Citations Output",
        "=" * 60,
        f"Style: {style.upper()}",
        f"Total Citations: {len(citations)}",
        "",
        "",
    ]

    for index, citation in enumerate(citations, start=1):
        lines.append(f"Source {index}: {citation['url']}")
        lines.append(f"In-text citation: {citation['intext']}")
        lines.append(f"Reference list entry: {citation['reference']}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("")

    return "\n".join(lines)


def _extract_citation_entry(
    generator: CitationGenerator, url: str, style_lower: str, requested_style: str
) -> Dict[str, str]:
    """Extract a formatted citation entry from the generator state."""
    if url in generator.citations and style_lower in generator.citations[url]:
        citation_data = generator.citations[url][style_lower]
        return {
            "url": url,
            "intext": _remove_html_tags(citation_data["intext"]),
            "reference": _remove_html_tags(citation_data["reference"]),
        }

    return {
        "url": url,
        "intext": "(Citation generation failed)",
        "reference": (
            f"Error: Could not generate {requested_style} citation for {url}. "
            "The citation engine returned no result."
        ),
    }


def _record_generation_error(url: str, error: Exception) -> Dict[str, str]:
    """Create an entry describing a generation failure for a specific URL."""
    return {
        "url": url,
        "intext": f"(Error: {error})",
        "reference": f"Error generating citation for {url}: {error}",
    }


async def _generate_with_ai(
    url: str, style: str, generator: CitationGenerator
) -> None:
    """Generate a citation via the ConnectOnion agent for a single URL."""
    query = f"Generate a {style.upper()} citation for: {url}"
    await generate_citation_ai_with_urls(query, [url], generator)


@router.post("/generate")
async def download_citations_text_file(req: CitationRequest):
    """Generate citations for provided URLs and return them as a text file."""
    generator = CitationGenerator()
    compiled_citations: List[Dict[str, str]] = []
    style_lower = (req.style or "unsw").lower()

    for url in req.urls:
        url_str = str(url)

        if req.use_ai:
            try:
                await _generate_with_ai(url_str, req.style, generator)
            except Exception as exc:  # noqa: BLE001 - continue processing others
                compiled_citations.append(_record_generation_error(url_str, exc))
                continue
        else:
            generator.generate_citation(url_str, style=req.style)

        compiled_citations.append(
            _extract_citation_entry(generator, url_str, style_lower, req.style)
        )

    text_payload = _build_text_file_contents(compiled_citations, style_lower)
    file_like = io.BytesIO(text_payload.encode("utf-8"))

    return StreamingResponse(
        file_like,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="citations_{style_lower}_{len(compiled_citations)}.txt"'
        },
    )


@router.get("/styles")
async def list_supported_styles() -> List[str]:
    """Return all supported citation styles."""
    return ["harvard", "unsw", "mla", "chicago", "apa", "ieee", "vancouver"]


app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "CiteEverythingForMe API",
        "version": "1.0.0",
        "description": "AI-powered academic citation generator",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "generate_citations": "POST /api/citations/generate (returns .txt file)",
            "list_styles": "GET /api/citations/styles",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

