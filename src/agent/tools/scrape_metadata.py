"""Tool for scraping metadata from web pages.

This module provides a fallback mechanism when CiteAs API is unavailable or
doesn't have data for a particular URL. It uses trafilatura to extract
metadata (title, authors, publication date) directly from web pages.

The extracted metadata is formatted to match the CiteAs response structure,
so it can be used by the same formatting functions.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx
import trafilatura


def get_metadata(url: str) -> dict[str, Any]:
    """Scrape metadata from a web page for citation generation.

    This tool is used as a fallback when CiteAs API doesn't have data for
    a URL. It fetches the web page and extracts:
    - Title
    - Authors
    - Publication date/year
    - Publisher/source (domain name)
    - URL

    Args:
        url: The URL of the web page to scrape metadata from.

    Returns:
        Dictionary with structure matching CiteAs response:
        {
            "metadata": {
                "title": "Page title",
                "author": ["Author 1", "Author 2"],
                "year": "2024",
                "publisher": "example.com",
                "url": "https://example.com/page",
                "issued": {"date-parts": [[2024]]}
            }
        }

        Returns {"metadata": {}} if scraping fails (network error, etc.).

    Note:
        Uses trafilatura library for robust metadata extraction from HTML.
        Falls back to fetching URL directly if initial extraction fails.
    """

    # Fetch the web page with redirect following enabled
    try:
        response = httpx.get(url, timeout=15.0, follow_redirects=True)
        response.raise_for_status()
    except Exception:  # pragma: no cover - network failures
        return {"metadata": {}}

    # Extract metadata from the HTML content
    # Try extracting from response text first
    content = trafilatura.extract_metadata(response.text)

    # If that fails, try fetching the URL directly with trafilatura
    if not content:
        downloaded = trafilatura.fetch_url(url)
        content = trafilatura.extract_metadata(downloaded or response.text) or {}

    # Normalize trafilatura output to a plain dictionary
    content = _normalize_trafilatura_metadata(content)

    # extract fields from the metadata
    title = content.get("title") or ""

    authors = content.get("authors") or content.get("author")
    if isinstance(authors, str):
        authors = [authors]
    if not isinstance(authors, list):
        authors = []

    published = content.get("date") or content.get("published")
    year = ""
    if published and isinstance(published, str) and len(published) >= 4:
        year = published[:4]

    domain = urlparse(url).netloc or ""

    # Build metadata dictionary matching CiteAs format
    metadata: dict[str, Any] = {
        "title": title,
        "author": authors,
        "publisher": content.get("source") or domain,
        "url": url,
    }

    if year:
        metadata["year"] = year
        metadata["issued"] = {"date-parts": [[int(year)] if year.isdigit() else [year]]}

    return {"metadata": metadata}


def _normalize_trafilatura_metadata(content: Any) -> dict[str, Any]:
    """Convert trafilatura's metadata output into a plain dictionary.

    Trafilatura can return metadata in different formats:
    - Plain dictionary
    - Dictionary with nested "metadata" key
    - Document object with attributes

    This function normalizes all formats into a single plain dictionary.

    Args:
        content: Trafilatura output - can be:
            - A dictionary (plain or with nested "metadata")
            - A Document object with metadata attributes

    Returns:
        Plain dictionary containing all metadata fields.
    """
    if isinstance(content, dict):
        if isinstance(content.get("metadata"), dict):
            metadata = content["metadata"].copy()
            metadata.update(
                {k: v for k, v in content.items() if k != "metadata" and v is not None}
            )
            return metadata
        return content
    metadata: dict[str, Any] = {}
    if hasattr(content, "metadata"):
        metadata.update(getattr(content, "metadata") or {})
    if hasattr(content, "__dict__"):
        metadata.update(
            {
                key: value
                for key, value in vars(content).items()
                if key not in metadata and value
            }
        )
    return metadata
