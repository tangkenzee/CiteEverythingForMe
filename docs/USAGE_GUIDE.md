## Quick Start

### 1. Start the Backend

```bash
cd CiteEverythingForMe
uvicorn agent.main:app --reload
```

- API root: `http://localhost:8000`
- Bulk generation endpoint: `POST /api/citations/generate`
- Styles listing: `GET /api/citations/styles`
- Health check: `GET /health`

> **AI Mode:** When enabled, the backend uses a ConnectOnion agent to interpret the request internally—no extra fields are required.

### 2. Load the Chrome Extension

1. Open `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked** and select the `extension/` directory
4. Pin the extension icon (optional)

### 3. Capture URLs and Download Citations

1. Visit any page you wish to cite.
2. Open the extension popup and click **Add Current Page** to append the active tab URL (repeat for each tab). You can also paste or edit URLs directly in the textarea.
3. Select the citation style and toggle **Use AI** if desired.
4. Click **Generate Citations** to download `citations.txt`.
5. Click **Clear URLs** to reset the list before starting another batch.

---

## Using the REST API Directly

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

- `"use_ai": true` enables the ConnectOnion agent
- `GET /api/citations/styles` → `["harvard", "unsw", "mla", "chicago", "apa", "ieee", "vancouver"]`

---
