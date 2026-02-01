import streamlit as st
import pandas as pd
from datetime import datetime, time

# 1. 페이지 설정
st.set_page_config(page_title="Chef_dskim 통합관리시스템", layout="wide")

# --- [데이터베이스] 1. 카테고리 구조 (책장) ---
CATEGORY_TREE = {
    "🇰🇷 한식": ["국/찌개/전골/탕", "찜", "구이", "조림", "볶음", "무침/나물", "김치/장류", "밥/죽/면"],
    "🇯🇵 일식": ["사시미/스시", "구이(야키)", "튀김(아게)", "찜(무시)", "조림(니모노)", "면류(라멘/소바)", "돈부리"],
    "🇨🇳 중식": ["튀김/볶음", "탕/찜", "냉채", "면류", "만두/딤섬"],
    "🍝 양식": ["에피타이저", "파스타", "스테이크/메인", "스튜/수프", "샐러드"],
    "🍞 베이커리": ["제빵(Bread)", "제과(Cake/Cookie)", "디저트", "샌드위치"],
    "🍷 주류/음료": ["와인", "사케", "전통주", "칵테일", "커피/음료"],
    "📦 기타": ["소스/드레싱", "가니쉬", "향신료 배합", "이유식/환자식"]
}

# --- [데이터베이스] 2. 오퍼레이션 기본값 ---
DAILY_ROUTINE = [
    {"start": time(9, 0), "end": time(9, 30), "cat": "Prep", "task": "오픈 준비 (환기, 조명, 식자재 검수)", "point": "냉장고 온도 확인", "done": False},
    {"start": time(21, 30), "end": time(22, 0), "cat": "Clean", "task": "주방 마감 청소 및 발주", "point": "가스 밸브 잠금 확인", "done": False}
]

# 2. 세션 상태 초기화
# (1) 내비게이션 상태
if 'nav_depth' not in st.session_state:
    st.session_state.nav_depth = 0 
if 'selected_main' not in st.session_state:
    st.session_state.selected_main = ""
if 'selected_sub' not in st.session_state:
    st.session_state.selected_sub = ""

# (2) 타임테이블 데이터
if 'schedule_df' not in st.session_state:
    df = pd.DataFrame(DAILY_ROUTINE)
    df.columns = ["시작 시간", "종료 시간", "구분", "세부 작업 내용", "체크 포인트", "완료"]
    st.session_state.schedule_df = df

# 사이드바
with st.sidebar:
    st.header("📊 시스템 상태")
    st.info(f"오늘: {datetime.now().strftime('%Y-%m-%d')}")
    st.divider()
    if st.button("🏠 메뉴 홈으로 (초기화)"):
        st.session_state.nav_depth = 0
        st.session_state.selected_main = ""
        st.session_state.selected_sub = ""
        st.rerun()

st.title("👨‍🍳 MISOYON 통합 관리 시스템")

# 탭 메뉴 구성
menu_tabs = st.tabs(["⏱️ 오퍼레이션(Main)", "📖 메뉴 & 레시피", "🧪 R&D", "💰 원가", "📸 입고"])

# =========================================================
# [TAB 1] 현장 오퍼레이션 (타임테이블)
# =========================================================
with menu_tabs[0]:
    st.subheader("📅 현장 오퍼레이션 & 타임테이블")
    
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.caption("💡 시간과 내용을 클릭하여 수정하세요. (행 추가 가능)")
    with col2:
        if st.button("🔄 일정 초기화"):
            df = pd.DataFrame(DAILY_ROUTINE)
            df.columns = ["시작 시간", "종료 시간", "구분", "세부 작업 내용", "체크 포인트", "완료"]
            st.session_state.schedule_df = df
            st.rerun()

    # 데이터 에디터
    edited_df = st.data_editor(
        st.session_state.schedule_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "시작 시간": st.column_config.TimeColumn("Start", format="HH:mm"),
            "종료 시간": st.column_config.TimeColumn("End", format="HH:mm"),
            "구분": st.column_config.SelectboxColumn("Cat", options=["Prep", "Cooking", "Service", "Clean", "R&D"]),
            "세부 작업 내용": st.column_config.TextColumn("Task", width="large"),
            "체크 포인트": st.column_config.TextColumn("Check Point", width="medium"),
            "완료": st.column_config.CheckboxColumn("Done", default=False)
        },
        hide_index=True
    )
    st.session_state.schedule_df = edited_df

    # 진행률 표시
    total = len(edited_df)
    done = edited_df["완료"].sum()
    if total > 0:
        st.progress(done/total, text=f"금일 공정 진행률: {int(done/total*100)}%")

# =========================================================
# [TAB 2] 메뉴 & 레시피 (책장형 내비게이션)
# =========================================================
with menu_tabs[1]:
    
    # [Level 0] 대분류 책장
    if st.session_state.nav_depth == 0:
        st.subheader("📚 레시피 라이브러리 (Category)")
        cols = st.columns(4)
        for idx, category in enumerate(CATEGORY_TREE.keys()):
            with cols[idx % 4]:
                if st.button(f"\n{category}\n\n📂 열기", key=f"main_{idx}", use_container_width=True):
                    st.session_state.selected_main = category
                    st.session_state.nav_depth = 1
                    st.rerun()

    # [Level 1] 중분류 목차
    elif st.session_state.nav_depth == 1:
        c1, c2 = st.columns([0.1, 0.9])
        with c1:
            if st.button("⬅️", help="책장으로"):
                st.session_state.nav_depth = 0
                st.rerun()
        with c2:
            st.subheader(f"{st.session_state.selected_main} > 세부 분류 선택")
        
        st.divider()
        sub_list = CATEGORY_TREE[st.session_state.selected_main]
        cols = st.columns(3)
        for idx, sub in enumerate(sub_list):
            with cols[idx % 3]:
                if st.button(f"🔖 {sub}", key=f"sub_{idx}", use_container_width=True):
                    st.session_state.selected_sub = sub
                    st.session_state.nav_depth = 2
                    st.rerun()

    # [Level 2] 레시피 리스트 (노트)
    elif st.session_state.nav_depth == 2:
        c1, c2 = st.columns([0.1, 0.9])
        with c1:
            if st.button("⬅️", help="목차로"):
                st.session_state.nav_depth = 1
                st.rerun()
        with c2:
            st.subheader(f"{st.session_state.selected_sub} > 레시피 목록")
            
        st.info("💡 (여기에 셰프님의 실제 레시피 데이터가 연동될 예정입니다)")
        
        # 샘플 UI
        st.markdown(f"**'{st.session_state.selected_sub}'** 카테고리에 등록된 레시피가 없습니다.")
        if st.button("➕ 이 카테고리에 새 레시피 등록하기"):
             st.toast("R&D 탭으로 이동하여 등록 절차를 진행합니다.")

# =========================================================
# [TAB 3, 4, 5] 준비 중
# =========================================================
with menu_tabs[2]: st.empty()
with menu_tabs[3]: st.empty()
with menu_tabs[4]: st.empty()
