import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 및 레이아웃 설정
st.set_page_config(page_title="Chef_dskim 통합관리시스템", layout="wide")

# 2. 상단 헤더 및 내비게이션 (터치형 탭 구조)
# 셰프님이 원하신 '좌측 타이틀 + 옆으로 항목 배치'를 구현합니다.
st.markdown("### 👨‍🍳 Chef_dskim 통합관리시스템")

# 10가지 기능을 그룹핑하여 상단 메뉴로 배치
# 메인(타임테이블)을 가장 앞에 둡니다.
menu_tabs = st.tabs([
    "🕒 작업 타임테이블(Main)", 
    "📋 메뉴 & 레시피", 
    "🧪 R&D & 개발", 
    "💰 원가 & 자재", 
    "📸 입고 & 재고"
])

# --- [1번 탭: 중앙 메인 화면 - 작업 타임테이블] ---
with menu_tabs[0]:
    st.subheader(f"📅 오늘의 현장 오퍼레이션 ({datetime.now().strftime('%Y-%m-%d')})")
    
    # 타임테이블을 시각적으로 4단계로 구분
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("🌅 오전 오픈 준비 (09:00 ~ 11:30)")
        st.checkbox("육수 불 올리기 및 농도 체크")
        st.checkbox("입고 식자재 검수 (스마트 입고)")
        st.checkbox("채소류 전처리 (양파, 대파)")
        
    with col2:
        st.warning("🔥 런치 서비스 (11:30 ~ 14:30)")
        st.checkbox("점심 예약 4팀 세팅 확인")
        st.checkbox("갈비탕/육회 비빔밥 재료 소진 파악")
        
    with col3:
        st.success("🧪 브레이크 & R&D (14:30 ~ 17:00)")
        st.checkbox("신메뉴(불고기 소스) 테스트")
        st.checkbox("저녁 영업용 숯불 세팅")
        
    with col4:
        st.error("🌙 디너 서비스 & 마감 (17:00 ~ 22:00)")
        st.checkbox("저녁 단체(8인) 갈비 초벌")
        st.checkbox("당일 매출 정산 및 발주서 작성")
        st.checkbox("주방 위생 점검 및 소등")

# --- [나머지 탭은 구조만 잡아둡니다] ---
with menu_tabs[1]:
    st.write("### 📖 메뉴 등록/검색 및 레시피 데이터베이스")
    st.caption("이곳에서 메뉴를 검색하거나 등록합니다.")

with menu_tabs[2]:
    st.write("### 🧪 레시피 개발 및 멀티미디어 연동")
    st.caption("개발 중인 레시피와 유튜브/이미지 링크를 연결합니다.")

with menu_tabs[3]:
    st.write("### 💰 원가 계산 및 식재료 사용량 관리")
    st.caption("엑셀 데이터 기반 실시간 원가 산출 화면입니다.")

with menu_tabs[4]:
    st.write("### 📦 입고/재고/발주 총괄")
    st.caption("카메라 촬영(OCR) 및 재고 수량 체크 화면입니다.")
