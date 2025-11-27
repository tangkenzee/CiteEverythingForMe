import pytest

from src.agent.tools.scrape_metadata import scrape_metadata


def test_scrape_metadata_success(monkeypatch):
    class DummyResponse:
        text = "<html></html>"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        "src.agent.tools.scrape_metadata.httpx.get",
        lambda url, timeout=None, follow_redirects=None: DummyResponse(),
    )
    monkeypatch.setattr(
        "src.agent.tools.scrape_metadata.trafilatura.extract_metadata",
        lambda text: {"metadata": {"title": "Scraped", "author": ["Author"]}},
    )
    monkeypatch.setattr(
        "src.agent.tools.scrape_metadata.trafilatura.fetch_url",
        lambda url: "<html></html>",
    )
    result = scrape_metadata("https://example.com")
    assert result["metadata"]["title"] == "Scraped"
    assert result["metadata"]["author"] == ["Author"]


def test_scrape_metadata_failure(monkeypatch):
    def failing_get(url, timeout=None, follow_redirects=None):
        raise RuntimeError("blocked")

    monkeypatch.setattr("src.agent.tools.scrape_metadata.httpx.get", failing_get)
    result = scrape_metadata("https://example.com")
    assert result["metadata"] == {}
