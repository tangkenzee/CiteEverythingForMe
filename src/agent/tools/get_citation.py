from __future__ import annotations

from urllib.parse import quote

import httpx


def fetch_cites(url: str) -> dict:
    """Retrieve the CiteAs payload for a single URL.

    Args:
        url: The resource to fetch from CiteAs (DOI, URL, keyword).

    Returns:
        Parsed JSON response from CiteAs containing citations/metadata.
    """

    endpoint = f"https://api.citeas.org/product/{quote(url, safe=':/')}"

    # ADD your email here
    params = {"email": "test@example.com"}
    try:
        response = httpx.get(endpoint, params=params, timeout=3.0)
        response.raise_for_status()

        return response.json()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"CiteAs rejected {url}: {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        raise RuntimeError(f"Unable to reach CiteAs for {url}: {exc}") from exc
