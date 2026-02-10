"""Text extraction utilities."""

from bs4 import BeautifulSoup


def extract_title(soup: BeautifulSoup) -> str:
    """Extract title from HTML.
    
    Prioritizes h1 tag over title tag for better accuracy.
    """
    # Try h1 first
    h1_tag = soup.find('h1')
    if h1_tag:
        return h1_tag.get_text(strip=True)
    
    # Fallback to title tag
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.get_text(strip=True)
    
    return 'Untitled'


def extract_headings(soup: BeautifulSoup) -> list[dict]:
    """Extract all headings from HTML."""
    headings = []
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
        headings.append({
            'level': heading.name,
            'text': heading.get_text(strip=True)
        })
    return headings


def extract_code_blocks(soup: BeautifulSoup) -> list[str]:
    """Extract code blocks from HTML."""
    code_blocks = []
    for code in soup.find_all(['code', 'pre', '.fragment']):
        code_text = code.get_text(strip=True)
        if len(code_text) > 10:
            code_blocks.append(code_text)
    return code_blocks


def extract_text(soup: BeautifulSoup) -> str:
    """Extract main text content from HTML."""
    # Remove unwanted elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', '.navpath']):
        element.decompose()
    
    return soup.get_text(separator='\n', strip=True)
