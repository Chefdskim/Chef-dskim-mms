import streamlit as st
import pandas as pd
from datetime import datetime, time

# 1. 페이지 설정
st.set_page_config(page_title="Chef_dskim 통합 관리 시스템", layout="wide")

# =========================================================
# [데이터베이스 초기화]
# =========================================================

# 1. 카테고리
CATEGORY_TREE = {
    "🇰🇷 한식": ["국/찌개/전골/탕", "찜", "구이", "조림", "볶음", "무침/나물", "김치/장류", "밥/죽/면"],
    "🇯🇵 일식": ["사시미/스시", "구이(야키)", "튀김(아게)", "찜(무시)", "조림(니모노)", "면류(라멘/소바)", "돈부리"],
    "🇨🇳 중식": ["튀김/볶음", "탕/찜", "냉채", "면류", "만두/딤섬"],
    "🍝 양식": ["에피타이저", "파스타", "스테이크/메인", "스튜/수프", "샐러드"],
    "🍞 베이커리": ["제빵(Bread)", "제과(Cake/Cookie)", "디저트", "샌드위치"],
    "🍷 주류/음료": ["와인", "사케", "전통주", "칵테일", "커피/음료"],
    "📦 기타": ["소스/드레싱", "가니쉬", "향신료 배합", "이유식/환자식"]
}

# 2. 식자재 DB (기초 데이터)
if 'ingredient_db' not in st.session_state:
    data = [
        {"품목명": "소갈비(Short Rib)", "규격": "kg", "단가": 35000, "수율": 100},
        {"품목명": "돼지갈비", "규격": "kg", "단가": 18000, "수율": 100},
        {"품목명": "진간장", "규격": "L", "단가": 4500, "수율": 100},
        {"품목명": "백설탕", "규격": "kg", "단가": 1800, "수율": 100},
        {"품목명": "물엿", "규격": "kg", "단가": 3000, "수율": 100},
        {"품목명": "참기름", "규격": "can", "단가": 55000, "수율": 100},
        {"품목명": "깐마늘", "규격": "kg", "단가": 8000, "수율": 95},
        {"품목명": "대파", "규격": "단", "단가": 2500, "수율": 85},
        {"품목명": "양파", "규격": "kg", "단가": 1500, "수율": 90},
        {"품목명": "무", "규격": "개", "단가": 1500, "수율": 85},
        {"품목명": "배", "규격": "개", "단가": 4000, "수율": 80},
        {"품목명": "계란(특란)", "규격": "ea", "단가": 350, "수율": 100},
        {"품목명": "맛소금", "규격": "g", "단가": 12, "수율": 100},
        {"품목명": "쌀", "규격": "kg", "단가": 3000, "수율": 100},
        {"품목명": "김치", "규격": "kg", "단가": 5000, "수율": 100},
    ]
    st.session_state.ingredient_db = pd.DataFrame(data)

# 3. 레시피 DB
if 'recipe_db' not in st.session_state:
    st.session_state.recipe_db = [
        {
            "name": "왕갈비탕", 
            "main_cat": "🇰🇷 한식", 
            "sub_cat": "국/찌개/전골/탕",
            "ingredients": [
                {"name": "소갈비(Short Rib)", "qty": 250}, 
                {"name": "무", "qty": 0.1}, 
                {"name": "대파", "qty": 0.1},
                {"name": "깐마늘", "qty": 10}
            ],
            "tasks": [{"time": "08:00", "cat": "Prep", "desc": "핏물 빼기", "point": "찬물 유수"}]
        },
        {
            "name": "공기밥", 
            "main_cat": "🇰🇷 한식", 
            "sub_cat": "밥/죽/면",
            "ingredients": [{"name": "쌀", "qty": 150}],
            "tasks": []
        },
        {
            "name": "배추김치(반찬)", 
            "main_cat": "🇰🇷 한식", 
            "sub_cat": "김치/장류",
            "ingredients": [{"name": "김치", "qty": 80}],
            "tasks": []
        }
    ]

# 4. 타임테이블 & 내비게이션
if 'schedule_df' not in st.session_state:
    st.session_state.schedule_df = pd.DataFrame([{"시작 시간": time(9,0), "종료 시간": time(9,30), "구분": "Prep", "세부 작업 내용": "오픈 준비", "체크 포인트": "온도", "완료": False}])
if 'nav_depth' not in st.session_state: st.session_state.nav_depth = 0
if 'selected_main' not in st.session_state: st.session_state.selected_main = ""
if 'selected_sub' not in st.session_state: st.session_state.selected_sub = ""


# =========================================================
# 사이드바 & 헤더
# =========================================================
with st.sidebar:
    st.header("📊 시스템 상태")
    st.info(f"오늘: {datetime.now().strftime('%Y-%m-%d')}")
    st.divider()
    if st.button("🏠 홈으로"): st.session_state.nav_depth = 0; st.rerun()
    if st.button("🔄 DB 초기화"): 
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

