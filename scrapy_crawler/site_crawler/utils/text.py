import re
from readability import Document

WS_RE = re.compile(r"[\t\r\f\v ]+")
NL_RE = re.compile(r"\n{3,}")


def extract_main_text(html: str, *, url: str = "") -> tuple[str, str]:
    """Return (title, text) from HTML.

    readability-lxml is used for main-content extraction.
    """
    doc = Document(html)
    title = (doc.short_title() or "").strip()
    summary_html = doc.summary(html_partial=True)

    # crude text extraction
    # (If you want more robust: use lxml.html to text_content)
    text = re.sub(r"<[^>]+>", "\n", summary_html)
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"&[a-zA-Z]+;", " ", text)

    text = text.strip()
    text = WS_RE.sub(" ", text)
    text = text.replace(" \n", "\n")
    text = NL_RE.sub("\n\n", text)

    return title, text
