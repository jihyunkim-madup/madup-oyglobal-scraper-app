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