st.title("👨‍🍳 Chef_dskim 통합 관리 시스템")
menu_tabs = st.tabs(["⏱️ 오퍼레이션", "📖 메뉴 & 레시피", "🧪 R&D/레시피 등록", "💰 원가 관리", "📸 입고"])

# =========================================================
# [TAB 1] 오퍼레이션
# =========================================================
with menu_tabs[0]:
    st.subheader("📅 현장 오퍼레이션")
    with st.expander("➕ [작업 추가] 메뉴 검색", expanded=False):
        menu_names = [r['name'] for r in st.session_state.recipe_db]
        selected = st.multiselect("메뉴 선택", menu_names)
        if st.button("🚀 공정 추가") and selected:
            st.success("공정 추가됨 (화면 갱신)")
    st.data_editor(st.session_state.schedule_df, num_rows="dynamic", use_container_width=True, hide_index=True)

# =========================================================
# [TAB 2] 메뉴 책장
# =========================================================
with menu_tabs[1]:
    if st.session_state.nav_depth == 0:
        cols = st.columns(4)
        for idx, cat in enumerate(CATEGORY_TREE.keys()):
            with cols[idx%4]: 
                if st.button(f"\n{cat}\n\n📂", key=f"m_{idx}", use_container_width=True): 
                    st.session_state.selected_main=cat; st.session_state.nav_depth=1; st.rerun()
    elif st.session_state.nav_depth == 1:
        st.button("⬅️", on_click=lambda: st.session_state.update(nav_depth=0))
        cols = st.columns(3)
        for idx, sub in enumerate(CATEGORY_TREE[st.session_state.selected_main]):
            with cols[idx%3]:
                if st.button(f"🔖 {sub}", key=f"s_{idx}", use_container_width=True):
                    st.session_state.selected_sub=sub; st.session_state.nav_depth=2; st.rerun()
    elif st.session_state.nav_depth == 2:
        st.button("⬅️", on_click=lambda: st.session_state.update(nav_depth=1))
        cur = [r for r in st.session_state.recipe_db if r['main_cat']==st.session_state.selected_main and r['sub_cat']==st.session_state.selected_sub]
        for r in cur:
            with st.expander(f"🍽️ {r['name']}"):
                st.write("**[재료 구성 (1인분)]**")
                ing_display = []
                for i in r.get('ingredients', []):
                    ing_display.append(f"{i['name']} {i['qty']}")
                st.info(", ".join(ing_display) if ing_display else "등록된 재료 없음")
                st.write("**[공정]**")
                for t in r['tasks']: st.text(f"- {t['time']} {t['desc']}")

# =========================================================
# [TAB 3] R&D
# =========================================================
with menu_tabs[2]:
    st.subheader("🧪 신규 레시피 및 재료 구성 등록")
    st.caption("※ 주의: 구매 단위가 'kg'이나 'L'인 식자재는 **g(그램)** 또는 **ml** 단위로 입력해주세요.")
    
    with st.form("new_recipe_full"):
        col1, col2 = st.columns(2)
        with col1:
            nm = st.text_input("메뉴명")
            main_c = st.selectbox("대분류", list(CATEGORY_TREE.keys()))
        with col2:
            sub_c = st.selectbox("중분류", CATEGORY_TREE[main_c])
            st.write("") 

        st.divider()
        st.write("🥦 **재료 구성 (BOM)**")
        
        # 초기값 빈 리스트 (에러 방지)
        empty_df = pd.DataFrame(columns=["재료명(검색)", "1인분 투입량"])
        
        edited_ing_bom = st.data_editor(
            empty_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "재료명(검색)": st.column_config.SelectboxColumn("재료명", options=list(st.session_state.ingredient_db["품목명"].unique()), required=True),
                "1인분 투입량": st.column_config.NumberColumn("1인분 투입량 (g/ml/개)", min_value=0, format="%.1f")
            }
        )

        st.write("⏱️ **조리 공정 (SOP)**")
        edited_sop = st.data_editor(
            pd.DataFrame([{"time": "09:00", "cat": "Prep", "desc": "작업내용", "point": "체크"}]),
            num_rows="dynamic", use_container_width=True
        )
        
        if st.form_submit_button("💾 레시피 및 데이터 저장"):
            if nm:
                final_ings = []
                for _, row in edited_ing_bom.iterrows():
                    if row["재료명(검색)"] and row["1인분 투입량"] > 0:
                        final_ings.append({"name": row["재료명(검색)"], "qty": row["1인분 투입량"]})
                
                final_tasks = []
                for _, row in edited_sop.iterrows():
                    if row['desc'] != "작업내용":
                        final_tasks.append({"time": row['time'], "cat": row['cat'], "desc": row['desc'], "point": row['point']})
                
                st.session_state.recipe_db.append({
                    "name": nm, "main_cat": main_c, "sub_cat": sub_c, 
                    "ingredients": final_ings, "tasks": final_tasks
                })
                st.success(f"✅ [{nm}] 등록 완료!")

