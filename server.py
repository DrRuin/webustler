import os
import re
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from fastmcp import FastMCP

_PRIMARY_URL = "https://r.jina.ai/"
_FALLBACK_URL = "http://host.docker.internal:8191/v1"
_TIMEOUT = int(os.getenv("TIMEOUT", "120"))
_WORDS_PER_MINUTE = 200  # Average reading speed

# Common file signatures for binary detection
_FILE_SIGNATURES = {
    b"%PDF": "PDF",
    b"\x89PNG": "PNG",
    b"\xff\xd8\xff": "JPEG",
    b"GIF8": "GIF",
    b"PK\x03\x04": "ZIP/Office",
    b"Rar!": "RAR",
    b"\x1f\x8b": "GZIP",
}

_BLOCKED = [
    "Verify you are human by completing the action below.",
    "Warning: Target URL returned error 403: Forbidden",
    "Verification is taking longer than expected. Check your Internet connection",
    "Warning: This page maybe requiring CAPTCHA, please make sure you are authorized to access this page.",
    "needs to review the security of your connection before proceeding.",
]

_REMOVE_TAGS = [
    "script",
    "style",
    "nav",
    "footer",
    "header",
    "noscript",
    "aside",
    "iframe",
    "form",
    "button",
    "input",
    "select",
    "textarea",
    "svg",
    "canvas",
    "video",
    "audio",
    "map",
    "object",
    "embed",
]

_REMOVE_SELECTORS = [
    "[class*='sidebar']",
    "[class*='comment']",
    "[class*='advertisement']",
    "[class*='ad-']",
    "[class*='ads-']",
    "[class*='advert']",
    "[class*='social']",
    "[class*='share']",
    "[class*='related']",
    "[class*='popup']",
    "[class*='modal']",
    "[class*='cookie']",
    "[class*='banner']",
    "[class*='promo']",
    "[class*='newsletter']",
    "[id*='sidebar']",
    "[id*='comment']",
    "[id*='advertisement']",
    "[id*='ad-']",
    "[id*='ads-']",
    "[role='complementary']",
    "[role='banner']",
    "[role='navigation']",
    "[role='contentinfo']",
]

mcp = FastMCP("Webustler")


def _needs_fallback(content: str) -> bool:
    return any(p in content for p in _BLOCKED)


def _fetch_primary(url: str) -> tuple[str, int]:
    try:
        response = requests.get(f"{_PRIMARY_URL}{url}", timeout=_TIMEOUT)
        response.raise_for_status()
        return response.text, response.status_code
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP {e.response.status_code}: {e.response.text[:200]}")
    except requests.exceptions.Timeout:
        raise Exception("Request timed out")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")


