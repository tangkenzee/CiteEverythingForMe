"""Tests for CitationGenerator class."""

import unittest
from unittest.mock import Mock, patch

from shared.citation_generator import CitationGenerator


class TestCitationGenerator(unittest.TestCase):
    """Test cases for CitationGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = CitationGenerator()

    def test_init(self):
        """Test CitationGenerator initialization."""
        self.assertEqual(self.generator.citations, {})
        self.assertEqual(self.generator.default_style, "unsw")

    def test_clear_citations(self):
        """Test clearing citations."""
        self.generator.citations = {"url1": {"harvard": {"intext": "test", "reference": "test"}}}
        result = self.generator.clear_citations()
        self.assertEqual(self.generator.citations, {})
        self.assertIn("Cleared", result)

    def test_list_available_styles(self):
        """Test listing available citation styles."""
        result = self.generator.list_available_styles()
        self.assertIn("Harvard", result)
        self.assertIn("UNSW", result)
        self.assertIn("MLA", result)
        self.assertIn("Chicago", result)
        self.assertIn("APA", result)
        self.assertIn("IEEE", result)
        self.assertIn("Vancouver", result)

    def test_get_all_citations_empty(self):
        """Test getting all citations when none exist."""
        result = self.generator.get_all_citations()
        self.assertEqual(result, "No citations have been generated yet.")

    @patch("shared.citation_generator.requests.get")
    def test_get_page_title(self, mock_get):
        """Test fetching page title."""
        mock_response = Mock()
        mock_response.content = b'<html><head><title>Test Page</title></head></html>'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        title = self.generator.get_page_title("https://example.com")
        self.assertEqual(title, "Test Page")

    def test_author_from_domain(self):
        """Test extracting author from domain."""
        # Test basic domain
        author = self.generator._author_from_domain("example.com")
        self.assertEqual(author, "Example")

        # Test government domain
        author = self.generator._author_from_domain("dss.gov.au")
        self.assertEqual(author, "Department of Social Services")

        # Test university domain
        author = self.generator._author_from_domain("unsw.edu.au")
        self.assertIn("University", author)

    def test_strip_html_tags(self):
        """Test HTML tag stripping."""
        text = "<em>Test</em> &lt;URL&gt;"
        result = self.generator._strip_html_tags(text)
        self.assertEqual(result, "Test <URL>")


if __name__ == "__main__":
    unittest.main()

