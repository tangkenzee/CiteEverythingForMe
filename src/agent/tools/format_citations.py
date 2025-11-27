from __future__ import annotations

from ast import literal_eval
from datetime import date
from typing import Any, Mapping
import json


def format_citations(citations_object: dict[str, Any] | str | Mapping[str, Any]) -> str:
    """Build a UNSW Harvard citation string from CiteAs metadata."""
        #  citations_object is a dictionary with the following keys: 
        # - citations: a list of citation objects
        # - metadata: a dictionary with the metadata of the citation
        # - status: the status of the citation
        # - error: the error message if the citation is not found
        # - message: the message of the response
        # - url: the url of the response
        # - format: the format of the response
        # - style: the style of the response

    citations_object = _normalize_citations_object(citations_object)

    metadata = citations_object.get("metadata") or {}
    authors = _format_authors(metadata.get("author") or metadata.get("authors"))
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

    citation = ", ".join(components)
    return f"{citation}." if citation else ""


def _format_authors(authors: Any) -> str:
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
        return family or given or ""
    return ""


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
    return ""


def _extract_first_nonempty(*values: Any) -> str:
    for value in values:
        if value:
            return str(value)
    return ""


def _extract_site_name(metadata: dict[str, Any]) -> str:
    return _extract_first_nonempty(
        metadata.get("site"),
        metadata.get("site_name"),
        metadata.get("site-title"),
        metadata.get("title"),
        metadata.get("name"),
    )


def _format_accessed_date(accessed_date: date) -> str:
    return f"{accessed_date.day} {accessed_date.strftime('%B')} {accessed_date.year}"


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
    if candidate:
        return str(candidate)

    return ""


def _normalize_citations_object(candidate: dict[str, Any] | str | Mapping[str, Any]) -> dict[str, Any]:
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

