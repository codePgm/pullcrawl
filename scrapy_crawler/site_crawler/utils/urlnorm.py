from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode

TRACKING_PREFIXES = ("utm_",)
TRACKING_KEYS = {"gclid", "fbclid", "igshid", "mc_cid", "mc_eid"}


def normalize_url(base_url: str, href: str, *, strip_tracking: bool = True) -> str | None:
    if not href:
        return None
    href = href.strip()
    # Skip non-http(s)
    if href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
        return None

    abs_url = urljoin(base_url, href)
    parts = urlsplit(abs_url)

    if parts.scheme not in ("http", "https"):
        return None

    # Drop fragment
    fragmentless = parts._replace(fragment="")

    # Normalize query
    if strip_tracking and fragmentless.query:
        q = []
        for k, v in parse_qsl(fragmentless.query, keep_blank_values=True):
            if k in TRACKING_KEYS:
                continue
            if any(k.startswith(p) for p in TRACKING_PREFIXES):
                continue
            q.append((k, v))
        q.sort()
        fragmentless = fragmentless._replace(query=urlencode(q, doseq=True))

    # Normalize trailing slash: keep as-is (optional)
    return urlunsplit(fragmentless)
