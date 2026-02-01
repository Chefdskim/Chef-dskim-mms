import streamlit as st
import pandas as pd
from datetime import datetime, time

# 1. 페이지 설정
st.set_page_config(page_title="Chef_dskim 통합관리시스템", layout="wide")

# --- [초기 데이터] 시스템 시작 시 기본으로 가지고 있을 레시피 DB ---
# 셰프님이 데이터를 입력하기 전, 테스트용으로 몇 개 넣어둡니다.
INITIAL_RECIPES = [
    {
        "name": "왕갈비탕",
        "main_cat": "🇰🇷 한식",
        "sub_cat": "국/찌개/전골/탕",
        "tasks": [
            {"time": "08:00", "cat": "Prep", "desc": "핏물 빼기 (30분 간격 물 교체)", "point": "찬물 유수 유지"},
            {"time": "09:30", "cat": "Cooking", "desc": "초벌 삶기 및 불순물 제거", "point": "월계수잎 투입"}
        ]
    },
    {
        "name": "소갈비찜",
        "main_cat": "🇰🇷 한식",
        "sub_cat": "찜",
        "tasks": [
            {"time": "14:00", "cat": "Prep", "desc": "원육 포션 작업 및 칼집", "point": "기름기 제거"},
            {"time": "15:00", "cat": "Cooking", "desc": "1차 양념 숙성", "point": "연육 작용 확인"}
        ]
    }
]

# --- [카테고리 구조] ---
CATEGORY_TREE = {
    "🇰🇷 한식": ["국/찌개/전골/탕", "찜", "구이", "조림", "볶음", "무침/나물", "김치/장류", "밥/죽/면"],
    "🇯🇵 일식": ["사시미/스시", "구이(야키)", "튀김(아게)", "찜(무시)", "조림(니모노)", "면류(라멘/소바)", "돈부리"],
    "🇨🇳 중식": ["튀김/볶음", "탕/찜", "냉채", "면류", "만두/딤섬"],
    "🍝 양식": ["에피타이저", "파스타", "스테이크/메인", "스튜/수프", "샐러드"],
    "🍞 베이커리": ["제빵(Bread)", "제과(Cake/Cookie)", "디저트", "샌드위치"],
    "🍷 주류/음료": ["와인", "사케", "전통주", "칵테일", "커피/음료"],
    "📦 기타": ["소스/드레싱", "가니쉬", "향신료 배합", "이유식/환자식"]
}

# 2. 세션 상태 초기화 (데이터베이스 역할)
if 'recipe_db' not in st.session_state:
    st.session_state.recipe_db = INITIAL_RECIPES

if 'schedule_df' not in st.session_state:
    # 기본 루틴
    default_routine = [
        {"시작 시간": time(9, 0), "종료 시간": time(9, 30), "구분": "Prep", "세부 작업 내용": "오픈 준비 (식자재 검수)", "체크 포인트": "냉장고 온도", "완료": False},
        {"시작 시간": time(21, 30), "종료 시간": time(22, 0), "구분": "Clean", "세부 작업 내용": "마감 청소 및 발주", "체크 포인트": "가스/전기", "완료": False}
    ]
    st.session_state.schedule_df = pd.DataFrame(default_routine)

# 내비게이션 상태
if 'nav_depth' not in st.session_state: st.session_state.nav_depth = 0
if 'selected_main' not in st.session_state: st.session_state.selected_main = ""
if 'selected_sub' not in st.session_state: st.session_state.selected_sub = ""


# 사이드바
with st.sidebar:
    st.header("📊 시스템 상태")
    st.info(f"오늘: {datetime.now().strftime('%Y-%m-%d')}")
    st.write(f"등록된 레시피: {len(st.session_state.recipe_db)}개")
    if st.button("🏠 메뉴 홈으로 (초기화)"):
        st.session_state.nav_depth = 0
        st.rerun()

