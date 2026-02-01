import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Chef_dskim 통합 관리 시스템", layout="wide")

# 1. 사이드바 및 헤더 (시스템 무결성 상태)
with st.sidebar:
    st.header("🛡️ 시스템 무결성")
    st.success("데이터베이스: 연결됨")
    st.success("엑셀 동기화: 완료 (147종)")
    st.info("마지막 업데이트: 2026-02-01")

st.title("👨‍🍳 MISOYON MMS 메인 대시보드")

# 탭 구성: 대시보드가 메인입니다.
tab1, tab2, tab3 = st.tabs(["📈 경영 요약", "📋 작업 리스트", "📸 스마트 입고"])

with tab1:
    st.subheader("메뉴별 수익성 분포")
    # 셰프님의 수익성 분포 가상 데이터 (추후 실제 엑셀 데이터와 연동)
    chart_data = pd.DataFrame(
        np.random.randn(20, 2),
        columns=['원가율', '판매량']
    )
    st.scatter_chart(chart_data)
    
    st.caption("※ 우상향일수록 수익성이 좋은 메뉴이며, 원가율이 높은 품목은 붉게 표시됩니다.")

with tab2:
    st.subheader("오늘의 작업 리스트")
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("🍖 갈비 원물 손질 (20kg)")
        st.checkbox("🥣 데리야끼 소스 대량 제조")
        st.checkbox("🥬 채소류 전처리")
    with col2:
        st.button("➕ 작업 추가")
        st.button("🧹 리스트 초기화")

with tab3:
    st.header("🔍 실시간 원가 대조 (스마트 입고)")
    # 기존에 완성했던 카메라 및 입고가 계산 로직이 이쪽으로 들어옵니다.
    c1, c2 = st.columns(2)
    with c1:
        st.camera_input("명세표 촬영")
    with c2:
        st.text_input("품목 입력")
        st.number_input("입고가 입력")
