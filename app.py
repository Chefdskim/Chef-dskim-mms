import streamlit as st
import pandas as pd

# 셰프님 마스터 데이터 (임시 데이터 - 추후 data.json 연동)
master_ingredients = {
    "갈비(원물)": {"price": 13000, "yield": 50.4},
    "차돌박이": {"price": 18000, "yield": 100},
    "쪽파(실파)": {"price": 4500, "yield": 85}
}

st.set_page_config(page_title="Chef_dskim MMS", layout="wide")
st.title("👨‍🍳 Chef_dskim 통합 관리 시스템")

tab1, tab2, tab3 = st.tabs(["📸 스마트 입고", "📊 수익성 분포", "📋 작업 리스트"])

with tab1:
    st.header("식자재 명세표 등록")
    img_file = st.camera_input("명세표를 촬영하세요")
    if img_file:
        st.info("비전 AI 분석 중... (테스트: 갈비 단가 상승 상황)")
        # 시뮬레이션 결과
        st.warning("⚠️ 갈비(원물) 단가 변동 감지: 13,000원 -> 14,500원 (+11.5%)")
        if st.button("신규 단가 승인 및 전체 레시피 반영"):
            st.success("147종 레시피 원가가 최신화되었습니다.")

with tab2:
    st.header("메뉴별 수익성 분포")
    st.info("판매 데이터 대기 중...")

with tab3:
    st.header("오늘의 준비 작업 리스트")
    st.checkbox("차돌박이 10kg 손질 및 유자 제스트 전처리")
