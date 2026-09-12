from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def clean_html(soup: BeautifulSoup):
    """Remove scripts, styles, navigation, headers, footers."""
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "aside"]):
        tag.decompose()

def extract_links(soup: BeautifulSoup, base_url: str) -> set[str]:
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(base_url, href)
        # Clean URL fragment
        full_url = full_url.split('#')[0]
        links.add(full_url)
    return links

def parse_html(html: str, url: str) -> tuple[str, str, set[str], list[dict]]:
    """
    Returns title, full text, extracted links, and chunks.
    Chunking strategy: split by headings.
    """
    soup = BeautifulSoup(html, "html.parser")
    
    title = ""
    if soup.title:
        title = soup.title.string.strip() if soup.title.string else ""
        
    links = extract_links(soup, url)
    
    clean_html(soup)
    full_text = soup.get_text(separator="\n", strip=True)
    
    chunks = []
    current_section = "General"
    current_content = []
    
    for element in soup.body.descendants if soup.body else soup.descendants:
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if current_content:
                text = " ".join(current_content).strip()
                if text:
                    chunks.append({
                        'title': title,
                        'section': current_section,
                        'content': text
                    })
            current_section = element.get_text(strip=True)
            current_content = []
        elif element.name in ['p', 'li', 'td', 'div']:
            text = element.get_text(strip=True)
            if text and text not in current_content:
                current_content.append(text)
                
    if current_content:
        text = " ".join(current_content).strip()
        if text:
            chunks.append({
                'title': title,
                'section': current_section,
                'content': text
            })
            
    # Fallback if no chunks generated
    if not chunks and full_text:
        chunks.append({
            'title': title,
            'section': 'General',
            'content': full_text[:2000] # simple length fallback
        })
        
    return title, full_text, links, chunks
