# tests/test_scraper.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scraper import detect_url_type, extract_ga_code

def test_detect_ga_code():
    assert detect_url_type("GA240423305") == "ga_code"
    assert detect_url_type("ga240423305") == "ga_code"

def test_detect_product_url():
    assert detect_url_type(
        "https://global.oliveyoung.com/product/detail?prdtNo=GA240423305"
    ) == "product"

def test_detect_event_url():
    assert detect_url_type(
        "https://global.oliveyoung.com/event/planning?plndpNo=2353"
    ) == "event"

def test_detect_search_url():
    assert detect_url_type(
        "https://global.oliveyoung.com/display/search?query=Niacinamide"
    ) == "search"

def test_detect_unknown():
    assert detect_url_type("https://example.com/whatever") == "unknown"
    assert detect_url_type("not-a-url") == "unknown"
    assert detect_url_type("") == "unknown"

def test_extract_ga_code_from_direct():
    assert extract_ga_code("GA240423305") == "GA240423305"
    assert extract_ga_code("ga240423305") == "GA240423305"

def test_extract_ga_code_from_url():
    assert extract_ga_code(
        "https://global.oliveyoung.com/product/detail?prdtNo=GA240423305"
    ) == "GA240423305"

def test_extract_ga_code_fails_gracefully():
    assert extract_ga_code("https://example.com/no-ga-code") == ""
    assert extract_ga_code("not-a-url") == ""

def test_detect_url_type_with_whitespace():
    assert detect_url_type("  GA240423305  ") == "ga_code"


from scraper import fetch_product

def test_fetch_product_returns_correct_keys():
    result = fetch_product("GA240423305")
    assert set(result.keys()) == {
        "product_code", "product_name", "main_image_url", "product_url", "source_url"
    }

def test_fetch_product_values():
    result = fetch_product("GA240423305")
    assert result["product_code"] == "GA240423305"
    assert len(result["product_name"]) > 0
    assert result["main_image_url"].startswith("https://")
    assert "prdtNo=GA240423305" in result["product_url"]
    assert result["source_url"] == ""  # 기본값은 빈 문자열


from scraper import fetch_event, fetch_search


def test_fetch_search_returns_list():
    results = fetch_search("Niacinamide", max_results=10)
    assert isinstance(results, list)
    assert len(results) > 0


def test_fetch_search_item_keys():
    results = fetch_search("Niacinamide", max_results=5)
    item = results[0]
    assert set(item.keys()) == {
        "product_code", "product_name", "main_image_url", "product_url", "source_url"
    }


def test_fetch_search_max_results():
    results = fetch_search("Niacinamide", max_results=10)
    assert len(results) <= 10


def test_fetch_event_returns_list():
    results = fetch_event("2353")
    assert isinstance(results, list)
    assert len(results) > 0

def test_fetch_event_item_keys():
    results = fetch_event("2353")
    item = results[0]
    assert set(item.keys()) == {
        "product_code", "product_name", "main_image_url", "product_url", "source_url"
    }

def test_fetch_event_item_values():
    results = fetch_event("2353")
    item = results[0]
    assert item["product_code"].startswith("GA")
    assert item["source_url"] == ""


from scraper import extract_from_input

def test_extract_from_ga_code():
    results = extract_from_input("GA240423305")
    assert len(results) == 1
    assert results[0]["product_code"] == "GA240423305"
    assert results[0]["source_url"] == "GA240423305"  # 첫 번째 항목에만 source_url

def test_extract_from_product_url():
    url = "https://global.oliveyoung.com/product/detail?prdtNo=GA240423305"
    results = extract_from_input(url)
    assert len(results) == 1
    assert results[0]["source_url"] == url

def test_extract_from_event_url():
    url = "https://global.oliveyoung.com/event/planning?plndpNo=2353"
    results = extract_from_input(url)
    assert len(results) > 1  # 기획전은 다건
    assert results[0]["source_url"] == url
    assert results[1]["source_url"] == ""  # 두 번째부터는 빈 문자열

def test_extract_unknown_input():
    results = extract_from_input("https://example.com/unknown")
    assert len(results) == 1
    assert results[0]["product_code"] == "❌ 인식불가"
