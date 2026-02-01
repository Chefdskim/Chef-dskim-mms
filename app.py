import streamlit as st
import pandas as pd
from datetime import datetime, time

# 1. 페이지 설정
st.set_page_config(page_title="Chef_dskim 통합 관리 시스템", layout="wide")

# =========================================================
# [데이터베이스 초기화]
# =========================================================

# 1. 카테고리 구조
CATEGORY_TREE = {
    "🇰🇷 한식": ["국/찌개/전골/탕", "찜", "구이", "조림", "볶음", "무침/나물", "김치/장류", "밥/죽/면"],
    "🇯🇵 일식": ["사시미/스시", "구이(야키)", "튀김(아게)", "찜(무시)", "조림(니모노)", "면류(라멘/소바)", "돈부리"],
    "🇨🇳 중식": ["튀김/볶음", "탕/찜", "냉채", "면류", "만두/딤섬"],
    "🍝 양식": ["에피타이저", "파스타", "스테이크/메인", "스튜/수프", "샐러드"],
    "🍞 베이커리": ["제빵(Bread)", "제과(Cake/Cookie)", "디저트", "샌드위치"],
    "🍷 주류/음료": ["와인", "사케", "전통주", "칵테일", "커피/음료"],
    "📦 기타": ["소스/드레싱", "가니쉬", "향신료 배합", "이유식/환자식"]
}

# 2. 식자재 단가 마스터 (기초 데이터 탑재)
if 'ingredient_db' not in st.session_state:
    data = [
        {"품목명": "소갈비(Short Rib)", "규격": "kg", "단가": 35000, "수율": 100},
        {"품목명": "돼지갈비", "규격": "kg", "단가": 18000, "수율": 100},
        {"품목명": "갈비본살", "규격": "kg", "단가": 42000, "수율": 90},
        {"품목명": "진간장", "규격": "L", "단가": 4500, "수율": 100},
        {"품목명": "국간장", "규격": "L", "단가": 5000, "수율": 100},
        {"품목명": "백설탕", "규격": "kg", "단가": 1800, "수율": 100},
        {"품목명": "흑설탕", "규격": "kg", "단가": 2100, "수율": 100},
        {"품목명": "물엿", "규격": "kg", "단가": 3000, "수율": 100},
        {"품목명": "참기름", "규격": "can", "단가": 55000, "수율": 100},
        {"품목명": "통깨", "규격": "kg", "단가": 12000, "수율": 100},
        {"품목명": "후추(순후추)", "규격": "can", "단가": 6000, "수율": 100},
        {"품목명": "깐마늘", "규격": "kg", "단가": 8000, "수율": 95},
        {"품목명": "다진마늘", "규격": "kg", "단가": 9500, "수율": 100},
        {"품목명": "생강", "규격": "kg", "단가": 7000, "수율": 90},
        {"품목명": "대파", "규격": "단", "단가": 2500, "수율": 85},
        {"품목명": "양파", "규격": "kg", "단가": 1500, "수율": 90},
        {"품목명": "무", "규격": "개", "단가": 1500, "수율": 85},
        {"품목명": "배", "규격": "개", "단가": 4000, "수율": 80},
        {"품목명": "사과", "규격": "개", "단가": 3500, "수율": 80},
        {"품목명": "청주", "규격": "bottle", "단가": 9000, "수율": 100},
        {"품목명": "계란(특란)", "규격": "ea", "단가": 350, "수율": 100},
        {"품목명": "맛소금", "규격": "g", "단가": 12, "수율": 100},
    ]
    st.session_state.ingredient_db = pd.DataFrame(data)

# 3. 레시피 DB
if 'recipe_db' not in st.session_state:
    st.session_state.recipe_db = [
        {
            "name": "왕갈비탕", 
            "main_cat": "🇰🇷 한식", 
            "sub_cat": "국/찌개/전골/탕", 
            "tasks": [
                {"time": "08:00", "cat": "Prep", "desc": "핏물 빼기 (30분 간격)", "point": "찬물 유수"},
                {"time": "09:30", "cat": "Cooking", "desc": "초벌 삶기", "point": "월계수잎"}
            ]
        }
    ]

