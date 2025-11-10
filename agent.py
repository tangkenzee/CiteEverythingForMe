from connectonion import Agent
import requests
import json
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, Literal, Optional, Tuple
from datetime import datetime

CitationStyle = Literal["harvard", "mla", "chicago", "apa", "ieee", "vancouver", "unsw"]

class CitationGenerator:
    """Academic citation generator supporting multiple citation styles."""
    
    def __init__(self):
        self.citations: Dict[str, Dict[str, Dict[str, str]]] = {}
        self.default_style: CitationStyle = "harvard"
    
    def get_page_title(self, url: str) -> str:
        """Return the page title or an error string."""
        title, _ = self.get_page_content(url)
        return title

    def get_page_content(self, url: str) -> Tuple[str, Optional[BeautifulSoup]]:
        """Return (title, soup) for the given URL."""
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
        except requests.RequestException as exc:
            return f"Error fetching page: {exc}", None

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string.strip() if soup.title and soup.title.string else 'No Title Found'
        return title, soup
    
    def _determine_author(self, soup: Optional[BeautifulSoup], domain: str) -> str:
        """Extract author/organisation name from page content, fallback to domain if not found."""
        if soup is None:
            return self._author_from_domain(domain)
        
        # Try various meta tags for author information
        author = None
        
        # 1. Try meta name="author"
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author and meta_author.get('content'):
            author = meta_author.get('content').strip()
        
        # 2. Try meta property="article:author"
        if not author:
            meta_article_author = soup.find('meta', attrs={'property': 'article:author'})
            if meta_article_author and meta_article_author.get('content'):
                content = meta_article_author.get('content').strip()
                # If it's a URL, try to extract name from it or skip
                if not content.startswith('http') and '/' not in content:
                    author = content
        
        # 3. Try meta property="og:site_name" (often the organization)
        if not author:
            meta_site_name = soup.find('meta', attrs={'property': 'og:site_name'})
            if meta_site_name and meta_site_name.get('content'):
                author = meta_site_name.get('content').strip()
        
        # 4. Try link rel="author"
        if not author:
            link_author = soup.find('link', attrs={'rel': 'author'})
            if link_author and link_author.get('title'):
                author = link_author.get('title').strip()
        
        # 5. Try schema.org organization/author
        if not author:
            # Look for JSON-LD structured data
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        # PRIORITY: Check for author first (more specific than publisher)
                        if 'author' in data:
                            author_data = data['author']
                            # Handle list of authors
                            if isinstance(author_data, list) and len(author_data) > 0:
                                first_author = author_data[0]
                                if isinstance(first_author, dict) and 'name' in first_author:
                                    author = first_author['name'].strip()
                                    break
                            # Handle single author object
                            elif isinstance(author_data, dict) and 'name' in author_data:
                                author = author_data['name'].strip()
                                break
                        # FALLBACK: Check for publisher (organization, less specific)
                        if not author and 'publisher' in data:
                            publisher = data['publisher']
                            if isinstance(publisher, dict) and 'name' in publisher:
                                author = publisher['name'].strip()
                                break
                except:
                    continue
        
        # 6. Try to find author in text patterns like "By [author name]" or "By [role] [author name]"
        if not author:
            import re
            # FIRST: Search in individual HTML elements (more reliable than full text)
            # Look for elements containing "By" and role keywords
            role_pattern = r'By\s+(?:[A-Za-z\s]+?\s+)?(?:reporter|writer|journalist|editor|correspondent|staff)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
            
            for tag in ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'article']:
                for elem in soup.find_all(tag, limit=50):  # Limit search to first 50 elements
                    text = elem.get_text()
                    if 'By' in text and ('reporter' in text or 'writer' in text or 'journalist' in text):
                        match = re.search(role_pattern, text)
                        if match:
                            potential_author = match.group(1).strip()
                            words = potential_author.split()
                            # Validate: 2 words, each starting with capital, no URLs/special chars
                            if (len(words) == 2 and 
                                all(word and word[0].isupper() and word.isalpha() for word in words) and
                                '/' not in potential_author and 'http' not in potential_author.lower() and
                                '.' not in potential_author):
                                author = potential_author
                                break
                if author:
                    break
            
            # SECOND: If not found in elements, search full text
            if not author:
                text_content = soup.get_text()
                
                # Pattern with role keywords (reporter, writer, etc.) - most reliable
                match = re.search(role_pattern, text_content)
                if match:
                    potential_author = match.group(1).strip()
                    words = potential_author.split()
                    # Validate: 2 words, each starting with capital, no URLs/special chars
                    if (len(words) == 2 and 
                        all(word and word[0].isupper() and word.isalpha() for word in words) and
                        '/' not in potential_author and 'http' not in potential_author.lower() and
                        '.' not in potential_author):
                        author = potential_author
                
                # Simple "By Firstname Lastname" pattern
                if not author:
                    simple_pattern = r'By\s+([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s|$|[.,;:]|\.)'
                    matches = list(re.finditer(simple_pattern, text_content))
                    for match in matches:
                        potential_author = match.group(1).strip()
                        words = potential_author.split()
                        if (len(words) == 2 and 
                            all(word and word[0].isupper() and word.isalpha() for word in words) and
                            '/' not in potential_author and 'http' not in potential_author.lower() and
                            '.' not in potential_author):
                            start_pos = match.start()
                            if start_pos < 1000:  # Prefer matches near the start
                                author = potential_author
                                break
                
                # Other patterns
                if not author:
                    patterns = [
                        r'[Ww]ritten\s+by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s|$|[.,;:])',
                        r'[Aa]uthor:\s+([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s|$|[.,;:])',
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, text_content)
                        if match:
                            potential_author = match.group(1).strip()
                            words = potential_author.split()
                            if (len(words) == 2 and 
                                all(word and word[0].isupper() and word.isalpha() for word in words) and
                                '/' not in potential_author):
                                author = potential_author
                                break
        
        # 7. Try to find author in common HTML elements with author-related classes/ids
        if not author:
            # Look for common author indicators in HTML
            author_selectors = [
                soup.find('span', class_=lambda x: x and ('author' in x.lower() or 'byline' in x.lower())),
                soup.find('div', class_=lambda x: x and ('author' in x.lower() or 'byline' in x.lower())),
                soup.find('p', class_=lambda x: x and ('author' in x.lower() or 'byline' in x.lower())),
                soup.find('span', id=lambda x: x and 'author' in x.lower()),
                soup.find('div', id=lambda x: x and 'author' in x.lower()),
                soup.find('p', id=lambda x: x and 'author' in x.lower()),
            ]
            for element in author_selectors:
                if element:
                    text = element.get_text(strip=True)
                    # Check if it contains "By" pattern
                    if 'By' in text or 'by' in text:
                        # Extract name after "By"
                        import re
                        match = re.search(r'[Bb]y\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', text)
                        if match:
                            author = match.group(1).strip()
                            break
                    elif len(text) < 100 and len(text.split()) <= 4:  # Reasonable author name length
                        author = text
                        break
        
        # 8. Try to find organization name in common HTML elements
        if not author:
            # Look for common organization indicators
            org_selectors = [
                soup.find('span', class_=lambda x: x and 'org' in x.lower()),
                soup.find('div', class_=lambda x: x and 'org' in x.lower()),
            ]
            for element in org_selectors:
                if element and element.get_text(strip=True):
                    text = element.get_text(strip=True)
                    if len(text) < 100:  # Reasonable author name length
                        author = text
                        break
        
        return author.strip() if author else self._author_from_domain(domain)
    
    def _get_access_date(self, url: str) -> datetime:
        """Get the access date for a URL, trying headers first, then current date."""
        response = None
        try:
            response = requests.head(url, timeout=10, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
        except requests.RequestException:
            return datetime.now()

        date_str = response.headers.get('Date', '')
        if date_str:
            from email.utils import parsedate_to_datetime
            try:
                return parsedate_to_datetime(date_str)
            except (TypeError, ValueError):
                pass
        return datetime.now()
    
    def _format_harvard(self, title: str, domain: str, url: str, access_date: datetime) -> Dict[str, str]:
        """Format citation in Harvard style."""
        year = access_date.strftime('%Y')
        date_accessed = access_date.strftime('%d %B %Y')
        
        if title != 'No Title Found' and not title.startswith('Error'):
            intext = f"({title}, {year})"
            reference = f"{title} {year}, <em>{domain}</em>, viewed {date_accessed}, &lt;{url}&gt;."
        else:
            intext = f"(Unknown Title, {year})"
            reference = f"Unknown Title {year}, <em>{domain}</em>, viewed {date_accessed}, &lt;{url}&gt;."
        
        return {"intext": intext, "reference": reference}
    
    def _format_mla(self, title: str, domain: str, url: str, access_date: datetime) -> Dict[str, str]:
        """Format citation in MLA style."""
        date_accessed = access_date.strftime('%d %b. %Y')
        
        if title != 'No Title Found' and not title.startswith('Error'):
            intext = f'("{title}")'
            reference = f'"{title}." <em>{domain}</em>, {date_accessed}, {url}.'
        else:
            intext = '("Unknown Title")'
            reference = f'"Unknown Title." <em>{domain}</em>, {date_accessed}, {url}.'
        
        return {"intext": intext, "reference": reference}
    
    def _format_chicago(self, title: str, domain: str, url: str, access_date: datetime) -> Dict[str, str]:
        """Format citation in Chicago style."""
        date_accessed = access_date.strftime('%B %d, %Y')
        
        if title != 'No Title Found' and not title.startswith('Error'):
            intext = f'({title}, {date_accessed})'
            reference = f'"{title}." {domain}. Accessed {date_accessed}. {url}.'
        else:
            intext = f'(Unknown Title, {date_accessed})'
            reference = f'"Unknown Title." {domain}. Accessed {date_accessed}. {url}.'
        
        return {"intext": intext, "reference": reference}
    
    def _format_apa(self, title: str, domain: str, url: str, access_date: datetime) -> Dict[str, str]:
        """Format citation in APA style."""
        year = access_date.strftime('%Y')
        month_day = access_date.strftime('%B %d')
        
        if title != 'No Title Found' and not title.startswith('Error'):
            intext = f'({title}, {year})'
            reference = f"{title}. ({year}, {month_day}). <em>{domain}</em>. {url}"
        else:
            intext = f'(Unknown Title, {year})'
            reference = f"Unknown Title. ({year}, {month_day}). <em>{domain}</em>. {url}"
        
        return {"intext": intext, "reference": reference}
    
    def _format_ieee(self, title: str, domain: str, url: str, access_date: datetime) -> Dict[str, str]:
        """Format citation in IEEE style."""
        date_accessed = access_date.strftime('%d %B %Y')
        
        if title != 'No Title Found' and not title.startswith('Error'):
            intext = f'[{title}]'
            reference = f'"{title}," {domain}, {date_accessed}. [Online]. Available: {url}'
        else:
            intext = '[Unknown Title]'
            reference = f'"Unknown Title," {domain}, {date_accessed}. [Online]. Available: {url}'
        
        return {"intext": intext, "reference": reference}
    
    def _format_vancouver(self, title: str, domain: str, url: str, access_date: datetime) -> Dict[str, str]:
        """Format citation in Vancouver style."""
        date_accessed = access_date.strftime('%d %B %Y')
        
        if title != 'No Title Found' and not title.startswith('Error'):
            intext = f'({title})'
            reference = f"{title} [Internet]. {domain}; {date_accessed} [cited {date_accessed}]. Available from: {url}"
        else:
            intext = '(Unknown Title)'
            reference = f"Unknown Title [Internet]. {domain}; {date_accessed} [cited {date_accessed}]. Available from: {url}"
        
        return {"intext": intext, "reference": reference}
    
    def _author_from_domain(self, domain: str) -> str:
        """Extract author/organisation name from domain name."""
        # Remove www. prefix if present
        domain_clean = domain.replace('www.', '')
        
        # Extract the main domain name (before first dot)
        main_domain = domain_clean.split('.')[0]
        
        # Convert to title case and replace hyphens/underscores with spaces
        author = main_domain.replace('-', ' ').replace('_', ' ')
        author = ' '.join(word.capitalize() for word in author.split())
        
        # Handle common domain patterns
        if '.gov.au' in domain or '.gov.' in domain:
            # Try to extract organization name from subdomain or main domain
            parts = domain_clean.split('.')
            if len(parts) > 2:
                # e.g., dss.gov.au -> Department of Social Services
                org_part = parts[0].upper()
                # Convert acronyms to full names if possible
                if org_part == 'DSS':
                    return 'Department of Social Services'
                elif org_part == 'ATO':
                    return 'Australian Taxation Office'
                elif org_part == 'ABS':
                    return 'Australian Bureau of Statistics'
            return author + ' (Government)'
        elif '.edu.au' in domain or '.edu.' in domain:
            return author + ' (University)'
        elif '.org' in domain:
            return author + ' (Organisation)'
        
        return author
    
    def _format_unsw(self, title: str, domain: str, url: str, access_date: datetime, author: str) -> Dict[str, str]:
        """Format citation in UNSW Harvard style (University of New South Wales)."""
        year = access_date.strftime('%Y')
        date_accessed = access_date.strftime('%d %B %Y')
        
        # Author is passed in (extracted from page or domain as fallback)
        # Site name is the page title (different from author)
        site_name = title if title != 'No Title Found' and not title.startswith('Error') else 'Unknown website'
        
        # Try to infer sponsor from domain (e.g., .gov.au -> government, .edu.au -> educational institution)
        sponsor = None
        if '.gov.' in domain or '.gov.au' in domain:
            sponsor = "Government"
        elif '.edu.' in domain or '.edu.au' in domain:
            sponsor = "Educational institution"
        elif '.org' in domain:
            sponsor = "Organisation"
        
        # Format reference according to UNSW Harvard style
        # Format: Author Year, Site name (in italics), Name of sponsor (if available), accessed Day Month Year, <URL>.
        # In-text: (Author Year) - NOT (Title Year)
        if title != 'No Title Found' and not title.startswith('Error'):
            intext = f"({author} {year})"
            if sponsor:
                reference = f"{author} {year}, <em>{site_name}</em>, {sponsor}, accessed {date_accessed}, &lt;{url}&gt;."
            else:
                reference = f"{author} {year}, <em>{site_name}</em>, accessed {date_accessed}, &lt;{url}&gt;."
        else:
            intext = f"({author} {year})"
            if sponsor:
                reference = f"{author} {year}, <em>{site_name}</em>, {sponsor}, accessed {date_accessed}, &lt;{url}&gt;."
            else:
                reference = f"{author} {year}, <em>{site_name}</em>, accessed {date_accessed}, &lt;{url}&gt;."
        
        return {"intext": intext, "reference": reference}
    
    def generate_citation(self, url: str, style: CitationStyle = "harvard") -> str:
        """Generate citations in the specified academic style (harvard, mla, chicago, apa, ieee, vancouver, unsw)."""
        # Extract domain
        domain = urlparse(url).netloc
        
        # Get access date
        access_date = self._get_access_date(url)
        
        # Format based on style
        style_lower = style.lower()
        
        # For UNSW style, we need to extract author from page content
        if style_lower == "unsw":
            # Fetch page content to extract author
            title, soup = self.get_page_content(url)
            if title.startswith('Error'):
                # Fallback to simple title fetch if content fetch failed
                title = self.get_page_title(url)
                soup = None
            
            # Extract author from page (falls back to domain if not found)
            author = self._determine_author(soup, domain)
            formatted = self._format_unsw(title, domain, url, access_date, author)
        else:
            # For other styles, just fetch title
            title = self.get_page_title(url)
            
            if style_lower == "harvard":
                formatted = self._format_harvard(title, domain, url, access_date)
            elif style_lower == "mla":
                formatted = self._format_mla(title, domain, url, access_date)
            elif style_lower == "chicago":
                formatted = self._format_chicago(title, domain, url, access_date)
            elif style_lower == "apa":
                formatted = self._format_apa(title, domain, url, access_date)
            elif style_lower == "ieee":
                formatted = self._format_ieee(title, domain, url, access_date)
            elif style_lower == "vancouver":
                formatted = self._format_vancouver(title, domain, url, access_date)
            else:
                # Default to Harvard if unknown style
                formatted = self._format_harvard(title, domain, url, access_date)
                style_lower = "harvard"
        
        # Store citation with style
        if url not in self.citations:
            self.citations[url] = {}
        self.citations[url][style_lower] = formatted
        
        # Automatically export to file after generating citation
        self._update_citation_output(style_lower)
        
        return f"Generated {style_lower.upper()} citation for {url}:\n\nIn-text citation: {formatted['intext']}\n\nReference list entry:\n{formatted['reference']}"
    
    def get_all_citations(self, style: CitationStyle = "harvard") -> str:
        """Retrieve all generated citations in the specified style."""
        if not self.citations:
            return "No citations have been generated yet."
        
        style_lower = style.lower()
        result = f"Generated Citations ({style_lower.upper()} Style):\n\n"
        
        for url, styles_dict in self.citations.items():
            if style_lower in styles_dict:
                citation = styles_dict[style_lower]
                result += f"URL: {url}\n"
                result += f"In-text citation: {citation['intext']}\n"
                result += f"Reference: {citation['reference']}\n\n"
            else:
                result += f"URL: {url}\n"
                result += f"Note: No {style_lower.upper()} citation available for this URL. Generate one first.\n\n"
        
        return result.strip()
    
    def list_available_styles(self) -> str:
        """List all available citation styles."""
        return "Available citation styles:\n\n1. Harvard - Most common in UK/Australia\n2. UNSW - UNSW Harvard referencing style (University of New South Wales)\n3. MLA - Modern Language Association (common in humanities)\n4. Chicago - Chicago Manual of Style (versatile, used in many fields)\n5. APA - American Psychological Association (common in social sciences)\n6. IEEE - Institute of Electrical and Electronics Engineers (engineering/tech)\n7. Vancouver - Numeric style (common in medical/scientific fields)\n\nSpecify the style when generating citations, e.g., 'Generate a UNSW citation for...' or 'Generate a Harvard citation for...'"
    
    def clear_citations(self) -> str:
        """Clear all stored citations."""
        count = len(self.citations)
        self.citations.clear()
        return f"Cleared {count} citation(s)."
    
    def _strip_html_tags(self, text: str) -> str:
        """Remove HTML tags from text for clean file output."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        return text.strip()
    
    def _update_citation_output(self, style: str) -> None:
        """Automatically append new citations to citations_output.txt after each generation."""
        self._append_citations_to_output(style)
    
    def _load_existing_citations(self, filename: str = "citations_output.txt") -> Dict[str, set]:
        """Read existing citations from file to avoid duplicates. Returns dict of {url: {styles}}."""
        existing: Dict[str, set] = {}
        if not os.path.exists(filename):
            return existing

        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()

        for style, url in re.findall(r'Style:\s+(\w+)[\s\S]*?Source:\s+(https?://[^\s]+)', content):
            existing.setdefault(url, set()).add(style.lower())

        old_urls = re.findall(r'Source\s+\d+:\s+(https?://[^\s]+)', content)
        style_context = re.search(r'Citations\s+\((\w+)\s+Style\)', content, re.IGNORECASE)
        detected_style = style_context.group(1).lower() if style_context else 'unknown'
        for url in old_urls:
            existing.setdefault(url, set()).add(detected_style)

        return existing
    
    def _append_citations_to_output(self, style: str, filename: str = "citations_output.txt") -> None:
        """Append new citations to citations_output.txt, avoiding duplicates."""
        if not self.citations:
            return
        
        style_lower = style.lower()
        existing_citations = self._load_existing_citations(filename)  # {url: {styles}}
        
        # Find new citations for this style
        new_citations = []
        for url, styles_dict in self.citations.items():
            if style_lower in styles_dict:
                citation = styles_dict[style_lower]
                # Check if this URL-style combination already exists
                if url in existing_citations:
                    # URL exists, check if this specific style is already there
                    if style_lower in existing_citations[url]:
                        continue  # This URL+style combination already exists, skip
                    # URL exists but not in this style - allow it (same URL, different style)
                # URL doesn't exist or style doesn't exist for this URL - add it
                new_citations.append((url, citation))
        
        if not new_citations:
            return  # No new citations to add
        
        # Append new citations to file
        file_exists = os.path.exists(filename)
        file_empty = not file_exists or os.path.getsize(filename) == 0
        
        with open(filename, 'a', encoding='utf-8') as f:
            # If file is empty, write header
            if file_empty:
                f.write("Citations Output\n")
                f.write("=" * 60 + "\n\n")
            
            # Append new citations
            for url, citation in new_citations:
                # Clean HTML tags for easier copying
                intext_clean = self._strip_html_tags(citation['intext'])
                reference_clean = self._strip_html_tags(citation['reference'])
                
                f.write(f"Style: {style_lower.upper()}\n")
                f.write(f"Source: {url}\n")
                f.write(f"In-text citation: {intext_clean}\n")
                f.write(f"Reference list entry: {reference_clean}\n")
                f.write("\n" + "-" * 60 + "\n\n")
    
    def export_citations_to_file(self, style: CitationStyle = "harvard", filename: str = "citations.txt") -> str:
        """Export all citations in the specified style to a text file for easy copying."""
        if not self.citations:
            return "No citations to export. Generate some citations first."
        
        style_lower = style.lower()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Citations ({style_lower.upper()} Style)\n")
                f.write("=" * 60 + "\n\n")
                
                citation_count = 0
                for url, styles_dict in self.citations.items():
                    if style_lower in styles_dict:
                        citation = styles_dict[style_lower]
                        citation_count += 1
                        
                        # Clean HTML tags for easier copying
                        intext_clean = self._strip_html_tags(citation['intext'])
                        reference_clean = self._strip_html_tags(citation['reference'])
                        
                        f.write(f"Source {citation_count}: {url}\n")
                        f.write(f"In-text citation: {intext_clean}\n")
                        f.write(f"Reference list entry: {reference_clean}\n")
                        f.write("\n" + "-" * 60 + "\n\n")
                
                if citation_count == 0:
                    f.write(f"No {style_lower.upper()} citations found. Generate citations in this style first.\n")
            
            return f"Exported {citation_count} citation(s) to {filename}. You can now copy and paste from the file!"
        except Exception as e:
            return f"Error exporting citations: {str(e)}"


# Create the citation generator instance
citation_gen = CitationGenerator()

# Create the ConnectOnion agent
agent = Agent(
    name="citation_generator",
    system_prompt="prompt.md",
    tools=[citation_gen],
    max_iterations=15,
    model="co/gpt-5-nano"
)


# Interactive usage - users provide their own URLs
if __name__ == "__main__":
    print("=" * 60)
    print("Academic Citation Generator")
    print("=" * 60)
    print("\nEnter your requests in natural language.")
    print("Examples:")
    print("  - 'Generate an APA citation for https://www.example.com'")
    print("  - 'Generate Harvard citations for https://url1.com and https://url2.com'")
    print("  - 'Show me all my MLA citations'")
    print("  - 'Export all my UNSW citations to a file'")
    print("  - Type 'quit' or 'exit' to stop\n")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\nYour request: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! Your citations have been saved.")
                break
            # Process user's request
            result = agent.input(user_input)
            print(f"\n{result}")
            print("-" * 60)
        except KeyboardInterrupt:
            print("\n\nGoodbye! Your citations have been saved.")
            break