# =========================================================
# [TAB 4] 원가 관리 (수정사항 반영: 자동가격계산 + 검색UI)
# =========================================================
with menu_tabs[3]:
    st.subheader("💰 원가 분석 및 마진율 계산기")
    
    cost_t1, cost_t2 = st.tabs(["📊 식자재 단가표", "🧮 자동 원가 계산기"])
    
    with cost_t1:
        st.data_editor(st.session_state.ingredient_db, num_rows="dynamic", use_container_width=True)

    with cost_t2:
        # 모드 선택
        calc_mode = st.radio("분석 모드", ["단품 메뉴 분석", "세트/코스 메뉴 분석"], horizontal=True)
        
        # [수정 2] 드롭다운 제거 -> 검색 입력 방식 적용
        col_search, col_select = st.columns([1, 2])
        target_menus = []
        
        with col_search:
            menu_search_q = st.text_input("🔍 메뉴 검색 (엔터)", placeholder="예: 갈비")
            
            # DB에서 이름 검색
            all_menus = [r['name'] for r in st.session_state.recipe_db]
            filtered_menus = [m for m in all_menus if menu_search_q in m] if menu_search_q else all_menus

        with col_select:
            if calc_mode == "단품 메뉴 분석":
                # [수정 3] 용어 변경 '분석할 메뉴' -> '단품 메뉴 선택'
                sel = st.selectbox("단품 메뉴 선택", filtered_menus)
                if sel: target_menus = [sel]
            else:
                sel = st.multiselect("세트/코스 메뉴 선택", filtered_menus)
                target_menus = sel

        # [수정 1] 인분수 및 가격 자동 계산 로직
        st.divider()
        col_input1, col_input2, col_result_sales = st.columns(3)
        
        with col_input1:
            servings = st.number_input("판매 인분수(수량)", value=1, min_value=1, step=1)
            
        with col_input2:
            # 판매가는 1인분(1세트) 단가로 입력 받음
            unit_price_label = "1인분 판매 단가 (원)" if calc_mode == "단품 메뉴 분석" else "1세트 판매 단가 (원)"
            unit_sales_price = st.number_input(unit_price_label, value=15000, step=1000)
            
        with col_result_sales:
            # 총 판매가는 자동 계산 (Read-only 느낌으로 metric 사용)
            total_expected_sales = unit_sales_price * servings
            st.metric("총 예상 매출액 (자동 계산)", f"{int(total_expected_sales):,}원", help="단가 x 수량")

        st.divider()

        if target_menus:
            calculated_rows = []
            for m_name in target_menus:
                recipe_data = next((r for r in st.session_state.recipe_db if r['name'] == m_name), None)
                if recipe_data and 'ingredients' in recipe_data:
                    for ing in recipe_data['ingredients']:
                        ing_info = st.session_state.ingredient_db[st.session_state.ingredient_db['품목명'] == ing['name']]
                        if not ing_info.empty:
                            row = ing_info.iloc[0]
                            unit = str(row['규격']).lower().strip()
                            price = row['단가']
                            yield_rate = row['수율']
                            
                            cost = (price / 1000 * ing['qty']) if unit in ['kg', 'l', '리터'] else (price * ing['qty'])
                            if yield_rate > 0: cost = cost * (100/yield_rate)
                            
                            calculated_rows.append({
                                "구분": m_name, "재료명": ing['name'], 
                                "1인분 투입량": ing['qty'], "단위": "g/ml" if unit in ['kg','l'] else unit, 
                                "1인분 원가": int(cost)
                            })
            
            if calculated_rows:
                res_df = pd.DataFrame(calculated_rows)
                st.write("📝 **상세 원가 내역**")
                st.dataframe(res_df, use_container_width=True)
                
                # 최종 집계 (인분수 반영)
                total_cost_unit = res_df["1인분 원가"].sum() # 1인분 총 원가
                total_cost_final = total_cost_unit * servings # N인분 총 원가
                
                margin_final = total_expected_sales - total_cost_final
                rate_final = (total_cost_final / total_expected_sales * 100) if total_expected_sales > 0 else 0
                
                st.success(f"💰 수익성 분석 결과 ({servings}인분 기준)")
                m1, m2, m3 = st.columns(3)
                m1.metric("총 원가 합계", f"{int(total_cost_final):,}원")
                m2.metric("총 예상 마진", f"{int(margin_final):,}원", delta_color="normal")
                m3.metric("원가율", f"{rate_final:.1f}%", delta_color="inverse")
            else:
                st.warning("선택된 메뉴에 재료 정보가 없습니다.")

# [TAB 5] 입고 (준비 중)
with menu_tabs[4]: st.write("입고 관리 준비 중")
