# scraper.py
import re
import requests
from urllib.parse import urlparse, parse_qs

CDN_BASE = "https://cdn-image.oliveyoung.com/"
_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://global.oliveyoung.com/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
}


def detect_url_type(text: str) -> str:
    """입력 텍스트의 URL 유형을 반환한다."""
    s = text.strip()
    if not s:
        return "unknown"
    if re.match(r'^GA\d{9}$', s, re.IGNORECASE):
        return "ga_code"
    try:
        parsed = urlparse(s)
        qs = parse_qs(parsed.query)
        path = parsed.path
    except Exception:
        return "unknown"
    if "/product/detail" in path or "prdtNo" in qs:
        return "product"
    if "/event/planning" in path or "plndpNo" in qs:
        return "event"
    if "/display/search" in path or "query" in qs:
        return "search"
    return "unknown"


def extract_ga_code(text: str) -> str:
    """URL 또는 GA코드 문자열에서 GA코드만 추출한다."""
    s = text.strip()
    if re.match(r'^GA\d{9}$', s, re.IGNORECASE):
        return s.upper()
    parsed = urlparse(s)
    qs = parse_qs(parsed.query)
    if "prdtNo" in qs:
        return qs["prdtNo"][0]
    m = re.search(r'(GA\d{9})', s, re.IGNORECASE)
    return m.group(1).upper() if m else s
