import pytest

from src.agent.tools.get_citation import fetch_cites


def test_get_citation_success(monkeypatch):
    class DummyResponse:
        def __init__(self, data):
            self._data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self._data

    def fake_get(url, params=None, timeout=None):
        assert "citeas" in url
        return DummyResponse({"citations": [{"citation": "test citation"}]})

    monkeypatch.setattr("src.agent.tools.get_citation.httpx.get", fake_get)
    result = fetch_cites("https://example.com")
    assert result["citations"][0]["citation"] == "test citation"


def test_get_citation_http_error(monkeypatch):
    class ErrorResponse:
        def raise_for_status(self):
            raise RuntimeError("400")

    monkeypatch.setattr(
        "src.agent.tools.get_citation.httpx.get",
        lambda *args, **kwargs: ErrorResponse(),
    )
    with pytest.raises(RuntimeError):
        fetch_cites("https://example.com")
