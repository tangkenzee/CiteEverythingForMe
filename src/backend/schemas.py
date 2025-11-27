from __future__ import annotations

from pydantic import BaseModel


class CitationResponse(BaseModel):
    citations: list[str]


