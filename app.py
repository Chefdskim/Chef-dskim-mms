import streamlit as st
import pandas as pd
import pdfplumber # PDF 추출을 위해 추가 (requirements.txt 수정 필요)

st.set_page_config(page_title="Chef_dskim 통합 관리 시스템", layout="wide")

# 사이드바 설정
with st.sidebar:
    st.header("🛡️ 시스템 상태")
    st.success("레시피 엔진: 가동 중")
    st.info("데이터 무결성: 147종 대조 준비 완료")

st.title("👨‍🍳 Chef_dskim 레시피 및 데이터 관리")

# 탭 구성 변경: 레시피 등록을 가장 앞으로 배치
tab1, tab2, tab3 = st.tabs(["📖 레시피 등록 및 분석", "📈 수익성 분석", "📸 스마트 입고"])

with tab1:
    st.subheader("신규 레시피 및 식자재 명세서 등록")
    uploaded_file = st.file_uploader("레시피 파일(XLSX, PDF, CSV)을 올려주세요", type=["xlsx", "pdf", "csv"])
    
    if uploaded_file:
        file_type = uploaded_file.name.split('.')[-1]
        
        try:
            if file_type == 'xlsx' or file_type == 'csv':
                # 엑셀/CSV 읽기
                df = pd.read_excel(uploaded_file) if file_type == 'xlsx' else pd.read_csv(uploaded_file)
                st.success(f"✅ 엑셀 레시피 로드 성공: {uploaded_file.name}")
                st.dataframe(df, use_container_width=True) # 데이터 확인용 표 출력
                
            elif file_type == 'pdf':
                # PDF 텍스트 추출 로직
                with pdfplumber.open(uploaded_file) as pdf:
                    content = ""
                    for page in pdf.pages:
                        content += page.extract_text()
                st.success(f"✅ PDF 레시피 인식 성공: {uploaded_file.name}")
                st.text_area("PDF 추출 내용", content, height=300)
                
            st.button("💾 이 레시피를 마스터 DB에 저장")
            
        except Exception as e:
            st.error(f"파일 분석 중 오류가 발생했습니다: {e}")

with tab2:
    st.subheader("메뉴별 수익성 분포")
    st.info("등록된 레시피와 입고가를 대조하여 수익성을 계산합니다.")
    # (이전의 Scatter Chart 로직이 여기로 연결됩니다)

with tab3:
    st.header("📸 스마트 입고")
    st.camera_input("입고 명세표 촬영")
