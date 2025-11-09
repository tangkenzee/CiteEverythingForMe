# How to Use the Academic Citation Generator

A practical guide for university students on using the citation generator agent.

## Quick Start

### 1. Run the Agent (Interactive Mode)

```bash
# Navigate to the project directory
cd CiteEverythingForMe

# Run the agent
python agent.py
```

This starts an interactive session where **you provide your own URLs**. The agent will prompt you for requests, and you can type in natural language:

```
Your request: Generate an APA citation for https://www.your-source.com
Your request: Generate Harvard citations for https://url1.com and https://url2.com
Your request: Show me all my MLA citations
Your request: quit
```

### 2. Use in Your Own Python Code

```python
from agent import agent

# You provide your own URLs
your_url = "https://www.your-research-source.com"
result = agent.input(f"Generate a Harvard citation for {your_url}")
print(result)

# Or with multiple URLs
urls = [
    "https://www.source1.com",
    "https://www.source2.com"
]
result = agent.input(f"Generate APA citations for {' and '.join(urls)}")
print(result)
```

---

## Common Usage Patterns

### Basic Citation Generation

**Single URL, Default Style (Harvard):**
```
Generate a citation for https://www.python.org
```

**Single URL, Specific Style:**
```
Generate an MLA citation for https://www.example.com
```

**Multiple URLs:**
```
Generate Harvard citations for https://www.example.com and https://www.python.org
```

---

## Citation Style Examples

### Harvard Style
**Request:**
```
Generate a Harvard citation for https://www.python.org
```

**Output:**
- In-text: `(Welcome to Python.org, 2025)`
- Reference: `Welcome to Python.org 2025, www.python.org, viewed 09 November 2025, <https://www.python.org>.`

---

### MLA Style
**Request:**
```
Generate an MLA citation for https://www.example.com
```

**Output:**
- In-text: `("Example Domain")`
- Reference: `"Example Domain." www.example.com, 09 Nov. 2025, https://www.example.com.`

---

### APA Style
**Request:**
```
Generate an APA citation for https://www.python.org
```

**Output:**
- In-text: `(Welcome to Python.org, 2025)`
- Reference: `Welcome to Python.org. (2025, November 09). www.python.org. https://www.python.org`

---

### Chicago Style
**Request:**
```
Generate a Chicago citation for https://www.example.com
```

**Output:**
- In-text: `(Example Domain, November 09, 2025)`
- Reference: `"Example Domain." www.example.com. Accessed November 09, 2025. https://www.example.com.`

---

### IEEE Style
**Request:**
```
Generate an IEEE citation for https://www.python.org
```

**Output:**
- In-text: `[Welcome to Python.org]`
- Reference: `"Welcome to Python.org," www.python.org, 09 November 2025. [Online]. Available: https://www.python.org`

---

### Vancouver Style
**Request:**
```
Generate a Vancouver citation for https://www.example.com
```

**Output:**
- In-text: `(Example Domain)`
- Reference: `Example Domain [Internet]. www.example.com; 09 November 2025 [cited 09 November 2025]. Available from: https://www.example.com`

---

## Advanced Usage

### Generate Multiple Styles for Same URL

**Request:**
```
Generate APA and Chicago citations for https://www.python.org
```

The agent will generate both styles and store them separately.

---

### View All Citations in a Style

**Request:**
```
Show me all my Harvard citations
```

This retrieves all URLs you've cited in Harvard style.

---

### List Available Styles

**Request:**
```
What citation styles are available?
```

**Output:**
```
Available citation styles:

1. Harvard - Most common in UK/Australia
2. MLA - Modern Language Association (common in humanities)
3. Chicago - Chicago Manual of Style (versatile, used in many fields)
4. APA - American Psychological Association (common in social sciences)
5. IEEE - Institute of Electrical and Electronics Engineers (engineering/tech)
6. Vancouver - Numeric style (common in medical/scientific fields)
```

---

### Working with Multiple Sources

**Request:**
```
Generate MLA citations for:
- https://www.example.com
- https://www.python.org
- https://www.wikipedia.org
```

The agent will process all URLs and generate citations for each.

---

## Interactive Python Session

### Example 1: Research Paper Workflow

```python
from agent import agent

# Step 1: Generate citations for your sources
agent.input("Generate APA citations for https://www.example.com and https://www.python.org")

# Step 2: View all your APA citations
result = agent.input("Show me all my APA citations")
print(result)

# Step 3: Copy the citations into your paper
```

---

### Example 2: Comparing Citation Styles

