from __future__ import annotations

from typing import Any


def format_citations(citations_object: dict[str, Any]) -> str:
    """Build a UNSW Harvard citation string from CiteAs metadata."""

    metadata = citations_object.get("metadata") or {}
    authors = _format_authors(metadata.get("author") or metadata.get("authors"))
    title = _extract_title(metadata)
    year = _extract_year(metadata)
    publisher = _extract_first_nonempty(
        metadata.get("publisher"),
        metadata.get("publisher-place"),
    )
    url = _extract_first_nonempty(
        metadata.get("url"),
        citations_object.get("url"),
        metadata.get("doi"),
    )

    return f"{authors} ({year}). {title}. {publisher}. Available at: {url}."


def _format_authors(authors: Any) -> str:
    if isinstance(authors, str):
        return authors
    if not authors:
        return "Missing data"
    formatted = []
    for author in authors:
        formatted_name = _format_author(author)
        if formatted_name:
            formatted.append(formatted_name)
    return ", ".join(formatted) if formatted else "Missing data"


def _format_author(author: Any) -> str:
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
            initials = "".join(f"{part[0].upper()}." for part in given.split() if part)
            return f"{family}, {initials}"
        return family or given or "Missing data"
    return "Missing data"


def _extract_year(metadata: dict[str, Any]) -> str:
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
    return "Missing data"


def _extract_first_nonempty(*values: Any) -> str:
    for value in values:
        if value:
            return str(value)
    return "Missing data"


def _extract_title(metadata: dict[str, Any]) -> str:
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
            if candidate and candidate != "Missing data":
                return str(candidate)

    return "Missing data"

