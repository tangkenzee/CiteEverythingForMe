"""Request payload management for the citation agent.

This module provides a thread-local storage mechanism for passing request
data (URLs and citation format) from the FastAPI backend to the agent's tools.

The workflow:
1. Backend calls set_request_payload() before invoking the agent
2. Agent tools call fetch_request_payload() to get the URLs and format
3. Backend calls clear_request_payload() after processing to prevent data leakage

This pattern is necessary because the agent tools need access to the request
context, but the agent interface doesn't directly pass request parameters.
"""

from __future__ import annotations

from typing import Sequence, Any

# Global storage for the current request payload
# This is set by the backend before agent execution and cleared after
_current_payload: dict[str, Any] | None = None


def set_request_payload(urls: Sequence[str], citation_format: str) -> None:
    """Save the current citation request so agent tools can access it.
    
    Called by the FastAPI backend before invoking the citation agent.
    This stores the URLs and format in a global variable that agent tools
    can retrieve via fetch_request_payload().
    
    Args:
        urls: Sequence of URL strings to process (typically 1 URL at a time).
        citation_format: Citation style format ("harvard", "mla", or "unsw").
    
    Note:
        This function modifies global state. It should be called before
        agent execution and clear_request_payload() should be called after.
    """
    global _current_payload
    _current_payload = {
        "urls": [str(entry) for entry in urls],
        "format": citation_format,
    }


def clear_request_payload() -> None:
    """Clear the cached request payload after agent processing.
    
    Called by the FastAPI backend after the agent has finished processing
    a request. This prevents data from one request leaking into the next.
    
    """
    global _current_payload
    _current_payload = None


def fetch_request_payload() -> dict[str, Any]:
    """Tool function for the agent to retrieve the current request payload.
    
    This is called by the citation agent during its workflow to get:
    - The URLs that need to be processed
    - The citation format requested by the user
    
    Returns:
        Dictionary containing:
        {
            "urls": [list of URL strings],
            "format": "citation format string"
        }
    
    Raises:
        RuntimeError: If no request payload has been set (i.e., set_request_payload
                     was not called before agent execution).
    
    Note:
        This function is exposed as a tool to the agent, allowing it to
        access the request context during citation generation.
    """
    if not _current_payload:
        raise RuntimeError("No request payload is loaded.")
    return {
        "urls": list(_current_payload["urls"]),
        "format": _current_payload["format"],
    }
