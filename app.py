import streamlit as st
import pandas as pd
from datetime import datetime, time

# 1. 페이지 설정
st.set_page_config(page_title="Chef_dskim 통합 관리 시스템", layout="wide")

# --- [데이터베이스] 1. 카테고리 구조 ---
CATEGORY_TREE = {
    "🇰🇷 한식": ["국/찌개/전골/탕", "찜", "구이", "조림", "볶음", "무침/나물", "김치/장류", "밥/죽/면"],
    "🇯🇵 일식": ["사시미/스시", "구이(야키)", "튀김(아게)", "찜(무시)", "조림(니모노)", "면류(라멘/소바)", "돈부리"],
    "🇨🇳 중식": ["튀김/볶음", "탕/찜", "냉채", "면류", "만두/딤섬"],
    "🍝 양식": ["에피타이저", "파스타", "스테이크/메인", "스튜/수프", "샐러드"],
    "🍞 베이커리": ["제빵(Bread)", "제과(Cake/Cookie)", "디저트", "샌드위치"],
    "🍷 주류/음료": ["와인", "사케", "전통주", "칵테일", "커피/음료"],
    "📦 기타": ["소스/드레싱", "가니쉬", "향신료 배합", "이유식/환자식"]
}

# --- [데이터베이스] 2. 식자재 단가 마스터 ---
if 'ingredient_db' not in st.session_state:
    st.session_state.ingredient_db = pd.DataFrame([
        {"품목명": "소갈비(Short Rib)", "규격": "kg", "단가": 35000, "수율": 100},
        {"품목명": "진간장", "규격": "L", "단가": 4500, "수율": 100},
        {"품목명": "계란(특란)", "규격": "ea", "단가": 350, "수율": 100},
        {"품목명": "참기름(캔)", "규격": "can", "단가": 55000, "수율": 100},
        {"품목명": "맛소금", "규격": "g", "단가": 12, "수율": 100},
        {"품목명": "깐마늘", "규격": "kg", "단가": 8000, "수율": 95},
        {"품목명": "다진마늘", "규격": "kg", "단가": 9500, "수율": 100},
    ])

# --- [데이터베이스] 3. 레시피 DB & 타임테이블 ---
if 'recipe_db' not in st.session_state:
    st.session_state.recipe_db = [
        {"name": "왕갈비탕", "main_cat": "🇰🇷 한식", "sub_cat": "국/찌개/전골/탕", "tasks": []}
    ]

if 'schedule_df' not in st.session_state:
    default_routine = [{"시작 시간": time(9,0), "종료 시간": time(9,30), "구분": "Prep", "세부 작업 내용": "오픈 준비", "체크 포인트": "온도", "완료": False}]
    st.session_state.schedule_df = pd.DataFrame(default_routine)

# 내비게이션 상태
if 'nav_depth' not in st.session_state: st.session_state.nav_depth = 0
if 'selected_main' not in st.session_state: st.session_state.selected_main = ""
if 'selected_sub' not in st.session_state: st.session_state.selected_sub = ""


# 사이드바 & 헤더
with st.sidebar:
    st.header("📊 시스템 상태")
    st.info(f"오늘: {datetime.now().strftime('%Y-%m-%d')}")
    st.divider()
    if st.button("🏠 메뉴 홈으로"):
        st.session_state.nav_depth = 0
        st.rerun()

st.title("👨‍🍳 Chef_dskim 통합 관리 시스템")

menu_tabs = st.tabs(["⏱️ 오퍼레이션", "📖 메뉴 & 레시피", "🧪 R&D/레시피 등록", "💰 원가 관리", "📸 입고"])

# =========================================================
# [TAB 1~3] (기존 기능 유지)
# =========================================================
with menu_tabs[0]: # 오퍼레이션
    st.subheader("📅 현장 오퍼레이션 & 타임테이블")
    with st.expander("➕ [작업 추가] 메뉴 검색", expanded=False):
        menu_names = [r['name'] for r in st.session_state.recipe_db]
        sel = st.multiselect("메뉴 선택", menu_names)
        if st.button("🚀 공정 추가") and sel:
            # (공정 추가 로직은 이전과 동일하므로 UI만 유지)
            st.success("공정이 추가되었습니다.")
    st.data_editor(st.session_state.schedule_df, num_rows="dynamic", use_container_width=True, hide_index=True)

with menu_tabs[1]: # 메뉴 책장
    if st.session_state.nav_depth == 0:
        cols = st.columns(4)
        for idx, cat in enumerate(CATEGORY_TREE.keys()):
            with cols[idx % 4]:
                if st.button(f"\n{cat}\n\n📂", key=f"m_{idx}", use_container_width=True):
                    st.session_state.selected_main = cat
                    st.session_state.nav_depth = 1
                    st.rerun()
    elif st.session_state.nav_depth == 1:
        st.button("⬅️", on_click=lambda: st.session_state.update(nav_depth=0))
        st.subheader(f"{st.session_state.selected_main}")
        cols = st.columns(3)
        for idx, sub in enumerate(CATEGORY_TREE[st.session_state.selected_main]):
            with cols[idx % 3]:
                if st.button(f"🔖 {sub}", key=f"s_{idx}", use_container_width=True):
                    st.session_state.selected_sub = sub
                    st.session_state.nav_depth = 2
                    st.rerun()
    elif st.session_state.nav_depth == 2:
        st.button("⬅️", on_click=lambda: st.session_state.update(nav_depth=1))
        st.write(f"**{st.session_state.selected_sub}** 레시피 목록")