```python
from agent import agent

url = "https://www.example.com"

# Generate in multiple styles
agent.input(f"Generate Harvard, MLA, and APA citations for {url}")

# View each style
print("Harvard:")
print(agent.input("Show me Harvard citations"))

print("\nMLA:")
print(agent.input("Show me MLA citations"))

print("\nAPA:")
print(agent.input("Show me APA citations"))
```

---

### Example 3: Batch Processing with Your URLs

```python
from agent import agent

# You provide your own list of URLs
your_urls = [
    "https://www.your-source1.com",
    "https://www.your-source2.com",
    "https://www.your-source3.com"
]

# Generate citations for all your URLs
for url in your_urls:
    result = agent.input(f"Generate a Harvard citation for {url}")
    print(result)
    print()
```

### Example 4: User Input URLs

```python
from agent import agent

# Get URLs from user input
print("Enter URLs to cite (one per line, empty line to finish):")
urls = []
while True:
    url = input().strip()
    if not url:
        break
    urls.append(url)

# Generate citations for user's URLs
style = input("Enter citation style (Harvard, MLA, APA, etc.): ").strip()
for url in urls:
    result = agent.input(f"Generate a {style} citation for {url}")
    print(result)
    print()
```

---

## Tips for Best Results

### 1. **Always Specify the Style**
   - ✅ Good: "Generate an APA citation for..."
   - ❌ Less clear: "Generate a citation for..." (defaults to Harvard)

### 2. **Use Complete URLs**
   - ✅ Good: "https://www.example.com/article"
   - ❌ Problem: "example.com" (may not work correctly)

### 3. **Be Specific About Multiple URLs**
   - ✅ Good: "Generate MLA citations for URL1 and URL2"
   - ✅ Also good: List URLs on separate lines

### 4. **Check Your Institution's Requirements**
   - Some universities have specific variations of citation styles
   - Always verify the format matches your institution's guidelines

### 5. **Verify URLs Before Citing**
   - Make sure URLs are accessible
   - The agent will still generate citations for inaccessible pages, but with "Unknown Title"

---

## Common Questions

### Q: What if I don't specify a citation style?
**A:** The agent defaults to Harvard style. It's better to always specify your required style.

### Q: Can I generate the same URL in multiple styles?
**A:** Yes! The agent stores citations by style, so you can generate the same URL in Harvard, MLA, APA, etc.

### Q: What if a webpage can't be accessed?
**A:** The agent will still generate a citation using "Unknown Title" and inform you about the issue.

### Q: How do I clear my citations?
**A:** Ask: "Clear all citations" or the agent will use the `clear_citations()` tool.

### Q: Can I use this for non-web sources?
**A:** Currently, the agent is designed for web sources (URLs). For books, articles, etc., you'd need to manually format or extend the agent.

---

## Real-World Example: Writing a Research Paper

**Step 1: Run the agent interactively**
```bash
python agent.py
```

**Step 2: Provide your research sources**
```
Your request: Generate an APA citation for https://www.your-research-source.com
Your request: Generate an APA citation for https://www.another-source.com
Your request: Generate an APA citation for https://www.third-source.com
```

**Step 3: Get all citations for your reference list**
```
Your request: Show me all my APA citations
```

**Or use in Python code with your own URLs:**

```python
from agent import agent

# Your research sources (you provide these)
sources = [
    "https://www.your-research-source.com",
    "https://www.another-source.com",
    "https://www.third-source.com"
]

# Step 1: Generate all citations in your required style (e.g., APA)
for url in sources:
    agent.input(f"Generate an APA citation for {url}")

# Step 2: Get all citations formatted for your reference list
references = agent.input("Show me all my APA citations")
print("References:")
print(references)

# Step 3: Use in-text citations as you write
# The agent provides in-text format like: (Title, 2025)
```

---

## Troubleshooting

### Issue: Agent doesn't recognize the style
**Solution:** Use the full style name: "Harvard", "MLA", "APA", "Chicago", "IEEE", "Vancouver"

### Issue: Citation format looks wrong
**Solution:** 
- Check if your institution uses a specific variation
- Verify the URL is correct and accessible
- Try regenerating the citation

### Issue: Can't retrieve citations
**Solution:** Make sure you've generated citations first. The agent stores them by style.

---

## Next Steps

1. **Try it out:** Run the agent with a few test URLs
2. **Generate citations:** Create citations for your actual research sources
3. **Verify formatting:** Check against your institution's citation guide
4. **Use in your paper:** Copy the formatted citations into your reference list

---

## Need Help?

The agent is designed to be helpful and will:
- Ask for clarification if your request is unclear
- Suggest citation styles if you're unsure
- Explain citation formats when asked
- Handle errors gracefully

Just ask in natural language - the agent understands!

