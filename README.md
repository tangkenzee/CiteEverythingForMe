# Academic Citation Generator Agent

ALL your citations at once, no more searching one by one. 
CiteEverythingForME is a ConnectOnion-powered agent designed for university students to generate properly formatted academic citations for their written reports and formal papers.

## Features

- **Multiple Citation Styles**: Supports 7 major academic formats:
  - Harvard (default) - UK/Australia universities
  - UNSW - UNSW Harvard referencing style (University of New South Wales)
  - MLA - Humanities and literature
  - Chicago - Versatile, many disciplines
  - APA - Social sciences and psychology
  - IEEE - Engineering and technology
  - Vancouver - Medical and scientific fields

- Fetches webpage titles and metadata automatically
- Generates both in-text citations and reference list entries
- Stores citations by style for easy retrieval
- Handles errors gracefully
- Natural language interface - just ask in plain English

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the agent:**
   ```bash
   python agent.py
   ```
   
   This starts an interactive session. **You provide your own URLs** when prompted:
   ```
   Your request: Generate an APA citation for https://www.your-source.com
   Your request: Generate a UNSW citation for https://www.example.com
   Your request: Generate Harvard citations for https://url1.com and https://url2.com
   Your request: quit
   ```

**Note:** This agent uses ConnectOnion's hosted model (`co/gpt-4o-mini`), so no API key configuration is required!

## Usage

### Basic Usage

**Interactive Mode (Recommended):**
```bash
python agent.py
# Then enter your requests with your own URLs:
# Your request: Generate an APA citation for https://www.your-source.com
# Your request: Generate a UNSW citation for https://www.example.com
# Your request: Generate Harvard citations for https://url1.com and https://url2.com
```

**Or use in Python code with your own URLs:**
```python
from agent import agent

# You provide your own URLs
your_url = "https://www.your-research-source.com"
result = agent.input(f"Generate a Harvard citation for {your_url}")
print(result)

# Generate an MLA citation for your URL
result = agent.input(f"Generate an MLA citation for {your_url}")
print(result)

# Generate a UNSW citation (for UNSW students)
result = agent.input(f"Generate a UNSW citation for {your_url}")
print(result)

# Generate multiple styles for the same URL
result = agent.input(f"Generate APA and Chicago citations for {your_url}")
print(result)

# View all citations in a specific style
result = agent.input("Show me all my Harvard citations")
print(result)

# List available citation styles
result = agent.input("What citation styles are available?")
print(result)
```

### Citation Formats

The agent generates two types of citations for each style:

- **In-text citation** - For use within your paper
- **Reference list entry** - For your bibliography/references section

Each citation style follows its specific academic formatting rules. Examples:

**Harvard Style:**
- In-text: `(Example Domain, 2025)`
- Reference: `Example Domain 2025, www.example.com, viewed 09 November 2025, <https://www.example.com>.`

**UNSW Style (UNSW Harvard Referencing):**
- In-text: `(Example 2025)`
- Reference: `Example 2025, Example Domain, accessed 09 November 2025, <https://www.example.com>.`
- Note: UNSW style follows the University of New South Wales Harvard referencing guidelines, with author/organisation name derived from page content when available

**MLA Style:**
- In-text: `("Example Domain")`
- Reference: `"Example Domain." www.example.com, 09 Nov. 2025, https://www.example.com.`

**APA Style:**
- In-text: `(Example Domain, 2025)`
- Reference: `Example Domain. (2025, November 09). www.example.com. https://www.example.com`

## Tools Available

The agent has access to these tools:

- `fetch_page_title(url)` - Fetch the title of a webpage
- `generate_citation(url, style)` - Generate citations in specified style (harvard, unsw, mla, chicago, apa, ieee, vancouver)
- `get_all_citations(style)` - Retrieve all stored citations in a specific style
- `list_available_styles()` - List all supported citation formats
- `clear_citations()` - Clear all stored citations

## Citation Styles Guide

| Style | Common Use | Example Fields |
|-------|-----------|----------------|
| **Harvard** | UK/Australia universities | General academic work |
| **UNSW** | University of New South Wales | UNSW-specific Harvard style |
| **MLA** | Humanities, literature | English, history, arts |
| **Chicago** | Versatile, many fields | History, business, social sciences |
| **APA** | Social sciences | Psychology, education, sociology |
| **IEEE** | Engineering, technology | Computer science, engineering |
| **Vancouver** | Medical, scientific | Medicine, health sciences, biology |

## Requirements

- Python 3.8+
- ConnectOnion framework
- requests
- beautifulsoup4
- lxml

## Notes

- **Default Style**: If you don't specify a style, the agent defaults to Harvard
- **Multiple Styles**: You can generate the same URL in multiple citation styles
- **Style Storage**: Citations are stored by style, so you can retrieve all citations in a specific format
- **Academic Standards**: All citations follow official formatting guidelines for each style
- **Automatic File Export**: All citations are automatically saved to `citations_output.txt` for easy copying
- **Duplicate Prevention**: The same citation (URL + style) won't be added twice to the output file
- **Behavior Tracking**: The agent uses ConnectOnion's automatic behavior tracking
- **Error Handling**: If a page can't be accessed, the agent still generates a citation with "Unknown Title"

## Tips for Students

1. **Specify your style** - Always mention which citation style you need (e.g., "Generate an APA citation...")
2. **UNSW Students** - If you're a UNSW student, use the UNSW style which follows UNSW's specific Harvard referencing guidelines. See `UNSW_Harvard_referencing.md` for detailed formatting rules.
3. **Check with your institution** - Some universities have specific variations of citation styles
4. **Verify URLs** - Make sure URLs are accessible and correct before generating citations
5. **Multiple sources** - You can generate citations for multiple URLs in one request
6. **Style consistency** - Use the same citation style throughout your paper
7. **Author extraction** - The agent automatically extracts author/organisation names from page content when available, falling back to domain name if not found

