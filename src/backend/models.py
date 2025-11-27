from __future__ import annotations

from pydantic import BaseModel, HttpUrl, validator

_FORMAT_ALIASES: dict[str, str] = {
    "harvard": "harvard",
    "mla": "mla",
    "unsw harvard": "unsw harvard",
    "unsw": "unsw harvard",
    "unsw_harvard": "unsw harvard",
    "unsw-harvard": "unsw harvard",
    "unswharvard": "unsw harvard",
}


class GenerateRequest(BaseModel):
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
        normalized = _FORMAT_ALIASES.get(value.lower().strip())
        if not normalized:
            raise ValueError("format must be one of: harvard, mla, or unsw harvard.")
        return normalized

