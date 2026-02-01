import streamlit as st
import pandas as pd
import plotly.express as px
import pdfplumber

# 1. 페이지 설정
st.set_page_config(page_title="Chef_dskim MMS", layout="wide")

# 2. 사이드바 (핵심 지표만 노출)
with st.sidebar:
    st.header("📊 시스템 상태")
    st.success("데이터 엔진: 가동 중")
    st.info("오늘의 날짜: 2026-02-01")

st.title("👨‍🍳 MISOYON 통합 관리 시스템")

# 3. 탭 구성: 실무 흐름에 맞춰 재조립
tab1, tab2, tab3, tab4 = st.tabs(["📈 수익성 대시보드", "📖 레시피 마스터", "📸 스마트 입고", "📋 공정 리스트"])

# --- 탭 1: 경영 대시보드 (메뉴별 수익성) ---
with tab1:
    st.subheader("메뉴별 수익성 분포")
    # 셰프님의 실제 데이터와 연동될 그래프
    sample_data = pd.DataFrame([
        {"메뉴명": "양념갈비", "원가율": 32.4, "마진": 15000},
        {"메뉴명": "차돌박이", "원가율": 45.1, "마진": 12500},
        {"메뉴명": "불고기", "원가율": 38.2, "마진": 9200},
        {"메뉴명": "갈비탕", "원가율": 28.7, "마진": 6800}
    ])
    fig = px.scatter(sample_data, x="원가율", y="마진", text="메뉴명", size="마진", color="원가율",
                     labels={"원가율": "원가율 (%)", "마진": "마진액 (원)"})
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig, use_container_width=True)

# --- 탭 2: 레시피 마스터 (데이터 판독) ---
with tab2:
    st.subheader("레시피 및 엑셀 데이터 등록")
    uploaded_file = st.file_uploader("파일 업로드 (XLSX, PDF, CSV)", type=["xlsx", "pdf", "csv"])
    
    if uploaded_file:
        ext = uploaded_file.name.split('.')[-1]
        try:
            if ext in ['xlsx', 'csv']:
                df = pd.read_excel(uploaded_file) if ext == 'xlsx' else pd.read_csv(uploaded_file)
                st.dataframe(df.dropna(how='all', axis=1), use_container_width=True)
            elif ext == 'pdf':
                with pdfplumber.open(uploaded_file) as pdf:
                    table = pdf.pages[0].extract_table()
                    if table:
                        st.table(pd.DataFrame(table[1:], columns=table[0]))
                    else:
                        st.text(pdf.pages[0].extract_text())
            st.button("💾 데이터베이스에 동기화")
        except Exception as e:
            st.error(f"파일 판독 오류: {e}")

# --- 탭 3: 스마트 입고 (실시간 원가) ---
with tab3:
    st.header("📸 입고 명세서 검증")
    c1, c2 = st.columns(2)
    with c1:
        st.camera_input("명세표 촬영")
    with c2:
        st.write("### 실시간 단가 변동 확인")
        st.info("촬영 시 엑셀 기준가와 대조하여 변동폭을 표시합니다.")

# --- 탭 4: 공정 리스트 (체크리스트) ---
with tab4:
    st.subheader("오늘의 주방 공정")
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("🍖 육류 원물 손질")
        st.checkbox("🥣 대용량 양념 제조")
    with col2:
        st.checkbox("🥬 채소 전처리 및 소분")
        st.checkbox("📊 원가 보고서 확인")
