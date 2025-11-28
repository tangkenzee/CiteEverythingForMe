from src.agent.tools.format_UNSW import format_UNSW


def test_format_reuses_authors_and_year():
    citations_object = {
        "metadata": {
            "author": [{"family": "Doe", "given": "Jane"}],
            "year": 2025,
            "title": "Test Page",
            "publisher": "Publisher",
            "url": "https://example.com",
        }
    }
    result = format_UNSW(citations_object)
    assert "Doe, J." in result
    assert "2025" in result
    assert "<https://example.com>" in result


def test_format_handles_missing_fields():
    citations_object = {"metadata": {"title": "Title Only"}}
    result = format_UNSW(citations_object)
    assert "Title Only" in result
    assert "accessed " in result


def test_format_accepts_serialized_input():
    citations_object = "{'metadata': {'title': 'Serialized'}}"
    result = format_UNSW(citations_object)
    assert "Serialized" in result


def test_format_handles_empty_input():
    citations_object = {}
    result = format_UNSW(citations_object)
    assert result.startswith("accessed ")
