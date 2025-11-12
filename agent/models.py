"""Request model for the citation generation API."""

from typing import List, Literal

from pydantic import BaseModel, HttpUrl, field_validator

CitationStyle = Literal["harvard", "mla", "chicago", "apa", "ieee", "vancouver", "unsw"]


class CitationRequest(BaseModel):
    """Incoming payload for citation generation requests."""

    urls: List[HttpUrl]
    style: CitationStyle = "unsw"  # Default to UNSW style
    use_ai: bool = False

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, value: List[HttpUrl]) -> List[HttpUrl]:
        """Ensure at least one URL is provided and no more than 50."""
        if not value:
            raise ValueError("At least one URL is required")
        if len(value) > 50:
            raise ValueError("Maximum 50 URLs allowed per request")
        return value

