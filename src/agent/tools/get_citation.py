"""Tool for fetching citations from the CiteAs API.

This module provides a function that queries the CiteAs API to retrieve
citation metadata, formatted citations, and export formats for a given URL

"""

from __future__ import annotations

from urllib.parse import quote

import httpx


def fetch_cites(url: str) -> dict:
    """Retrieve citation data from CiteAs API for a single resource.

    This tool is used by the citation agent to fetch pre-formatted citations
    and metadata from the CiteAs service.

    The response includes:
    - Multiple citation formats (APA, MLA, Chicago, etc.)
    - Metadata (authors, title, publication date, etc.)

    Args:
        url: (e.g., "https://example.com/article")

    Returns:
        Dictionary containing the CiteAs API response with structure:
        {
            "citations": [...],      # List of citation objects
            "exports": [...],         # List of export formats
            "metadata": {...},        # Resource metadata
            "name": "...",           # Resource name
            "url": "...",            # Canonical URL
            "provenance": [...]      # Data source information
        }

    Raises:
        RuntimeError:
            - If CiteAs API returns an error status code
            - If the request fails due to network issues

    Note:
        The email parameter is required by CiteAs for usage tracking.
        Update the email in the params dictionary to your own email address.

    Example:
        >>> fetch_cites("https://example.com/article")
        {
            "citations": [{"citation": "...", "style_fullname": "..."}],
            "metadata": {"title": "...", "author": [...]},
            ...
        }
    """
    # Construct CiteAs API endpoint with URL-encoded resource identifier
    endpoint = f"https://api.citeas.org/product/{quote(url, safe=':/')}"

    # CiteAs requires an email parameter for usage tracking
    # TODO: Replace with your actual email address
    params = {"email": "test@example.com"}

    try:
        # Make GET request to CiteAs API
        response = httpx.get(endpoint, params=params, timeout=3.0)
        response.raise_for_status()

        return response.json()

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"CiteAs rejected {url}: {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        raise RuntimeError(f"Unable to reach CiteAs for {url}: {exc}") from exc
