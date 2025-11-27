from __future__ import annotations

from pydantic import BaseModel, HttpUrl, validator

_ALLOWED_FORMATS = {"harvard", "mla", "unsw harvard"}


class CitationRequest(BaseModel):
    urls: list[HttpUrl]
    format: str

    @validator("urls")
    def max_url_limit(cls, urls: list[HttpUrl]) -> list[HttpUrl]:
        if not urls:
            raise ValueError("At least one URL must be provided.")
        if len(urls) > 5:
            raise ValueError("A maximum of 5 URLs is allowed per request.")
        return urls

    @validator("format", pre=True)
    def normalize_format(cls, value: str) -> str:
        cleaned = value.lower().strip()
        if cleaned not in _ALLOWED_FORMATS:
            allowed = ", ".join(sorted(_ALLOWED_FORMATS))
            raise ValueError(f"format must be one of: {allowed}.")
        return cleaned


class CitationResponse(BaseModel):
    citations: list[str]


