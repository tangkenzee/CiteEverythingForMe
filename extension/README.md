# CiteEverythingForMe Chrome Extension

Manifest V3 extension that captures URLs from the active tab and sends them to the FastAPI backend to generate citations.

## Features

- Captures the current tab URL automatically via `content/content.js`
- Maintains a running list of URLs in the background service worker
- Popup UI to review URLs, choose a citation style, and toggle AI mode
- Calls `POST /api/citations/generate` and downloads the resulting `citations.txt`

## Prerequisites

1. Start the backend server:
   ```bash
   uvicorn agent.main:app --reload
   ```
2. Ensure the backend is reachable at `http://localhost:8000`
3. Update CORS origins in `agent/main.py` before production use

## Installation (Chrome)

1. Open `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked** and select this `extension/` directory
4. Pin the extension for quick access (optional)

## Usage

1. Browse to any page you want to cite
2. Click the CiteEverythingForMe extension icon
3. Review the captured URLs in the popup
4. Select the citation style and optionally enable **Use AI**
5. Click **Generate Citations** to download `citations.txt`
6. Use **Clear URLs** to reset the list

## File Overview

- `manifest.json` – Extension manifest (Manifest V3)
- `content/content.js` – Captures active tab URL and sends it to the background script
- `background/background.js` – Stores URL list and responds to popup requests
- `popup/popup.html` – Popup UI layout
- `popup/popup.js` – Handles user actions and backend integration
- `icons/` – Placeholder icons (provide your own before publishing)

## Notes

- Only tested with the development backend; update `fetch` URL if deploying elsewhere
- Adjust `allow_origins` in the backend before distributing the extension
- The extension relies on the backend for citation generation; it does not work offline