st.title("👨‍🍳 MISOYON 통합 관리 시스템")
menu_tabs = st.tabs(["⏱️ 오퍼레이션(Main)", "📖 메뉴 & 레시피", "🧪 R&D/레시피 등록", "💰 원가", "📸 입고"])

# =========================================================
# [TAB 1] 현장 오퍼레이션 (메뉴 검색 기능 복구됨!)
# =========================================================
with menu_tabs[0]:
    st.subheader("📅 현장 오퍼레이션 & 타임테이블")
    
    # [1] 메뉴 검색 및 공정 추가 기능 (복구됨)
    with st.expander("➕ [작업 추가] 오늘 진행할 메뉴를 검색해서 추가하세요", expanded=True):
        # DB에 있는 레시피 이름들을 가져옵니다.
        menu_names = [r['name'] for r in st.session_state.recipe_db]
        
        col_search, col_btn = st.columns([0.8, 0.2])
        with col_search:
            selected_menus_op = st.multiselect("메뉴 검색 (여러 개 선택 가능)", menu_names, placeholder="예: 갈비탕, 육회...")
        with col_btn:
            if st.button("🚀 공정 추가", use_container_width=True):
                new_rows = []
                for m_name in selected_menus_op:
                    # DB에서 해당 메뉴의 공정(tasks)을 찾음
                    target_recipe = next((item for item in st.session_state.recipe_db if item["name"] == m_name), None)
                    if target_recipe:
                        for task in target_recipe['tasks']:
                            # 문자열 시간("08:00")을 객체로 변환
                            t_obj = datetime.strptime(task['time'], "%H:%M").time()
                            new_rows.append({
                                "시작 시간": t_obj,
                                "종료 시간": t_obj, # 일단 시작시간과 동일하게 설정 (수정 가능)
                                "구분": task['cat'],
                                "세부 작업 내용": f"[{m_name}] {task['desc']}",
                                "체크 포인트": task['point'],
                                "완료": False
                            })
                
                if new_rows:
                    new_df = pd.DataFrame(new_rows)
                    st.session_state.schedule_df = pd.concat([st.session_state.schedule_df, new_df], ignore_index=True)
                    # 시간순 정렬
                    st.session_state.schedule_df = st.session_state.schedule_df.sort_values(by="시작 시간").reset_index(drop=True)
                    st.success(f"{len(selected_menus_op)}개 메뉴의 작업이 타임테이블에 추가되었습니다.")
                    st.rerun()

    # [2] 타임테이블 에디터
    st.divider()
    col1, col2 = st.columns([0.8, 0.2])
    with col1: st.caption("💡 아래 표에서 시간과 내용을 수정하세요.")
    with col2:
        if st.button("🔄 리셋"):
            # 기본 루틴만 남기고 초기화
            default_routine = [
                {"시작 시간": time(9, 0), "종료 시간": time(9, 30), "구분": "Prep", "세부 작업 내용": "오픈 준비", "체크 포인트": "온도 체크", "완료": False},
            ]
            st.session_state.schedule_df = pd.DataFrame(default_routine)
            st.rerun()

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

