from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx
import trafilatura


def scrape_metadata(url: str) -> dict[str, Any]:
    """Fetch a page and return metadata suitable for UNSW citations.

    Args:
        url: The target URL to scrape for author/title/publish info.

    Returns:
        Dictionary containing a metadata object that mimics CiteAs response shape.
    """

    try:
        response = httpx.get(url, timeout=15.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.RequestError as exc:
        raise RuntimeError(f"Unable to reach {url}: {exc}") from exc
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"Citation page rejected {url}: {exc.response.status_code}") from exc

    content = trafilatura.extract_metadata(response.text)
    if not content:
        downloaded = trafilatura.fetch_url(url)
        content = trafilatura.extract_metadata(downloaded or response.text) or {}

    content = _normalize_trafilatura_metadata(content)

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
    """Convert trafilatura’s metadata output into a dict.

    Args:
        content: Either a dict or trafilatura Document object.

    Returns:
        A plain dictionary with metadata keys.
    """
    if isinstance(content, dict):
        return content
    metadata = {}
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