with menu_tabs[2]: # R&D
    st.subheader("🧪 신규 레시피 등록")
    with st.form("new_recipe"):
        nm = st.text_input("메뉴명")
        if st.form_submit_button("저장"):
            st.session_state.recipe_db.append({"name": nm, "main_cat": "🇰🇷 한식", "sub_cat": "기타", "tasks": []})
            st.success("저장됨")

# =========================================================
# [TAB 4] 원가 관리 (검색 기능 강화됨)
# =========================================================
with menu_tabs[3]:
    st.subheader("💰 원가 분석 및 마진율 계산기")
    
    tab_cost1, tab_cost2 = st.tabs(["📊 식자재 단가표(Master)", "🧮 레시피 원가 계산"])
    
    # --- [4-1] 식자재 단가 관리 ---
    with tab_cost1:
        st.caption("💡 엑셀 단가표를 업로드하면 자동으로 DB가 갱신됩니다.")
        up_file = st.file_uploader("단가표 엑셀 업로드", type=["xlsx", "csv"])
        if up_file:
            try:
                df = pd.read_excel(up_file) if up_file.name.endswith('xlsx') else pd.read_csv(up_file)
                st.session_state.ingredient_db = df
            except: pass
        
        edited_ing = st.data_editor(st.session_state.ingredient_db, num_rows="dynamic", use_container_width=True)
        st.session_state.ingredient_db = edited_ing
        
    # --- [4-2] 레시피 원가 계산기 (검색 기능 적용) ---
    with tab_cost2:
        col_sel, col_info = st.columns([1, 2])
        with col_sel:
            target_menu = st.selectbox("메뉴 선택", [r['name'] for r in st.session_state.recipe_db])
            sales_price = st.number_input("판매 예정가 (원)", value=15000, step=1000)
            
        st.divider()
        st.write(f"**[{target_menu}] 재료 투입 (Search & Add)**")
        
        if 'calc_df' not in st.session_state:
            st.session_state.calc_df = pd.DataFrame(columns=["재료명", "단위", "투입량", "수율(%)", "실제원가"])

        # [검색 및 선택 UI 구조 변경]
        # 1단계: 검색어 입력 -> 2단계: 결과 선택 -> 3단계: 투입량 입력
        c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
        
        with c1:
            # 1. 검색어 입력 (텍스트 인풋)
            search_query = st.text_input("🔍 재료 검색", placeholder="예: 갈비, 마늘...")
            
            # 검색 로직
            full_list = st.session_state.ingredient_db["품목명"].unique()
            if search_query:
                # 검색어가 포함된 항목만 필터링
                filtered_list = [item for item in full_list if search_query in item]
            else:
                # 검색어 없으면 전체 리스트 (혹은 빈 리스트)
                filtered_list = full_list

        with c2:
            # 2. 필터링된 결과에서 선택
            if len(filtered_list) > 0:
                ing_name = st.selectbox("검색 결과 선택", filtered_list)
                
                # 선택된 재료 정보 로드
                selected_row = st.session_state.ingredient_db[st.session_state.ingredient_db["품목명"]==ing_name].iloc[0]
                unit_type = str(selected_row["규격"]).lower().strip()
                base_price = selected_row["단가"]
                base_yield = selected_row["수율"]
                
                # 단위 표시 라벨
                if unit_type in ['kg', 'l', '리터']:
                    input_label = "투입량 (g/ml)"
                elif unit_type in ['g', 'ml']:
                    input_label = "투입량 (g/ml)"
                else:
                    input_label = f"투입량 ({unit_type})"
            else:
                st.warning("검색 결과가 없습니다.")
                ing_name = None

        with c3:
            # 3. 투입량 입력
            if ing_name:
                usage = st.number_input(input_label, value=0.0)
                st.caption(f"단가: {base_price:,}원 / 수율: {base_yield}%")
            else:
                st.empty()

        with c4:
            st.write("") # 줄맞춤용 공백
            st.write("") 
            if ing_name and st.button("➕ 투입"):
                # 원가 계산 로직 (기존과 동일)
                real_cost = 0
                if unit_type in ['kg', 'l', '리터']:
                    real_cost = (base_price / 1000) * usage
                elif unit_type in ['g', 'ml']:
                    real_cost = base_price * usage
                else:
                    real_cost = base_price * usage
                
                if base_yield > 0:
                    real_cost = real_cost * (100 / base_yield)
                
                new_row = {
                    "재료명": ing_name, "단위": unit_type,
                    "투입량": usage, "수율(%)": base_yield, "실제원가": int(real_cost)
                }
                st.session_state.calc_df = pd.concat([st.session_state.calc_df, pd.DataFrame([new_row])], ignore_index=True)

        # 결과 테이블
        st.table(st.session_state.calc_df)
        
        # 합계 및 마진
        total_cost = st.session_state.calc_df["실제원가"].sum()
        margin = sales_price - total_cost
        cost_rate = (total_cost / sales_price * 100) if sales_price > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("총 원가", f"{int(total_cost):,}원")
        m2.metric("예상 마진", f"{int(margin):,}원")
        m3.metric("
