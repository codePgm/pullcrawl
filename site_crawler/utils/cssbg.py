import re
from typing import Iterable

# background-image: url("...") or url(...)
URL_RE = re.compile(r"url\((?P<q>['\"]?)(?P<u>.*?)(?P=q)\)", re.IGNORECASE)


def extract_urls_from_css_text(css_text: str) -> list[str]:
    out = []
    for m in URL_RE.finditer(css_text or ""):
        u = (m.group("u") or "").strip()
        if not u:
            continue
        # Skip data URIs by default (can be huge)
        if u.startswith("data:"):
            continue
        out.append(u)
    return out


def unique(seq: Iterable[str]) -> list[str]:
    seen = set()
    out = []
    for x in seq:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out
