# app.py
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

from scraper import extract_from_input

st.set_page_config(
    page_title="OY Global 스크래퍼",
    page_icon="🛒",
    layout="wide",
)

st.title("🛒 OY Global 상품 스크래퍼")
st.caption("올리브영 글로벌 URL 또는 GA코드 → 상품 데이터 추출")


def render_results(rows: list[dict]) -> None:
    """결과 테이블 + CSV 다운로드 + 클립보드 복사 버튼을 렌더링한다."""
    if not rows:
        st.warning("추출된 상품이 없습니다.")
        return

    df = pd.DataFrame(rows, columns=[
        "product_code", "product_name", "main_image_url", "product_url", "source_url"
    ])
    st.success(f"✅ {len(df)}건 추출 완료")
    st.dataframe(df, use_container_width=True, hide_index=True)

    col1, col2 = st.columns([1, 1])

    # CSV 다운로드
    filename = f"oy_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with col1:
        st.download_button(
            label="📥 CSV 다운로드",
            data=df.to_csv(index=False, encoding="utf-8-sig"),
            file_name=filename,
            mime="text/csv",
        )

    # 클립보드 복사 (탭 구분 → 구글 시트 붙여넣기 가능)
    with col2:
        tsv = df.to_csv(sep="\t", index=False)
        tsv_escaped = tsv.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
        components.html(
            f"""
            <button
                onclick="navigator.clipboard.writeText(`{tsv_escaped}`)
                    .then(()=>{{ this.textContent='✅ 복사됨!'; setTimeout(()=>this.textContent='📋 클립보드 복사',2000); }})
                    .catch(()=>alert('복사 실패 — HTTPS 환경에서만 동작합니다'))"
                style="padding:8px 16px;background:#ff4b4b;color:white;border:none;
                       border-radius:4px;cursor:pointer;font-size:14px;width:100%;">
                📋 클립보드 복사
            </button>
            """,
            height=50,
        )


# ── 탭 ────────────────────────────────────────────────
tab_single, tab_multi = st.tabs(["단건", "다건"])

with tab_single:
    st.subheader("URL 또는 GA코드 단건 입력")
    single_input = st.text_input(
        label="입력",
        placeholder="GA240423305  또는  https://global.oliveyoung.com/product/detail?prdtNo=GA...",
        label_visibility="collapsed",
    )
    if st.button("추출", key="btn_single", type="primary") and single_input.strip():
        with st.spinner("추출 중..."):
            rows = extract_from_input(single_input.strip())
        render_results(rows)

with tab_multi:
    pass  # Task 8에서 구현