def _fetch_fallback(url: str) -> tuple[str, int]:
    try:
        response = requests.post(
            _FALLBACK_URL,
            json={"cmd": "request.get", "url": url, "maxTimeout": _TIMEOUT * 1000},
            timeout=_TIMEOUT + 30,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP {e.response.status_code}: {e.response.text[:200]}")
    except requests.exceptions.Timeout:
        raise Exception("Request timed out")
    except requests.exceptions.ConnectionError:
        raise Exception("Connection failed - is the service running?")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")

    data = response.json()
    if data.get("status") != "ok":
        raise Exception(f"Service error: {data.get('message', 'Unknown error')}")

    status_code = data.get("solution", {}).get("status", 200)
    return data["solution"]["response"], status_code


def _is_binary_content(content: str) -> tuple[bool, str]:
    """Check if content is binary. Returns (is_binary, file_type)."""
    try:
        header = content[:16].encode("latin-1")
        for sig, name in _FILE_SIGNATURES.items():
            if header.startswith(sig):
                return True, name
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    # Check for null bytes or high non-printable ratio
    if "\x00" in content[:1000]:
        return True, "Binary"
    sample = content[:2000]
    non_print = sum(1 for c in sample if ord(c) < 32 and c not in "\n\r\t")
    if len(sample) > 0 and non_print / len(sample) > 0.1:
        return True, "Binary"

    return False, ""


def _format_file_response(url: str, file_type: str) -> str:
    """Format response for file downloads."""
    filename = url.split("/")[-1] if "/" in url else "unknown"
    return f"""---
sourceURL: {url}
contentType: {file_type}
filename: {filename}
isFile: true
---

# File Download Detected

The URL points to a **{file_type}** file rather than a web page.

| Property | Value |
|----------|-------|
| Type | {file_type} |
| Filename | {filename} |
| URL | {url} |

This scraper is designed for web pages. Use a dedicated tool to process this file type."""


def _normalize_url(href: str, base_url: str) -> str | None:
    """Normalize a URL to absolute form."""
    if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
        return None
    try:
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        if parsed.scheme in ("http", "https"):
            return absolute
    except Exception:
        pass
    return None


def _get_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _extract_links(soup: BeautifulSoup, base_url: str) -> tuple[list[str], list[str]]:
    """Extract internal and external links from the page."""
    base_domain = _get_domain(base_url)
    internal = set()
    external = set()

    for a in soup.find_all("a", href=True):
        if url := _normalize_url(a["href"], base_url):
            if _get_domain(url) == base_domain:
                internal.add(url)
            else:
                external.add(url)

    return sorted(internal), sorted(external)


def _extract_images(soup: BeautifulSoup, base_url: str) -> list[str]:
    """Extract all unique image URLs from the page."""
    images = set()
    for img in soup.find_all("img", src=True):
        src = img["src"]
        if not src.startswith("data:"):
            if url := _normalize_url(src, base_url):
                images.add(url)
    # Also check srcset
    for img in soup.find_all("img", srcset=True):
        for part in img["srcset"].split(","):
            src = part.strip().split()[0]
            if not src.startswith("data:"):
                if url := _normalize_url(src, base_url):
                    images.add(url)
    return sorted(images)


def _count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def _estimate_reading_time(word_count: int) -> str:
    """Estimate reading time based on word count."""
    minutes = max(1, round(word_count / _WORDS_PER_MINUTE))
    if minutes == 1:
        return "1 min"
    return f"{minutes} mins"


def _extract_metadata(soup: BeautifulSoup, base_url: str, status_code: int) -> dict:
    """Extract metadata from HTML."""
    metadata = {"sourceURL": base_url, "statusCode": status_code}

    # Title
    if soup.title and soup.title.string:
        metadata["title"] = soup.title.string.strip()
    elif og_title := soup.find("meta", property="og:title"):
        metadata["title"] = og_title.get("content", "").strip()

    # Description
    if desc := soup.find("meta", attrs={"name": "description"}):
        metadata["description"] = desc.get("content", "").strip()
    elif og_desc := soup.find("meta", property="og:description"):
        metadata["description"] = og_desc.get("content", "").strip()

    # Author
    if author := soup.find("meta", attrs={"name": "author"}):
        metadata["author"] = author.get("content", "").strip()

    # Language
    if html_tag := soup.find("html"):
        if lang := html_tag.get("lang"):
            metadata["language"] = lang.strip()

    # Canonical URL
    if canonical := soup.find("link", rel="canonical"):
        metadata["canonical"] = canonical.get("href", "").strip()

    # Keywords
    if keywords := soup.find("meta", attrs={"name": "keywords"}):
        kw_list = [
            k.strip() for k in keywords.get("content", "").split(",") if k.strip()
        ]
        if kw_list:
            metadata["keywords"] = kw_list

    # Robots
    if robots := soup.find("meta", attrs={"name": "robots"}):
        metadata["robots"] = robots.get("content", "").strip()

    # Open Graph
    og_data = {}
    for og in soup.find_all("meta", property=re.compile(r"^og:")):
        key = og.get("property", "")[3:]
        if key and og.get("content"):
            og_data[key] = og.get("content").strip()
    if og_data:
        metadata["openGraph"] = og_data

    # Twitter Card
    twitter_data = {}
    for tw in soup.find_all("meta", attrs={"name": re.compile(r"^twitter:")}):
        key = tw.get("name", "")[8:]
        if key and tw.get("content"):
            twitter_data[key] = tw.get("content").strip()
    if twitter_data:
        metadata["twitter"] = twitter_data

    # Published/Modified time
    if pub_time := soup.find("meta", property="article:published_time"):
        metadata["publishedTime"] = pub_time.get("content", "").strip()
    if mod_time := soup.find("meta", property="article:modified_time"):
        metadata["modifiedTime"] = mod_time.get("content", "").strip()

    # Favicon
    if favicon := soup.find("link", rel=re.compile(r"icon")):
        href = favicon.get("href", "").strip()
        if href:
            metadata["favicon"] = _normalize_url(href, base_url) or href

    return metadata


def _remove_base64_images(soup: BeautifulSoup) -> None:
    """Remove base64 encoded images to save tokens."""
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src.startswith("data:"):
            img.decompose()


def _clean_html(soup: BeautifulSoup) -> BeautifulSoup:
    """Clean HTML by removing unwanted elements."""
    # Remove unwanted tags (but keep tables!)
    for tag in soup.find_all(_REMOVE_TAGS):
        tag.decompose()

    # Remove elements by CSS selectors
    for selector in _REMOVE_SELECTORS:
        for el in soup.select(selector):
            el.decompose()

    # Remove base64 images
    _remove_base64_images(soup)

    # Remove empty elements (but preserve table structure)
    for tag in soup.find_all():
        if tag.name in ["table", "thead", "tbody", "tr", "th", "td"]:
            continue
        if not tag.get_text(strip=True) and tag.name not in ["img", "br", "hr"]:
            tag.decompose()

    return soup


def _limit_newlines(text: str, max_consecutive: int = 3) -> str:
    """Limit consecutive newlines."""
    pattern = r"\n{" + str(max_consecutive + 1) + r",}"
    return re.sub(pattern, "\n" * max_consecutive, text)


def _to_markdown(
    html: str, base_url: str, status_code: int
) -> tuple[dict, str, list, list, list]:
    """Convert HTML to metadata, markdown, internal links, external links, and images."""
    soup = BeautifulSoup(html, "html.parser")

    # Extract data before cleaning
    metadata = _extract_metadata(soup, base_url, status_code)
    internal_links, external_links = _extract_links(soup, base_url)
    images = _extract_images(soup, base_url)

    # Clean HTML
    soup = _clean_html(soup)

    # Find main content
    main = soup.find("article") or soup.find("main") or soup.find("body")

    # Convert to markdown with enhanced options (preserve tables)
    markdown = md(
        str(main),
        heading_style="ATX",
        bullets="*",
        code_language="",
        strip=["a"],
        escape_asterisks=False,
        escape_underscores=False,
    )

    # Limit consecutive newlines
    markdown = _limit_newlines(markdown.strip())

    # Add content stats to metadata
    word_count = _count_words(markdown)
    metadata["wordCount"] = word_count
    metadata["readingTime"] = _estimate_reading_time(word_count)

    return metadata, markdown, internal_links, external_links, images


def _format_output(
    metadata: dict,
    markdown: str,
    internal_links: list,
    external_links: list,
    images: list,
) -> str:
    """Format the final output with YAML frontmatter."""
    output = ["---"]

    for key, value in metadata.items():
        if isinstance(value, dict):
            output.append(f"{key}:")
            for k, v in value.items():
                output.append(f"  {k}: {v}")
        elif isinstance(value, list):
            output.append(f"{key}: {', '.join(str(v) for v in value)}")
        else:
            output.append(f"{key}: {value}")

    if internal_links:
        output.append(f"internalLinksCount: {len(internal_links)}")
    if external_links:
        output.append(f"externalLinksCount: {len(external_links)}")
    if images:
        output.append(f"imagesCount: {len(images)}")

    output.append("---\n")
    output.append(markdown)

    if internal_links:
        output.append("\n\n---\n## Internal Links\n")
        for link in internal_links[:100]:
            output.append(f"- {link}")

    if external_links:
        output.append("\n\n---\n## External Links\n")
        for link in external_links[:50]:
            output.append(f"- {link}")

    if images:
        output.append("\n\n---\n## Images\n")
        for img in images[:50]:
            output.append(f"- {img}")

    return "\n".join(output)


@mcp.tool
def scrape(url: str) -> str:
    """Scrape a URL and return content with metadata, links, and images."""

    # Primary method (max 2 retries)
    for attempt in range(2):
        try:
            content, _ = _fetch_primary(url)
            if not _needs_fallback(content):
                return content
            break
        except Exception:
            if attempt < 1:
                time.sleep(5)
                continue
            break

    # Fallback method (max 3 retries)
    last_error = None
    for attempt in range(3):
        try:
            html, status_code = _fetch_fallback(url)

            # Check if response is a file download (binary content)
            is_binary, file_type = _is_binary_content(html)
            if is_binary:
                return _format_file_response(url, file_type)

            metadata, markdown, internal, external, images = _to_markdown(
                html, url, status_code
            )
            return _format_output(metadata, markdown, internal, external, images)

        except Exception as e:
            last_error = e
            if attempt < 2:
                time.sleep(5)

    raise Exception(f"Failed to scrape URL: {last_error}")


if __name__ == "__main__":
    mcp.run()
