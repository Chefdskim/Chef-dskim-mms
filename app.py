import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="Chef_dskim 통합관리시스템", layout="wide")

# 2. 세션 상태 초기화 (앱에서 직접 수정하기 위한 메모리 공간)
# 셰프님이 앱을 껐다 켜도 기본 틀은 유지되되, 내용은 마음대로 바꿀 수 있습니다.
if 'tasks' not in st.session_state:
    st.session_state.tasks = {
        "오전": ["육수 불 올리기", "입고 식자재 검수", "채소류 전처리"],
        "런치": ["예약석 세팅 확인", "재료 소진 파악"],
        "브레이크": ["신메뉴 테스트", "디너 숯불 세팅"],
        "디너": ["갈비 초벌 작업", "마감 정산"]
    }

# 사이드바
with st.sidebar:
    st.header("📊 시스템 상태")
    st.success("오퍼레이션 모드: 수정 가능")
    st.info(f"오늘 날짜: {datetime.now().strftime('%Y-%m-%d')}")

# 헤더
st.markdown("### 👨‍🍳 Chef_dskim 통합관리시스템")

# 탭 메뉴
menu_tabs = st.tabs([
    "🕒 작업 타임테이블(Main)", 
    "📋 메뉴 & 레시피", 
    "🧪 R&D & 개발", 
    "💰 원가 & 자재", 
    "📸 입고 & 재고"
])

# --- [메인: 현장 오퍼레이션 (수정 가능 버전)] ---
with menu_tabs[0]:
    st.subheader(f"📅 오늘의 현장 오퍼레이션 (터치하여 체크/수정)")

    # 4분할 레이아웃
    col1, col2, col3, col4 = st.columns(4)
    
    # 시간대별 표시 및 수정 함수
    def task_column(column, time_key, title, color_icon):
        with column:
            st.markdown(f"#### {color_icon} {title}")
            
            # 1. 기존 할 일 리스트 출력 (체크박스)
            for idx, task in enumerate(st.session_state.tasks[time_key]):
                # 체크박스와 삭제 버튼을 나란히 배치
                c_check, c_del = st.columns([0.8, 0.2])
                c_check.checkbox(task, key=f"{time_key}_{idx}")
                if c_del.button("X", key=f"del_{time_key}_{idx}"):
                    st.session_state.tasks[time_key].pop(idx)
                    st.rerun() # 즉시 새로고침하여 반영
            
            # 2. 새로운 작업 추가 (입력창 + 버튼)
            with st.expander("➕ 작업 추가"):
                new_task = st.text_input(f"{title} 할 일 입력", key=f"input_{time_key}")
                if st.button("등록", key=f"add_{time_key}"):
                    if new_task:
                        st.session_state.tasks[time_key].append(new_task)
                        st.rerun()

    # 각 컬럼에 적용
    task_column(col1, "오전", "오전 오픈 (09:00~)", "🌅")
    task_column(col2, "런치", "런치 서비스 (11:30~)", "🔥")
    task_column(col3, "브레이크", "R&D / 준비 (14:30~)", "🧪")
    task_column(col4, "디너", "디너 / 마감 (17:00~)", "🌙")

# --- [나머지 탭 (구조 유지)] ---
with menu_tabs[1]:
    st.write("메뉴 관리 화면 준비 중")
with menu_tabs[2]:
    st.write("R&D 화면 준비 중")
with menu_tabs[3]:
    st.write("원가 관리 화면 준비 중")
with menu_tabs[4]:
    st.write("재고 관리 화면 준비 중")
