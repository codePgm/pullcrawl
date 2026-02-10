"""URL normalization and validation utilities."""

from urllib.parse import urljoin, urlparse


def normalize_url(base_url: str, url: str) -> str:
    """Normalize URL to absolute URL."""
    return urljoin(base_url, url)


def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs are from the same domain."""
    return urlparse(url1).netloc == urlparse(url2).netloc


def is_same_path(url1: str, url2: str) -> bool:
    """Check if two URLs share the same base path."""
    path1 = '/'.join(urlparse(url1).path.split('/')[:-1]) + '/'
    path2_full = urlparse(url2).path
    return path2_full.startswith(path1)


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def extract_base_path(url: str) -> str:
    """Extract base path from URL (excluding filename)."""
    parsed = urlparse(url)
    return '/'.join(parsed.path.split('/')[:-1]) + '/'