# =========================================================
# [TAB 2] 메뉴 & 레시피 (DB 연동됨)
# =========================================================
with menu_tabs[1]:
    if st.session_state.nav_depth == 0:
        st.subheader("📚 레시피 라이브러리 (Category)")
        cols = st.columns(4)
        for idx, category in enumerate(CATEGORY_TREE.keys()):
            with cols[idx % 4]:
                if st.button(f"\n{category}\n\n📂 열기", key=f"main_{idx}", use_container_width=True):
                    st.session_state.selected_main = category
                    st.session_state.nav_depth = 1
                    st.rerun()

    elif st.session_state.nav_depth == 1:
        st.button("⬅️ 뒤로가기", on_click=lambda: st.session_state.update(nav_depth=0))
        st.subheader(f"{st.session_state.selected_main} > 상세 분류")
        cols = st.columns(3)
        for idx, sub in enumerate(CATEGORY_TREE[st.session_state.selected_main]):
            with cols[idx % 3]:
                if st.button(f"🔖 {sub}", key=f"sub_{idx}", use_container_width=True):
                    st.session_state.selected_sub = sub
                    st.session_state.nav_depth = 2
                    st.rerun()

    elif st.session_state.nav_depth == 2:
        st.button("⬅️ 뒤로가기", on_click=lambda: st.session_state.update(nav_depth=1))
        st.subheader(f"{st.session_state.selected_sub} > 레시피 목록")
        
        # DB에서 현재 카테고리에 맞는 레시피 필터링
        current_recipes = [r for r in st.session_state.recipe_db 
                           if r['main_cat'] == st.session_state.selected_main 
                           and r['sub_cat'] == st.session_state.selected_sub]
        
        if not current_recipes:
            st.warning("아직 등록된 레시피가 없습니다. 'R&D' 탭에서 등록해주세요.")
        
        for recipe in current_recipes:
            with st.expander(f"🍽️ {recipe['name']} (상세 보기)"):
                st.write(f"**카테고리**: {recipe['main_cat']} > {recipe['sub_cat']}")
                st.write("**[조리 공정 SOP]**")
                for t in recipe['tasks']:
                    st.text(f"- {t['time']} [{t['cat']}] {t['desc']} (Point: {t['point']})")

# =========================================================
# [TAB 3] R&D / 레시피 등록 (데이터 입력 기능)
# =========================================================
with menu_tabs[2]:
    st.subheader("🧪 신규 레시피 및 데이터 등록")
    st.caption("여기서 레시피를 등록하면 '오퍼레이션'과 '메뉴 책장'에 자동 추가됩니다.")
    
    with st.form("recipe_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("메뉴명 (예: 전주비빔밥)")
            new_main = st.selectbox("대분류", list(CATEGORY_TREE.keys()))
        with col2:
            # 선택된 대분류에 맞는 중분류 목록 가져오기
            sub_options = CATEGORY_TREE[new_main]
            new_sub = st.selectbox("중분류", sub_options)
            st.write("") # 간격 맞춤

        st.divider()
        st.write("⏱️ **조리 공정 (SOP) 입력** - 타임테이블 연동용")
        st.caption("예: 08:00 / Prep / 재료손질 / 2cm 간격 유지")
        
        # 공정 입력은 간단하게 텍스트로 받고 파싱하거나, 에디터를 쓸 수 있습니다.
        # 여기서는 사용 편의를 위해 Data Editor를 입력폼으로 씁니다.
        sop_input_df = pd.DataFrame([
            {"time": "09:00", "cat": "Prep", "desc": "작업 내용 입력", "point": "체크포인트"},
            {"time": "10:00", "cat": "Cooking", "desc": "작업 내용 입력", "point": "체크포인트"},
        ])
        edited_sop = st.data_editor(sop_input_df, num_rows="dynamic", use_container_width=True)
        
        submitted = st.form_submit_button("💾 레시피 시스템 등록")
        
        if submitted:
            if new_name:
                # 데이터 변환
                tasks_list = []
                for _, row in edited_sop.iterrows():
                    if row['desc'] != "작업 내용 입력": # 기본값 제외
                        tasks_list.append({
                            "time": row['time'], 
                            "cat": row['cat'], 
                            "desc": row['desc'], 
                            "point": row['point']
                        })
                
                # DB에 저장
                new_recipe = {
                    "name": new_name,
                    "main_cat": new_main,
                    "sub_cat": new_sub,
                    "tasks": tasks_list
                }
                st.session_state.recipe_db.append(new_recipe)
                st.success(f"✅ [{new_name}] 등록 완료! 이제 '오퍼레이션'과 '책장'에서 검색됩니다.")
            else:
                st.error("메뉴명을 입력해주세요.")

# [나머지 탭]
with menu_tabs[3]: st.write("원가 관리 준비 중")
with menu_tabs[4]: st.write("입고 관리 준비 중")
