"""Pydantic schemas for API request/response validation.

This module defines the data models used by the FastAPI endpoints.
Pydantic automatically validates incoming requests and ensures type safety.
"""

from __future__ import annotations

from pydantic import BaseModel, HttpUrl, validator

# Supported citation formats
_ALLOWED_FORMATS = {"harvard", "mla", "unsw"}


class CitationRequest(BaseModel):
    """Request schema for citation generation endpoint.

    Validates that:
    - At least 1 URL is provided
    - Maximum of 5 URLs per request
    - Format is one of the allowed values (case-insensitive)
    - URLs are valid HTTP/HTTPS URLs

    Attributes:
        urls: List of 1-5 valid HTTP/HTTPS URLs to generate citations
            for.
        format: Citation style format. Must be one of: "harvard", "mla",
            "unsw". Case-insensitive (will be normalized to lowercase).

    Example:
        {
            "urls": ["https://example.com/article"],
            "format": "Harvard"
        }
    """

    urls: list[HttpUrl]
    format: str

    @validator("urls")
    def max_url_limit(cls, urls: list[HttpUrl]) -> list[HttpUrl]:
        """Validate URL count is between 1 and 5."""
        if not urls:
            raise ValueError("At least one URL must be provided.")
        if len(urls) > 5:
            raise ValueError("A maximum of 5 URLs is allowed per request.")
        return urls

    @validator("format", pre=True)
    def normalize_format(cls, value: str) -> str:
        """Normalize and validate citation format string."""
        cleaned = value.lower().strip()
        if cleaned not in _ALLOWED_FORMATS:
            allowed = ", ".join(sorted(_ALLOWED_FORMATS))
            raise ValueError(f"format must be one of: {allowed}.")
        return cleaned


class CitationResponse(BaseModel):
    """Response schema for citation generation endpoint.

    Example:
        {
            "citations": [
                "Author, A. (2024) 'Title', Site, accessed 5 February 2025, "
                "<https://example.com>."
            ]
        }
    """

    citations: list[str]
