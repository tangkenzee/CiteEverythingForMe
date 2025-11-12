from fastapi.testclient import TestClient

from agent import main as agent_main
from shared.citation_generator import CitationGenerator

client = TestClient(agent_main.app)


def test_generate_citations_deterministic(monkeypatch):
    def fake_generate(self: CitationGenerator, url: str, style: str = "harvard") -> str:
        self.citations.setdefault(url, {})[style.lower()] = {
            "intext": "(Test Author 2025)",
            "reference": "Test Author 2025, Test Title, accessed 10 November 2025, <https://test.com>.",
        }
        return "OK"

    monkeypatch.setattr(CitationGenerator, "generate_citation", fake_generate)

    response = client.post(
        "/api/citations/generate",
        json={"urls": ["https://example.com"], "style": "harvard", "use_ai": False},
    )

    assert response.status_code == 200
    body = response.content.decode()
    assert "Test Author" in body
    assert "Citations Output" in body


def test_generate_citations_ai_mode(monkeypatch):
    async def fake_generate_with_ai(url: str, style: str, generator: CitationGenerator) -> None:
        generator.citations.setdefault(url, {})[style.lower()] = {
            "intext": "(AI Author 2025)",
            "reference": "AI Author 2025, AI Title, accessed 10 November 2025, <https://ai.com>.",
        }

    monkeypatch.setattr(agent_main, "_generate_with_ai", fake_generate_with_ai)

    response = client.post(
        "/api/citations/generate",
        json={"urls": ["https://example.com"], "style": "unsw", "use_ai": True},
    )

    assert response.status_code == 200
    body = response.content.decode()
    assert "AI Author" in body
    assert "UNSW" in body


def test_list_supported_styles():
    response = client.get("/api/citations/styles")
    assert response.status_code == 200
    styles = response.json()
    assert "unsw" in styles
    assert "harvard" in styles
