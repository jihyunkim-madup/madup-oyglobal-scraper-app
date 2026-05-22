# OY Global 스크래퍼

올리브영 글로벌 URL / GA코드 → 상품 데이터 추출 → CSV 다운로드 / 클립보드 복사

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 지원 입력 형태

- GA코드: `GA240423305`
- 상품 상세 URL: `https://global.oliveyoung.com/product/detail?prdtNo=GA240423305`
- 기획전 URL: `https://global.oliveyoung.com/event/planning?plndpNo=2353`
- 검색 URL: `https://global.oliveyoung.com/display/search?query=Niacinamide`
