from __future__ import annotations

from typing import Sequence, Any

_current_payload: dict[str, Any] | None = None


def set_request_payload(urls: Sequence[str], citation_format: str) -> None:
    """Save the current citation request so tools can consume it."""
    global _current_payload
    _current_payload = {
        "urls": [str(entry) for entry in urls],
        "format": citation_format,
    }


def clear_request_payload() -> None:
    """Drop the cached request once the agent has finished."""
    global _current_payload
    _current_payload = None


def fetch_request_payload() -> dict[str, Any]:
    """Tool available to the agent for retrieving the pending request."""
    if not _current_payload:
        raise RuntimeError("No request payload is loaded.")
    return {
        "urls": list(_current_payload["urls"]),
        "format": _current_payload["format"],
    }

