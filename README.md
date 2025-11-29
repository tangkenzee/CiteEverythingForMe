# CiteEverythingForMe

## Problem Statement

Creating properly formatted citations for web sources is a time-consuming and error-prone task that frequently interrupts research and writing workflows. Students, researchers, and writers often need to:

- Manually extract metadata (authors, publication dates, titles) from web pages
- Format citations according to complex style guidelines (Harvard, MLA, UNSW, etc.)
- Copy URLs to external citation tools or websites, disrupting their workflow
- Risk making formatting errors that can result in academic penalties or publication issues

Existing solutions typically require users to leave their browser, navigate to separate citation generators, or manually construct citations—adding friction and increasing the likelihood of mistakes.

**CiteEverythingForMe** solves this problem by providing a seamless, browser-integrated solution that automatically generates properly formatted citations directly from the web pages users are already viewing, without requiring them to leave their current context.

## Overview

CiteEverythingForMe is a Chrome extension paired with a FastAPI backend and a ConnectOnion agent. Users save up to five URLs, choose a citation format (Harvard, MLA, or UNSW), and download a numbered list of properly formatted citations without leaving the browser.

## Highlights

- **Frontend**: `popup.html`, `popup.js`, and `popup.css` collect URLs, make the `/generate` POST, and format the downloaded `.txt` file with numbered entries plus an in-text citation line and reference line per entry.
- **Backend**: FastAPI (`src/backend/main.py`) validates the request, loops through each URL, orchestrates the agent, and aggregates citations before returning them to the extension.
- **Agent & tools**: ConnectOnion agent (`src/agent/my_agent/app.py`) exposes `fetch_request_payload`, `fetch_cites`, `get_metadata`, and `format_UNSW`; read `agent_prompt.md` for the exact workflow.
- **Testing**: dedicated tests per tool plus formatter (`tests/test_format_UNSW.py`, `tests/test_request_payload.py`, `tests/test_get_citation.py`, `tests/test_scrape_metadata.py`) and GitHub Actions run the suite across Python 3.11–3.13 along with linting (`black`, `flake8`, `mypy`).

## Getting started

1. Install dependencies via `pip install -r src/backend/requirements.txt`.
2. Activate `myenv` and run `uvicorn src.backend.main:app --reload`.
3. Load the extension in Chrome (via `src/frontend/manifest.json`) and point it at `http://localhost:8000`.
4. Save URLs in the popup, choose a style, and click “Generate Citations.”

## Testing

```
python -m pytest tests/test_format_UNSW.py \
  tests/test_request_payload.py \
  tests/test_get_citation.py \
  tests/test_scrape_metadata.py
```

## CI

GitHub Actions (`.github/workflows/ci.yml`) installs backend dependencies, runs the tests matrix, and enforces formatting/linting.