# 4. 타임테이블 데이터
if 'schedule_df' not in st.session_state:
    default_routine = [{"시작 시간": time(9,0), "종료 시간": time(9,30), "구분": "Prep", "세부 작업 내용": "오픈 준비", "체크 포인트": "온도", "완료": False}]
    st.session_state.schedule_df = pd.DataFrame(default_routine)

# 5. 내비게이션 상태
if 'nav_depth' not in st.session_state: st.session_state.nav_depth = 0
if 'selected_main' not in st.session_state: st.session_state.selected_main = ""
if 'selected_sub' not in st.session_state: st.session_state.selected_sub = ""


# =========================================================
# 사이드바 & 헤더
# =========================================================
with st.sidebar:
    st.header("📊 시스템 상태")
    st.info(f"오늘: {datetime.now().strftime('%Y-%m-%d')}")
    st.write(f"식자재 DB: {len(st.session_state.ingredient_db)} 품목")
    st.divider()
    
    col_home, col_reset = st.columns(2)
    with col_home:
        if st.button("🏠 홈으로"):
            st.session_state.nav_depth = 0
            st.rerun()
    with col_reset:
        if st.button("🔄 DB 초기화"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

st.title("👨‍🍳 Chef_dskim 통합 관리 시스템")

menu_tabs = st.tabs(["⏱️ 오퍼레이션", "📖 메뉴 & 레시피", "🧪 R&D/레시피 등록", "💰 원가 관리", "📸 입고"])

# =========================================================
# [TAB 1] 현장 오퍼레이션
# =========================================================
with menu_tabs[0]:
    st.subheader("📅 현장 오퍼레이션 & 타임테이블")
    
    with st.expander("➕ [작업 추가] 메뉴 검색", expanded=False):
        menu_names = [r['name'] for r in st.session_state.recipe_db]
        selected_menus_op = st.multiselect("메뉴 선택", menu_names)
        
        if st.button("🚀 공정 추가") and selected_menus_op:
            new_rows = []
            for m_name in selected_menus_op:
                target_recipe = next((item for item in st.session_state.recipe_db if item["name"] == m_name), None)
                if target_recipe:
                    for task in target_recipe['tasks']:
                        try: t_obj = datetime.strptime(task['time'], "%H:%M").time()
                        except: t_obj = time(9,0)
                        
                        new_rows.append({
                            "시작 시간": t_obj, "종료 시간": t_obj, "구분": task['cat'],
                            "세부 작업 내용": f"[{m_name}] {task['desc']}", "체크 포인트": task['point'], "완료": False
                        })
            
            if new_rows:
                new_df = pd.DataFrame(new_rows)
                st.session_state.schedule_df = pd.concat([st.session_state.schedule_df, new_df], ignore_index=True)
                st.session_state.schedule_df = st.session_state.schedule_df.sort_values(by="시작 시간").reset_index(drop=True)
                st.success("공정이 추가되었습니다.")
                st.rerun()
                
    edited_df = st.data_editor(
        st.session_state.schedule_df,
        num_rows="dynamic", use_container_width=True, hide_index=True,
        column_config={
            "시작 시간": st.column_config.TimeColumn("Start", format="HH:mm"),
            "종료 시간": st.column_config.TimeColumn("End", format="HH:mm"),
            "구분": st.column_config.SelectboxColumn("Cat", options=["Prep", "Cooking", "Service", "Clean", "R&D"]),
            "세부 작업 내용": st.column_config.TextColumn("Task", width="large"),
            "체크 포인트": st.column_config.TextColumn("Check Point", width="medium"),
            "완료": st.column_config.CheckboxColumn("Done", default=False)
        }
    )
    st.session_state.schedule_df = edited_df

# =========================================================
# [TAB 2] 메뉴 & 레시피
# =========================================================
with menu_tabs[1]:
    if st.session_state.nav_depth == 0:
        st.subheader("📚 레시피 라이브러리 (Category)")
        cols = st.columns(4)
        for idx, cat in enumerate(CATEGORY_TREE.keys()):
            with cols[idx % 4]:
                if st.button(f"\n{cat}\n\n📂", key=f"m_{idx}", use_container_width=True):
                    st.session_state.selected_main = cat
                    st.session_state.nav_depth = 1
                    st.rerun()
                    
    elif st.session_state.nav_depth == 1:
        st.button("⬅️ 뒤로가기", on_click=lambda: st.session_state.update(nav_depth=0))
        st.subheader(f"{st.session_state.selected_main}")
        cols = st.columns(3)
        for idx, sub in enumerate(CATEGORY_TREE[st.session_state.selected_main]):
            with cols[idx % 3]:
                if st.button(f"🔖 {sub}", key=f"s_{idx}", use_container_width=True):
                    st.session_state.selected_sub = sub
                    st.session_state.nav_depth = 2
                    st.rerun()
                    
    elif st.session_state.nav_depth == 2:
        st.button("⬅️ 뒤로가기", on_click=lambda: st.session_state.update(nav_depth=1))
        st.subheader(f"{st.session_state.selected_sub} > 레시피 목록")
        
        current_recipes = [r for r in st.session_state.recipe_db 
                           if r['main_cat'] == st.session_state.selected_main 
                           and r['sub_cat'] == st.session_state.selected_sub]
        
        if not current_recipes:
            st.info("등록된 레시피가 없습니다.")
        
        for recipe in current_recipes:
            with st.expander(f"🍽️ {recipe['name']} (상세 보기)"):
                st.write("**[조리 공정 SOP]**")
                for t in recipe['tasks']:
                    st.text(f"- {t['time']} [{t['cat']}] {t['desc']} (Point: {t['point']})")

# =========================================================
# [TAB 3] R&D / 레시피 등록
# =========================================================
with menu_tabs[2]:
    st.subheader("🧪 신규 레시피 등록")
    with st.form("new_recipe"):
        col1, col2 = st.columns(2)
        with col1:
            nm = st.text_input("메뉴명 (예: 갈비찜)")
            main_c = st.selectbox("대분류", list(CATEGORY_TREE.keys()))
        with col2:
            sub_c = st.selectbox("중분류", CATEGORY_TREE[main_c])
            st.write("")
        
        st.write("⏱️ **조리 공정 (SOP)**")
        sop_input_df = pd.DataFrame([
            {"time": "09:00", "cat": "Prep", "desc": "작업 내용", "point": "체크포인트"},
        ])
        edited_sop = st.data_editor(sop_input_df, num_rows="dynamic", use_container_width=True)
        
        if st.form_submit_button("💾 레시피 저장"):
            if nm:
                tasks_list = []
                for _, row in edited_sop.iterrows():
                    if row['desc'] != "작업 내용":
                        tasks_list.append({
                            "time": row['time'], "cat": row['cat'], 
                            "desc": row['desc'], "point": row['point']
                        })
                st.session_state.recipe_db.append({
                    "name": nm, "main_cat": main_c, "sub_cat": sub_c, "tasks": tasks_list
                })
                st.success("저장 완료!")

# =========================================================
# [TAB 4] 원가 관리 (인분수 계산 기능 적용)
# =========================================================
with menu_tabs[3]:
    st.subheader("💰 원가 분석 및 마진율 계산기")
    
    tab_cost1, tab_cost2 = st.tabs(["📊 식자재 단가표(Master)", "🧮 레시피 원가 계산"])
    
    # 4-1 단가표 관리
    with tab_cost1:
        st.caption("💡 엑셀 업로드 시 기존 데이터에 추가됩니다.")
        up_file = st.file_uploader("단가표 엑셀 업로드", type=["xlsx", "csv"])
        if up_file:
            try:
                df = pd.read_excel(up_file) if up_file.name.endswith('xlsx') else pd.read_csv(up_file)
                st.session_state.ingredient_db = df
                st.success("DB 업데이트 완료")
            except: pass
        
        edited_ing = st.data_editor(st.session_state.ingredient_db, num_rows="dynamic", use_container_width=True)
        st.session_state.ingredient_db = edited_ing
        
    # 4-2 계산기
    with tab_cost2:
        # [수정된 입력 UI] 메뉴명 / 판매가 / 인분수
        col_sel, col_servings, col_info = st.columns([1, 1, 2])
        with col_sel:
            r_list = [r['name'] for r in st.session_state.recipe_db]
            target_menu = st.selectbox("메뉴 선택", r_list) if r_list else "메뉴 없음"
        
        with col_servings:
            servings = st.number_input("인분수 (Servings)", value=1, min_value=1, step=1, help="몇 인분 기준으로 계산할까요?")
            
        with col_info:
            sales_price_per_unit = st.number_input("1인분 판매 예정가 (원)", value=15000, step=1000)
            
        st.divider()
        st.write(f"**[{target_menu}] 재료 투입 (1인분 기준)**")
        
        if 'calc_df' not in st.session_state:
            st.session_state.calc_df = pd.DataFrame(columns=["재료명", "단위", "1인분 투입량", "수율(%)", "1인분 원가"])

        c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
        
        with c1:
            search_query = st.text_input("🔍 재료 검색 (엔터)", placeholder="예: 갈비")
            full_list = st.session_state.ingredient_db["품목명"].unique()
            filtered_list = [i for i in full_list if search_query in i] if search_query else []

        with c2:
            ing_name = None
            if filtered_list:
                ing_name = st.selectbox("검색 결과", filtered_list)
                row = st.session_state.ingredient_db[st.session_state.ingredient_db["품목명"]==ing_name].iloc[0]
                unit_type = str(row["규격"]).lower().strip()
                base_price = row["단가"]
                base_yield = row["수율"]
                lbl = "1인분당 투입량 (g/ml)" if unit_type in ['kg', 'l', '리터', 'g', 'ml'] else f"1인분당 투입량 ({unit_type})"
            elif search_query:
                st.warning("결과 없음")
            else:
                st.info("좌측에 검색어를 입력하세요.")

        with c3:
            if ing_name:
                usage = st.number_input(lbl, value=0.0)
                st.caption(f"단가: {base_price:,}원 / 수율: {base_yield}%")

        with c4:
            st.write("")
            st.write("")
            if ing_name and st.button("➕ 투입"):
                real_cost = 0
                if unit_type in ['kg', 'l', '리터']:
                    real_cost = (base_price / 1000) * usage
                else:
                    real_cost = base_price * usage
                
                if base_yield > 0:
                    real_cost = real_cost * (100 / base_yield)
                
                new_row = {
                    "재료명": ing_name, "단위": unit_type,
                    "1인분 투입량": usage, "수율(%)": base_yield, "1인분 원가": int(real_cost)
                }
                st.session_state.calc_df = pd.concat([st.session_state.calc_df, pd.DataFrame([new_row])], ignore_index=True)

        st.table(st.session_state.calc_df)
        
        # [계산 로직 강화]
        total_cost_per_unit = st.session_state.calc_df["1인분 원가"].sum()
        margin_per_unit = sales_price_per_unit - total_cost_per_unit
        rate = (total_cost_per_unit / sales_price_per_unit * 100) if sales_price_per_unit > 0 else 0
        
        # 인분수 적용 총계
        total_cost_all = total_cost_per_unit * servings
        total_sales_all = sales_price_per_unit * servings
        total_margin_all = margin_per_unit * servings
        
        st.divider()
        st.subheader("💰 최종 수익성 분석 결과")
        
        # 탭을 나눠서 보여줌 (1인분 vs 전체)
        res_tab1, res_tab2 = st.tabs([f"👤 1인분 기준", f"👥 {servings}인분 기준 (단체/예약)"])
        
        with res_tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("1인분 원가", f"{int(total_cost_per_unit):,}원")
            c2.metric("1인분 마진", f"{int(margin_per_unit):,}원")
            c3.metric("원가율", f"{rate:.1f}%", delta_color="inverse")
            
        with res_tab2:
            c1, c2, c3 = st.columns(3)
            c1.metric(f"총 원가 ({servings}인분)", f"{int(total_cost_all):,}원", help="재료비 총 예상 지출액")
            c2.metric(f"총 예상 수익 ({servings}인분)", f"{int(total_margin_all):,}원", help="총 매출 - 총 재료비")
            c3.metric("예상 총 매출", f"{int(total_sales_all):,}원")
        
        if st.button("🔄 계산기 초기화"):
            st.session_state.calc_df = st.session_state.calc_df.iloc[0:0]
            st.rerun()

# [TAB 5] 입고 관리
with menu_tabs[4]:
    st.header("📸 스마트 입고 관리 (준비 중)")
