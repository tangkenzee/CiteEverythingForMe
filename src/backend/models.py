"""Legacy model aliases for backward compatibility.

This module provides type aliases that may be used elsewhere in the codebase.
Currently, GenerateRequest is simply an alias for CitationRequest.
"""

from .schemas import CitationRequest

# Alias for CitationRequest (maintained for backward compatibility)
GenerateRequest = CitationRequest
