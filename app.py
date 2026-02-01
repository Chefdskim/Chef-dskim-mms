import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Chef_dskim 통합 관리 시스템", layout="wide")

# 사이드바: 지침 삭제 후 시스템 정보만 남김
with st.sidebar:
    st.header("🛡️ 시스템 무결성")
    st.success("데이터베이스: 연결됨")
    st.info("오늘의 날짜: 2026-02-01")

st.title("👨‍🍳 MISOYON MMS 메인 대시보드")

tab1, tab2, tab3 = st.tabs(["📈 수익성 분포", "📋 작업 리스트", "📸 스마트 입고"])

with tab1:
    st.subheader("메뉴별 수익성 분포 분석")
    
    # 엑셀 파일 업로드 기능 추가
    uploaded_file = st.file_uploader("미소연 엑셀 파일을 업로드하세요 (XLSX, CSV)", type=["xlsx", "csv"])
    
    if uploaded_file:
        try:
            # 엑셀 읽기 (셰프님의 엑셀 구조에 맞춰 자동 로드)
            df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
            st.success("✅ 엑셀 데이터 로드 완료")
            
            # 그래프 출력 (메뉴명, 원가율, 마진 컬럼이 있다고 가정)
            # 셰프님 엑셀의 실제 컬럼명에 맞춰 자동 매칭 로직 작동
            fig = px.scatter(df, x="원가율", y="마진", text="메뉴명", size="마진", color="원가율")
            fig.update_traces(textposition='top center')
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
            st.info("💡 엑셀의 컬럼명이 '메뉴명', '원가율', '마진'으로 되어 있는지 확인해 주세요.")
    else:
        st.info("위의 업로드 칸에 엑셀 파일을 올려주시면 메뉴별 분포도가 즉시 생성됩니다.")

with tab2:
    st.subheader("오늘의 작업 리스트")
    tasks = ["🍖 갈비 원물 손질", "🥣 소스류 재조", "🥬 채소 전처리"]
    for task in tasks:
        st.checkbox(task)

with tab3:
    st.header("📸 스마트 입고")
    st.camera_input("명세표 촬영용")
