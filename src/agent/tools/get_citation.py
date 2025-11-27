from __future__ import annotations

import time
from urllib.parse import quote

import httpx

def get_citation(url: str) -> dict:
    """Retrieve the CiteAs payload for a single URL."""

    endpoint = f"https://api.citeas.org/product/{quote(url, safe=':/')}"

    # ADD your email here
    params = {"email": "test@example.com"}
    try:
        response = httpx.get(endpoint, params=params, timeout=15.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"CiteAs rejected {url}: {exc.response.status_code}") from exc
    except httpx.RequestError as exc:
        raise RuntimeError(f"Unable to reach CiteAs for {url}: {exc}") from exc
    finally:
        # makes sure you stay under the rate limit
        time.sleep(0.5)

