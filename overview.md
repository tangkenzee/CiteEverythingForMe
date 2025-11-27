## Overview
The CiteEverythingForMe pipeline pairs a Chrome extension with a FastAPI backend and a ConnectOnion agent. The extension collects URLs and the desired citation style, then POSTs the payload to `/generate`. The backend validates it, loops through each URL, and invokes the agent once per URL. The agent handles CiteAs queries, Trafilatura fallback scraping (for UNSW), formatting, and returns `{"citations": ["..."]}` for each run. Once all citations are collected, the frontend formats and downloads them as a numbered text file.

## Architecture Details

- **Frontend stack**: Chrome popup (`popup.html`, `popup.js`, `popup.css`) plus storage utilities. Sends POST requests to `/generate`, receives the citation list, and downloads the `.txt` file with numbered entries, in-text citations, and reference text.

- **Backend stack**: FastAPI server (`src/backend/main.py`) with `schemas.py` for request validation, `models.py` to alias the request, and a loop that calls `set_request_payload` for every URL before invoking the agent. Aggregates the per-URL `{"citations": [...]}` responses into a single list.

- **Agent stack**: ConnectOnion agent (`src/agent/my_agent/app.py`) guided by `agent_prompt.md`. Tools under `src/agent/tools/` include `request_payload`, `get_citation`, `scrape_metadata`, and `format_citations`, each with dedicated tests.

# Full Architecture (ASCII Diagram)
```
[Chrome Extension / popup]
            |
            v
     HTTP POST /generate
===================================
|           Backend                |
===================================
            |
      [FastAPI backend]
        - Validate payload
        - Loop over each URL and call
          set_request_payload([url], format)
            |
            v
      [ConnectOnion Agent]
===================================
|             Agent                |
===================================
        - fetch_request_payload
        - get_citation -> CiteAs API
            |
      if format == harvard/mla: take citation entry
      if format == unsw:
        -> scrape_metadata (Trafilatura fallback)
        -> merge scraped fields into metadata
        -> format_citations(metadata)
            |
            v
        return {"citations": ["..."]}
===================================
|         Backend (continued)       |
===================================
            |
      collect citation string
      aggregated list per request
            |
        Final response -> frontend download
            |
===================================
|         Extension UI              |
===================================
       [popup.js] formats numbered sections with
               In-text and Reference blocks
```

## Typical Workflow

1. The extension gathers the URLs/format and posts them to `/generate`.
2. FastAPI validates the request and iterates through each URL, setting `request_payload` for that single link before running the agent.
3. The agent calls CiteAs, immediately runs `scrape_metadata` when the format is UNSW, merges the metadata fields, formats the citation, and returns `{"citations": ["..."]}`.
4. FastAPI collects each citation string into an array and, once all URLs are processed, returns the full list to the extension.
5. The extension formats the download file with numbered entries, in-text citations, and reference blocks.


# Notes
- **Workflow order matters**: the agent sees one URL per invocation, fetches CiteAs, optionally scrapes metadata, formats UNSW citations, and immediately returns JSON.

- **Testing**: `tests/test_format_citations.py`, `tests/test_request_payload.py`, `tests/test_get_citation.py`, and `tests/test_scrape_metadata.py` cover the formatter plus individual tools; run them with `python -m pytest tests/…`.

- **Formatting rules**: UNSW uses `scrape_metadata` results (Trafilatura wins) before running `format_citations`; Harvard/MLA rely solely on CiteAs’s `citations` array. The download helper extracts `(Author, Year)` or at least a year for the in-text citation line.

- **CI**: GitHub Actions (`.github/workflows/ci.yml`) installs backend dependencies, runs the four tests across Python 3.11–3.13, and performs `black`/`flake8`/`mypy`.

