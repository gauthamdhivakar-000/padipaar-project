"""Turns text / URL / PDF input into a clean list of clauses."""
import io
import ipaddress
import re
import socket
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

MAX_CHARS = 200_000
MAX_CLAUSES = 600
MAX_DOWNLOAD_BYTES = 3_000_000
USER_AGENT = "PadiPaarBot/1.0 (student project; reads public terms pages)"


class InputError(ValueError):
    """Raised for problems the user can fix (shown as HTTP 400)."""


# ----------------------------------------------------------------- text
def clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


_SPLIT = re.compile(r"(?<=[.;:!?])\s+(?=[A-Z0-9(\"'\u201c])|\n(?=\s*(?:\d+[.)]|[a-z][.)]|[-\u2022*])\s)")


def split_clauses(text: str):
    """Split a document into clauses (sentences / numbered items)."""
    text = clean_text(text)
    clauses = []
    for part in _SPLIT.split(text):
        part = re.sub(r"\s+", " ", part).strip()
        if len(part) < 40:
            continue
        if len(part) > 1200:
            pieces = [p.strip() for p in re.split(r";|\. ", part) if len(p.strip()) >= 40]
            clauses.extend(pieces)
        else:
            clauses.append(part)
    # remove exact duplicates but keep order
    seen, unique = set(), []
    for c in clauses:
        key = c.lower()
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique[:MAX_CLAUSES]


# ----------------------------------------------------------------- html
def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "form"]):
        tag.decompose()
    return soup.get_text("\n")


# ----------------------------------------------------------------- url safety
def _is_public_ip(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    return not (addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_multicast
                or addr.is_reserved or addr.is_unspecified)


def check_url_is_safe(url: str) -> str:
    """Block non-http(s) URLs and anything that resolves to a private address (SSRF guard)."""
    url = (url or "").strip()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise InputError("Please enter a full web address starting with http:// or https://")
    if parsed.port not in (None, 80, 443):
        raise InputError("Only standard web ports are allowed.")
    try:
        infos = socket.getaddrinfo(parsed.hostname, parsed.port or 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        raise InputError("Could not find that website. Please check the address or paste the text instead.")
    for info in infos:
        if not _is_public_ip(info[4][0]):
            raise InputError("That address is not allowed.")
    return url


def fetch_url_text(url: str) -> str:
    """Download a public page (max 3 redirects, size-limited) and return its readable text."""
    current = check_url_is_safe(url)
    for _ in range(4):
        try:
            resp = requests.get(current, timeout=12, allow_redirects=False, stream=True,
                                headers={"User-Agent": USER_AGENT})
        except requests.RequestException:
            raise InputError("Could not open that page. Please paste the text instead.")
        if resp.is_redirect or resp.status_code in (301, 302, 303, 307, 308):
            nxt = resp.headers.get("Location")
            resp.close()
            if not nxt:
                raise InputError("The page redirected badly. Please paste the text instead.")
            current = check_url_is_safe(urljoin(current, nxt))
            continue
        if resp.status_code >= 400:
            resp.close()
            raise InputError("The website refused the request (HTTP %d). Please paste the text instead." % resp.status_code)
        data = b""
        for chunk in resp.iter_content(65536):
            data += chunk
            if len(data) > MAX_DOWNLOAD_BYTES:
                break
        ctype = resp.headers.get("Content-Type", "").lower()
        resp.close()
        if "pdf" in ctype:
            return pdf_to_text(data)
        encoding = resp.encoding or "utf-8"
        try:
            html = data.decode(encoding, errors="replace")
        except LookupError:
            html = data.decode("utf-8", errors="replace")
        text = html_to_text(html)
        if len(clean_text(text)) < 200:
            raise InputError("This page has too little readable text (it may need JavaScript). "
                             "Please paste the text instead.")
        return text
    raise InputError("Too many redirects. Please paste the text instead.")


# ----------------------------------------------------------------- pdf
def pdf_to_text(data: bytes) -> str:
    import pdfplumber
    pages = []
    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages[:80]:
                pages.append(page.extract_text() or "")
    except Exception:
        raise InputError("Could not read that PDF file.")
    text = "\n".join(pages).strip()
    if len(text) < 50:
        raise InputError("No readable text found in the PDF (it may be a scanned image). "
                         "Please paste the text instead.")
    return text
