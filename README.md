# CiteEverythingForMe

AI-assisted academic citation generation for the web. A Manifest V3 Chrome extension captures pages you are viewing and a FastAPI backend formats citations across UNSW Harvard, Harvard, APA, MLA, Chicago, IEEE, and Vancouver styles. Download a single `citations.txt` file in one click.

## Key features

- Manifest V3 extension that collects URLs from the active browser tab
- Bulk citation generation via `POST /api/citations/generate`
- Optional ConnectOnion AI mode for natural-language citation requests
- Robust author extraction (meta tags, JSON-LD, bylines, domain fallback)
- Plain-text download (`citations_style_count.txt`) ready for copy/paste

## Prerequisites

- Python 3.9+
- Google Chrome (or Chromium-based browser)
- Git

## Install and set up the backend service

```bash
# Clone the repository
git clone <repository-url>
cd CiteEverythingForMe

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate

# Install dependencies (fastapi, uvicorn, connectonion, etc.)
pip install -r requirements.txt

# (Optional) install dev extras (pytest, linting)
pip install -e ".[dev]"
```

## Start the backend

```bash
uvicorn agent.main:app --reload
```

- API root: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

> **CORS**: During development we allow all origins (`*`). Before distributing the extension, update `allow_origins` in `agent/main.py` to the exact extension ID (e.g., `"chrome-extension://<extension-id>"`).

## Install the Chrome extension

1. Open `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked** and choose the `extension/` directory
4. (Optional) Pin the CiteEverythingForMe icon for quicker access

## Use the extension

1. Browse to any page you want to cite
2. Click the extension icon to open the popup
3. Verify captured URLs (clear or keep accumulating)
4. Choose citation style and toggle **Use AI** if desired
5. Click **Generate Citations** to download `citations.txt`

### Use the REST API directly

```bash
curl -X POST "http://localhost:8000/api/citations/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example.com", "https://example.org"],
    "style": "unsw",
    "use_ai": false
  }' \
  --output citations.txt
```

- `use_ai: true` routes the request through the ConnectOnion agent (no extra `query` field needed)
- `GET /api/citations/styles` returns the supported styles list

## Project layout

```
shared/            # Citation engine shared by backend & extension
agent/            # FastAPI app (main.py), ConnectOnion integration (agent_setup.py), request models (models.py), tools/
extension/         # Manifest V3 browser extension
docs/              # Prompt, UNSW notes, usage instructions
tests/             # Unit tests covering the shared citation engine
```

## Documentation

- Extension install & behavior: `extension/README.md`
- Usage guide: `docs/USAGE_GUIDE.md`
- UNSW Harvard referencing notes: `docs/UNSW_Harvard_referencing.md`
- ConnectOnion prompt: `docs/prompt.md`

## Troubleshooting

- **"Error generating citations"**: Ensure `uvicorn agent.main:app --reload` is running and accessible.
- **CORS errors**: Adjust `allow_origins` in `agent/main.py` to match your extension ID.
- **Missing URLs in popup**: Only tabs opened/visited after loading the extension are captured; use the popup’s **Clear URLs** button before starting a new batch.
- **AI mode behaves unexpectedly**: Verify the backend log output—exceptions are returned inline in the generated text file.

## Testing

```bash
pip install -e ".[dev]"
pytest
```

Tests currently verify the shared citation engine. Extend with FastAPI client tests as needed.

## Contributing & license

Contributions are welcome—feel free to open issues or pull requests. Licensed under the MIT License (`LICENSE`).

