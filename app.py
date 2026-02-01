import streamlit as st
import pandas as pd
import plotly.express as px
import pdfplumber

# 1. 페이지 기본 설정
st.set_page_config(page_title="Chef_dskim 통합 관리 시스템", layout="wide")

# 2. 사이드바 (시스템 상태 및 무결성)
with st.sidebar:
    st.header("🛡️ 시스템 무결성")
    st.success("통합 판독 엔진: 가동 중")
    st.info("오늘의 날짜: 2026-02-01")
    st.divider()
    st.header("⚙️ 제미(AI) 행동 강령")
    st.write("1. 엑셀 데이터 절대 엄수\n2. 팩트 기반 간결 보고")

st.title("👨‍🍳 MISOYON MMS 통합 관리")

# 3. 탭 구성 (경영, 레시피, 입고 순서)
tab1, tab2, tab3, tab4 = st.tabs(["📊 경영 대시보드", "📖 레시피 정밀 분석", "📸 스마트 입고", "📋 작업 리스트"])

# --- 탭 1: 경영 대시보드 (수익성 분포) ---
with tab1:
    st.subheader("메뉴별 수익성 분포 (Scatter Chart)")
    # 예시 데이터 (추후 엑셀 업로드 시 연동됨)
    sample_data = pd.DataFrame([
        {"메뉴명": "양념갈비", "원가율": 32.4, "마진": 15000},
        {"메뉴명": "차돌박이", "원가율": 45.1, "마진": 12500},
        {"메뉴명": "불고기", "원가율": 38.2, "마진": 9200}
    ])
    fig = px.scatter(sample_data, x="원가율", y="마진", text="메뉴명", size="마진", color="원가율")
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig, use_container_width=True)

# --- 탭 2: 레시피 정밀 분석 (이번에 추가된 통합 로직) ---
with tab2:
    st.subheader("📖 레시피 및 데이터 정밀 등록")
    uploaded_file = st.file_uploader("레시피 파일(XLSX, PDF, CSV)을 올려주세요", type=["xlsx", "pdf", "csv"])
    
    if uploaded_file:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        try:
            if file_ext == 'xlsx' or file_ext == 'csv':
                # 엑셀의 병합된 셀 등을 고려하여 데이터 로드
                df = pd.read_excel(uploaded_file, header=0) if file_ext == 'xlsx' else pd.read_csv(uploaded_file)
                st.success(f"✅ 엑셀 데이터 로드 성공")
                # 텅 빈 행/열은 제거하고 깔끔하게 보여줌
                clean_df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
                st.dataframe(clean_df, use_container_width=True)
                
            elif file_ext == 'pdf':
                with pdfplumber.open(uploaded_file) as pdf:
                    st.info("PDF 표 데이터를 추출합니다...")
                    all_tables = []
                    for page in pdf.pages:
                        table = page.extract_table()
                        if table:
                            df_pdf = pd.DataFrame(table[1:], columns=table[0])
                            all_tables.append(df_pdf)
                    
                    if all_tables:
                        for idx, t in enumerate(all_tables):
                            st.write(f"시트/페이지 {idx+1}")
                            st.table(t)
                    else:
                        st.warning("표 형식을 찾지 못했습니다. 텍스트로 표시합니다.")
                        st.text_area("원문 텍스트", pdf.pages[0].extract_text(), height=300)
            
            st.button("💾 분석된 데이터를 마스터 DB에 저장")
            
        except Exception as e:
            st.error(f"분석 중 오류 발생: {e}")

# --- 탭 3: 스마트 입고 ---
with tab3:
    st.header("📸 스마트 입고 (실시간 단가 대조)")
    col_cam, col_val = st.columns([1, 1])
    with col_cam:
        st.camera_input("명세표 촬영")
    with col_val:
        st.write("품목 선택 및 입고가 입력 로직 작동 중...")

# --- 탭 4: 작업 리스트 ---
with tab4:
    st.subheader("오늘의 작업 현황")
    for task in ["🍖 갈비 손질", "🥣 양념 제조", "🥬 야채 전처리"]:
        st.checkbox(task)
