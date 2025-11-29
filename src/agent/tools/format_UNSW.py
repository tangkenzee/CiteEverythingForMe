"""Citation formatting tool for UNSW citation style."""

from __future__ import annotations

from ast import literal_eval
from datetime import date
from typing import Any, Mapping
import json


def format_UNSW(
    citations_object: dict[str, Any] | str | Mapping[str, Any],
    **_: Any,
) -> str:
    """Format a citation in UNSW style from CiteAs metadata or scraped data.

    This function takes citation metadata (from CiteAs API or web scraping)
    and formats it according to UNSW citation guidelines. It handles:
    - Multiple author formats (dict with family/given, or plain strings)
    - Missing fields (gracefully omits unavailable information)
    - Various date formats
    - URL formatting

    The output format is:
    "Author, A. B. 2024, _Site Name_, Publisher, accessed 5 February 2025,
    <https://example.com>."

    Args:
        citations_object: Citation data in one of these formats:
            - Dictionary (CiteAs response or scraped metadata)
            - String representation of a dictionary (JSON or Python literal)
            - Mapping object (dict-like interface)
        **_: Additional keyword arguments (ignored, for tool compatibility).

    Example:
    >>> format_UNSW({
    ...     "metadata": {
    ...         "author": [{"family": "Smith", "given": "John"}],
    ...         "year": 2024,
    ...         "title": "Example Article"
    ...     },
    ...     "url": "https://example.com"
    ... })
    "Smith, J. 2024, _Example Article_, accessed 5 February 2025,
    <https://example.com>."

    Returns:
        Formatted citation string in UNSW style, ending with a period.
        Returns empty string if no usable data is available.
    """

    # Normalize input to a dictionary (handles string, dict, or Mapping)
    citations_object = _normalize_citations_object(citations_object)
    metadata = citations_object.get("metadata") or {}

    # Extract and format all citation components
    authors = _format_authors(
        metadata.get("author") or metadata.get("authors")
    )
    year = _extract_year(metadata)
    site_name = _extract_site_name(metadata)
    sponsor = _extract_first_nonempty(
        metadata.get("publisher"),
        metadata.get("sponsor"),
        metadata.get("publisher-place"),
    )
    url = _extract_first_nonempty(
        metadata.get("url"),
        citations_object.get("url"),
        metadata.get("URL"),
        metadata.get("doi"),
    )
    accessed = _format_accessed_date(date.today())
    author_year = " ".join(part for part in (authors, year) if part).strip()
    site_name_text = f"_{site_name}_" if site_name else ""
    accessed_text = f"accessed {accessed}" if accessed else ""
    url_text = f"<{url}>" if url else ""

    # Collect all non-empty components
    components = [
        component
        for component in (
            author_year,
            site_name_text,
            sponsor,
            accessed_text,
            url_text,
        )
        if component
    ]

    # Join components with commas and add period at end
    citation = ", ".join(components)
    return f"{citation}." if citation else ""


# Helper functions for formatting citations


def _format_authors(authors: Any) -> str:
    """Format the authors list into a comma-separated string.

    Args:
        authors: Either a string or iterable of author descriptors.

    Returns:
        Properly formatted author string or empty string when missing.
    """
    if isinstance(authors, str):
        return authors.strip()
    if not authors:
        return ""
    formatted = []
    for author in authors:
        formatted_name = _format_author(author)
        if formatted_name:
            formatted.append(formatted_name)
    return ", ".join(formatted)


def _format_author(author: Any) -> str:
    """Format a single author entry for the citation.

    Args:
        author: Single author representation (str or dict).

    Returns:
        Formatted author text (family, initials) or empty string
        when unavailable.
    """
    if isinstance(author, str):
        return author
    if isinstance(author, dict):
        family = _extract_first_nonempty(
            author.get("family"),
            author.get("surname"),
            author.get("lastName"),
        )
        given = _extract_first_nonempty(
            author.get("given"),
            author.get("firstName"),
            author.get("given-names"),
        )
        if family and given:
            initials = "".join(
                f"{part[0].upper()}." for part in given.split() if part
            )
            return f"{family}, {initials}"
        return family or given or ""
    return ""


def _extract_year(metadata: dict[str, Any]) -> str:
    """Extract the publication year from CiteAs metadata.

    Args:
        metadata: Metadata dictionary from CiteAs response.

    Returns:
        Year string if found, otherwise empty string.
    """
    year = metadata.get("year")
    if year:
        return str(year)
    issued = metadata.get("issued")
    if isinstance(issued, dict):
        date_parts = issued.get("date-parts")
        if (
            isinstance(date_parts, list)
            and date_parts
            and isinstance(date_parts[0], list)
            and date_parts[0]
        ):
            return str(date_parts[0][0])
    return ""


def _extract_first_nonempty(*values: Any) -> str:
    """Return the first truthy value converted to str.

    Args:
        values: Sequence of values to inspect.

    Returns:
        The first non-empty value as a string, or empty string if none.
    """
    for value in values:
        if value:
            return str(value)
    return ""


def _extract_site_name(metadata: dict[str, Any]) -> str:
    """Extract a site name or fallback from metadata.

    Args:
        metadata: CiteAs metadata object.

    Returns:
        Site name string or empty.
    """
    return _extract_first_nonempty(
        metadata.get("site"),
        metadata.get("site_name"),
        metadata.get("site-title"),
        metadata.get("title"),
        metadata.get("name"),
    )


def _format_accessed_date(accessed_date: date) -> str:
    """Return a human-readable accessed date for citations.

    Args:
        accessed_date: Date when citation was accessed.

    Returns:
        Formatted string like '5 February 2025'.
    """
    day = accessed_date.day
    month = accessed_date.strftime("%B")
    year = accessed_date.year
    return f"{day} {month} {year}"


def _extract_title(metadata: dict[str, Any]) -> str:
    """Extract a title value from metadata with fallbacks.

    Args:
        metadata: CiteAs metadata dictionary.

    Returns:
        Title string or empty.
    """
    title = metadata.get("title")
    if title:
        return str(title)

    titles = metadata.get("titles")
    if isinstance(titles, list):
        for entry in titles:
            candidate = (
                _extract_first_nonempty(entry.get("title"), entry.get("name"))
                if isinstance(entry, dict)
                else entry
            )
    if candidate:
        return str(candidate)

    return ""


def _normalize_citations_object(
    candidate: dict[str, Any] | str | Mapping[str, Any],
) -> dict[str, Any]:
    """Normalize the citations input into a real dict.

    Args:
        candidate: Either dict, mapping, or string representation
        of CiteAs response.

    Returns:
        Parsed dictionary ready for metadata extraction.
    """
    if isinstance(candidate, dict):
        return candidate
    if isinstance(candidate, Mapping):
        return dict(candidate)
    if isinstance(candidate, str):
        for parser in (json.loads, literal_eval):
            try:
                return parser(candidate)
            except (ValueError, SyntaxError):
                continue
        raise ValueError("Unable to parse citations object string.")
    raise ValueError("Unsupported type for citations object.")
