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
    """URL 또는 GA코드 문자열에서 GA코드만 추출한다.

    GA코드를 찾지 못하면 빈 문자열("")을 반환한다.
    """
    s = text.strip()
    if re.match(r'^GA\d{9}$', s, re.IGNORECASE):
        return s.upper()
    parsed = urlparse(s)
    qs = parse_qs(parsed.query)
    if "prdtNo" in qs:
        return qs["prdtNo"][0]
    m = re.search(r'(GA\d{9})', s, re.IGNORECASE)
    return m.group(1).upper() if m else ""


def fetch_product(ga_code: str) -> dict:
    """GA코드로 단건 상품 데이터를 조회한다."""
    resp = requests.post(
        "https://global.oliveyoung.com/product/detail-data",
        json={"prdtNo": ga_code},
        headers=_HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    p = resp.json().get("product", {})
    img_path = p.get("imagePath", "")
    return {
        "product_code": p.get("prdtNo", ga_code),
        "product_name": p.get("prdtNameEn", ""),
        "main_image_url": f"{CDN_BASE}{img_path}" if img_path else "",
        "product_url": f"https://global.oliveyoung.com/product/detail?prdtNo={ga_code}",
        "source_url": "",
    }


def fetch_event(plndp_no: str) -> list[dict]:
    """기획전 번호로 전체 상품 목록을 조회한다."""
    form_data = (
        f"plndpNo={plndp_no}&langCode=en&curLangCode=en"
        f"&acesCntryCode=00&mrgnCntryCode=9999&dlvCntryCode=1230"
    )
    resp = requests.post(
        "https://global.oliveyoung.com/event/read-plndp-list",
        data=form_data,
        headers={**_HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    resp.raise_for_status()
    products = resp.json().get("result", [])
    result = []
    for p in products:
        ga_code = p.get("prdtNo", "")
        img_path = p.get("prdtImagePath", "")
        result.append({
            "product_code": ga_code,
            "product_name": p.get("prdtName", ""),
            "main_image_url": f"{CDN_BASE}{img_path}" if img_path else "",
            "product_url": f"https://global.oliveyoung.com/product/detail?prdtNo={ga_code}",
            "source_url": "",
        })
    return result


def fetch_search(query: str, max_results: int = 100) -> list[dict]:
    """검색어로 상품 목록을 조회한다. max_results개까지 수집."""
    SEARCH_URL = "https://global.oliveyoung.com/display/search/product-list"
    ROWS_PER_PAGE = min(max_results, 24)
    collected = []
    page = 1

    while len(collected) < max_results:
        payload = {
            "query": query,
            "sort": "10",
            "pageNum": page,
            "rowsPerPage": ROWS_PER_PAGE,
            "brandNoList": [],
            "ctgrNoList": [],
            "eventSlprcDscntRt": [],
            "reviewScore": [],
            "attrValNoList": {},
        }
        resp = requests.post(
            SEARCH_URL,
            json=payload,
            headers=_HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        hits = data.get("search", {}).get("hits", {})
        total = hits.get("found", 0)
        hit_list = hits.get("hit", [])

        if not hit_list:
            break

        for item in hit_list:
            fields = item.get("fields", {})
            ga_code = fields.get("prdtNo", "")
            img_path = fields.get("imagePath", "")
            collected.append({
                "product_code": ga_code,
                "product_name": fields.get("prdtName", ""),
                "main_image_url": f"{CDN_BASE}{img_path}" if img_path else "",
                "product_url": f"https://global.oliveyoung.com/product/detail?prdtNo={ga_code}",
                "source_url": "",
            })
            if len(collected) >= max_results:
                break

        if len(collected) >= total or total == 0:
            break
        page += 1

    return collected


def extract_from_input(text: str) -> list[dict]:
    """URL 또는 GA코드 하나를 받아 상품 목록을 반환한다.

    - 첫 번째 항목의 source_url에만 원본 입력값을 기록한다.
    - 인식 불가 입력은 오류 행 하나를 반환한다.
    """
    source = text.strip()
    url_type = detect_url_type(source)

    try:
        if url_type == "ga_code":
            items = [fetch_product(source.upper())]
        elif url_type == "product":
            items = [fetch_product(extract_ga_code(source))]
        elif url_type == "event":
            plndp_no = parse_qs(urlparse(source).query).get("plndpNo", [""])[0]
            items = fetch_event(plndp_no)
        elif url_type == "search":
            query = parse_qs(urlparse(source).query).get("query", [""])[0]
            items = fetch_search(query)
        else:
            return [{
                "product_code": "❌ 인식불가",
                "product_name": source,
                "main_image_url": "",
                "product_url": "",
                "source_url": source,
            }]
    except Exception as e:
        return [{
            "product_code": "❌ 응답없음",
            "product_name": str(e),
            "main_image_url": "",
            "product_url": "",
            "source_url": source,
        }]

    # source_url은 첫 번째 항목에만
    if items:
        items[0]["source_url"] = source
    return items
