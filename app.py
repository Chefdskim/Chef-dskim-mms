import streamlit as st
import pandas as pd
from datetime import datetime, time
import random

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

# 2. 식자재 DB
if 'ingredient_db' not in st.session_state:
    data = [
        {"품목명": "소갈비(Short Rib)", "규격": "kg", "단가": 35000, "수율": 100},
        {"품목명": "돼지갈비", "규격": "kg", "단가": 18000, "수율": 100},
        {"품목명": "진간장", "규격": "L", "단가": 4500, "수율": 100},
        {"품목명": "백설탕", "규격": "kg", "단가": 1800, "수율": 100},
        {"품목명": "물엿", "규격": "kg", "단가": 3000, "수율": 100},
        {"품목명": "참기름", "규격": "can", "단가": 55000, "수율": 100},
        {"품목명": "깐마늘", "규격": "kg", "단가": 8000, "수율": 95},
        {"품목명": "대파", "규격": "kg", "단가": 3500, "수율": 85},
        {"품목명": "양파", "규격": "kg", "단가": 1500, "수율": 90},
        {"품목명": "무", "규격": "kg", "단가": 1200, "수율": 85},
        {"품목명": "배", "규격": "kg", "단가": 5000, "수율": 80},
        {"품목명": "계란(특란)", "규격": "ea", "단가": 350, "수율": 100},
        {"품목명": "맛소금", "규격": "g", "단가": 12, "수율": 100},
        {"품목명": "쌀", "규격": "kg", "단가": 3000, "수율": 100},
        {"품목명": "김치", "규격": "kg", "단가": 5000, "수율": 100},
    ]
    st.session_state.ingredient_db = pd.DataFrame(data)

# 3. 재고 DB
if 'inventory_db' not in st.session_state:
    inv_data = st.session_state.ingredient_db.copy()
    inv_data['현재고'] = 10.0 
    inv_data['최종변동일'] = "-"
    st.session_state.inventory_db = inv_data[['품목명', '규격', '현재고', '최종변동일']]

# 4. 레시피 DB
if 'recipe_db' not in st.session_state:
    st.session_state.recipe_db = [
        {
            "name": "왕갈비탕", "main_cat": "🇰🇷 한식", "sub_cat": "국/찌개/전골/탕",
            "ingredients": [{"name": "소갈비(Short Rib)", "qty": 250}, {"name": "무", "qty": 150}, {"name": "대파", "qty": 40}, {"name": "깐마늘", "qty": 10}],
            "tasks": [{"time": "08:00", "cat": "Prep", "desc": "핏물 빼기", "point": "찬물 유수"}]
        },
        {
            "name": "공기밥", "main_cat": "🇰🇷 한식", "sub_cat": "밥/죽/면",
            "ingredients": [{"name": "쌀", "qty": 150}],
            "tasks": []
        },
        {
            "name": "배추김치(반찬)", "main_cat": "🇰🇷 한식", "sub_cat": "김치/장류",
            "ingredients": [{"name": "김치", "qty": 80}],
            "tasks": []
        }
    ]

# 5. 장바구니 세션 (원가용 / 판매용)
if 'cost_cart' not in st.session_state: st.session_state.cost_cart = [] # 원가 분석용 장바구니
if 'sell_cart' not in st.session_state: st.session_state.sell_cart = [] # 판매 등록용 장바구니

# 6. 기타
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
menu_tabs = st.tabs(["⏱️ 오퍼레이션", "📖 메뉴 & 레시피", "🧪 R&D/레시피 등록", "💰 원가 관리", "📸 입고 & 재고"])

# =========================================================
# [TAB 1~3] (기능 유지)
# =========================================================
with menu_tabs[0]: # 오퍼레이션
    st.subheader("📅 현장 오퍼레이션")
    with st.expander("➕ [작업 추가] 메뉴 검색", expanded=False):
        menu_names = [r['name'] for r in st.session_state.recipe_db]
        selected = st.multiselect("메뉴 선택", menu_names)
        if st.button("🚀 공정 추가") and selected: st.success("공정 추가됨")
    st.data_editor(st.session_state.schedule_df, num_rows="dynamic", use_container_width=True, hide_index=True)

with menu_tabs[1]: # 메뉴 책장
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
                    ing_display.append(f"{i['name']} {i['qty']}g/ml/ea")
                st.info(", ".join(ing_display) if ing_display else "등록된 재료 없음")

with menu_tabs[2]: # R&D
    st.subheader("🧪 신규 레시피 등록")
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
        empty_df = pd.DataFrame(columns=["재료명(검색)", "1인분 투입량"])
        edited_ing_bom = st.data_editor(
            empty_df, num_rows="dynamic", use_container_width=True,
            column_config={
                "재료명(검색)": st.column_config.SelectboxColumn("재료명", options=list(st.session_state.ingredient_db["품목명"].unique()), required=True),
                "1인분 투입량": st.column_config.NumberColumn("1인분 투입량 (g/ml/개)", min_value=0, format="%.1f")
            }
        )
        st.write("⏱️ **조리 공정 (SOP)**")
        edited_sop = st.data_editor(pd.DataFrame([{"time": "09:00", "cat": "Prep", "desc": "작업내용", "point": "체크"}]), num_rows="dynamic", use_container_width=True)
        if st.form_submit_button("💾 레시피 및 데이터 저장"):
            if nm:
                final_ings = [{"name": r["재료명(검색)"], "qty": r["1인분 투입량"]} for _, r in edited_ing_bom.iterrows() if r["재료명(검색)"]]
                final_tasks = [{"time": r['time'], "cat": r['cat'], "desc": r['desc'], "point": r['point']} for _, r in edited_sop.iterrows() if r['desc'] != "작업내용"]
                st.session_state.recipe_db.append({"name": nm, "main_cat": main_c, "sub_cat": sub_c, "ingredients": final_ings, "tasks": final_tasks})
                st.success(f"✅ [{nm}] 등록 완료!")

# =========================================================
# [TAB 4] 원가 관리 (장바구니 방식 적용)
# =========================================================
with menu_tabs[3]:
    st.subheader("💰 원가 분석 및 마진율 계산기")
    
    cost_t1, cost_t2 = st.tabs(["📊 식자재 단가표", "🧮 메뉴 원가 분석(단품/코스)"])
    
    with cost_t1:
        st.data_editor(st.session_state.ingredient_db, num_rows="dynamic", use_container_width=True)

    with cost_t2:
        # 2분할: 왼쪽(검색 및 담기) / 오른쪽(분석 결과)
        c_left, c_right = st.columns([1, 1])
        
        with c_left:
            st.markdown("#### 1. 메뉴 구성 (Search & Add)")
            st.caption("단품이든 세트든 검색해서 목록에 담아주세요.")
            
            # [검색]
            cost_search_q = st.text_input("🔍 메뉴 검색", placeholder="예: 갈비", key="cost_q")
            all_menus = [r['name'] for r in st.session_state.recipe_db]
            filtered_menus = [m for m in all_menus if cost_search_q in m] if cost_search_q else all_menus
            
            # [선택 & 담기]
            cost_target = st.selectbox("검색 결과 선택", filtered_menus, key="cost_sel")
            
            if st.button("⬇️ 목록에 담기", key="add_cost"):
                if cost_target not in st.session_state.cost_cart:
                    st.session_state.cost_cart.append(cost_target)
            
            st.divider()
            st.markdown("#### 2. 설정")
            servings = st.number_input("인분수", 1, 1000, 1, key="cost_serv")
            sales_price = st.number_input("총 판매가 (원)", 0, 10000000, 15000, 1000, key="cost_price")

        with c_right:
            st.markdown("#### 3. 분석 리스트 & 결과")
            
            # 장바구니 표시
            if st.session_state.cost_cart:
                st.write("📋 **분석 대상 목록**")
                for i, m in enumerate(st.session_state.cost_cart):
                    c1, c2 = st.columns([0.8, 0.2])
                    c1.text(f"{i+1}. {m}")
                    if c2.button("삭제", key=f"del_cost_{i}"):
                        st.session_state.cost_cart.pop(i)
                        st.rerun()
                
                if st.button("🗑️ 전체 비우기", key="clear_cost"):
                    st.session_state.cost_cart = []
                    st.rerun()
                
                st.divider()
                
                # 계산 로직
                calculated_rows = []
                for m_name in st.session_state.cost_cart:
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
                                
                                unit_display = "g/ml" if unit in ['kg', 'l', '리터'] else unit
                                calculated_rows.append({
                                    "구분": m_name, "재료명": ing['name'], 
                                    "1인분 투입량": ing['qty'], "단위": unit_display, "1인분 원가": int(cost)
                                })
                
                if calculated_rows:
                    res_df = pd.DataFrame(calculated_rows)
                    with st.expander("📝 상세 재료 원가 보기"):
                        st.dataframe(res_df, use_container_width=True)
                    
                    total_cost_unit = res_df["1인분 원가"].sum()
                    total_cost_final = total_cost_unit * servings
                    margin_final = sales_price - total_cost_final
                    rate_final = (total_cost_final / sales_price * 100) if sales_price > 0 else 0
                    
                    st.success(f"💰 분석 결과 ({servings}인분 기준)")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("총 원가", f"{int(total_cost_final):,}원")
                    m2.metric("예상 마진", f"{int(margin_final):,}원")
                    m3.metric("원가율", f"{rate_final:.1f}%", delta_color="inverse")
            else:
                st.info("왼쪽에서 메뉴를 검색하여 담아주세요.")

# =========================================================
# [TAB 5] 입고 & 재고 (장바구니 판매 방식 적용)
# =========================================================
with menu_tabs[4]:
    st.subheader("📸 스마트 입고 & 재고 관리")
    
    in_tab1, in_tab2, in_tab3 = st.tabs(["📥 입고 등록 (OCR)", "📤 판매/소진 등록 (차감)", "📦 재고 현황"])
    
    # [5-1] 입고 (기존 유지)
    with in_tab1:
        st.info("거래명세서 등록 (OCR 시뮬레이션)")
        if st.button("🔍 OCR 시뮬레이션 (랜덤 입고)"):
            sample = st.session_state.ingredient_db.sample(3)
            ocr_results = []
            for _, row in sample.iterrows():
                new_price = row['단가'] + random.choice([-500, 0, 500])
                ocr_results.append({"품목명": row['품목명'], "입고수량": 10, "입고단가": new_price})
            st.session_state.ocr_data = pd.DataFrame(ocr_results)

        if 'ocr_data' in st.session_state:
            edited_in = st.data_editor(st.session_state.ocr_data, num_rows="dynamic", use_container_width=True)
            if st.button("✅ 입고 확정"):
                for _, row in edited_in.iterrows():
                    item, qty, price = row['품목명'], row['입고수량'], row['입고단가']
                    if item in st.session_state.inventory_db['품목명'].values:
                        idx = st.session_state.inventory_db[st.session_state.inventory_db['품목명']==item].index[0]
                        st.session_state.inventory_db.at[idx, '현재고'] += qty
                        st.session_state.inventory_db.at[idx, '최종변동일'] = datetime.now().strftime('%Y-%m-%d')
                    if item in st.session_state.ingredient_db['품목명'].values:
                        idx_m = st.session_state.ingredient_db[st.session_state.ingredient_db['품목명']==item].index[0]
                        st.session_state.ingredient_db.at[idx_m, '단가'] = price
                st.success("입고 완료")
                del st.session_state.ocr_data
                st.rerun()

    # [5-2] 판매/소진 (장바구니 방식 적용 - 핵심 수정)
    with in_tab2:
        st.info("판매된 메뉴를 검색하여 목록에 담은 후, 한 번에 재고를 차감하세요.")
        
        col_sell_left, col_sell_right = st.columns([1, 1])
        
        with col_sell_left:
            st.markdown("#### 1. 판매 메뉴 등록")
            
            # [검색]
            sell_q = st.text_input("🔍 메뉴 검색", placeholder="예: 갈비", key="sell_q")
            all_menus_sell = [r['name'] for r in st.session_state.recipe_db]
            filtered_sell = [m for m in all_menus_sell if sell_q in m] if sell_q else all_menus_sell
            
            # [선택 & 수량]
            c_sel, c_qty = st.columns([0.7, 0.3])
            with c_sel:
                sell_target = st.selectbox("메뉴 선택", filtered_sell, key="sell_sel")
            with c_qty:
                sell_qty_input = st.number_input("수량", 1, 1000, 1, key="sell_qty_in")
            
            # [담기]
            if st.button("⬇️ 판매 리스트에 추가"):
                st.session_state.sell_cart.append({"menu": sell_target, "qty": sell_qty_input})
        
        with col_sell_right:
            st.markdown("#### 2. 판매 예정 리스트")
            
            if st.session_state.sell_cart:
                # 리스트 표시 (Dataframe)
                cart_df = pd.DataFrame(st.session_state.sell_cart)
                st.dataframe(cart_df, use_container_width=True, hide_index=True)
                
                c_clear, c_confirm = st.columns(2)
                with c_clear:
                    if st.button("🗑️ 리스트 비우기"):
                        st.session_state.sell_cart = []
                        st.rerun()
                with c_confirm:
                    if st.button("🚀 재고 차감 실행"):
                        log_msg = []
                        for item in st.session_state.sell_cart:
                            m_name = item['menu']
                            s_qty = item['qty']
                            
                            recipe = next((r for r in st.session_state.recipe_db if r['name'] == m_name), None)
                            if recipe and 'ingredients' in recipe:
                                for ing in recipe['ingredients']:
                                    ing_name = ing['name']
                                    inv_row = st.session_state.inventory_db[st.session_state.inventory_db['품목명'] == ing_name]
                                    if not inv_row.empty:
                                        idx = inv_row.index[0]
                                        unit = str(inv_row.iloc[0]['규격']).lower()
                                        deduct = (ing['qty'] * s_qty) / 1000 if unit in ['kg','l','리터'] else (ing['qty'] * s_qty)
                                        
                                        st.session_state.inventory_db.at[idx, '현재고'] -= deduct
                                        st.session_state.inventory_db.at[idx, '최종변동일'] = datetime.now().strftime('%Y-%m-%d')
                                        log_msg.append(f"{ing_name}: -{deduct:.1f}")
                        
                        st.session_state.sell_cart = [] # 처리 후 비움
                        st.success("✅ 판매 처리 완료! 재고가 차감되었습니다.")
                        with st.expander("차감 상세 로그"):
                            st.write(", ".join(log_msg))
                        st.rerun()
            else:
                st.info("판매된 메뉴를 추가해주세요.")

    # [5-3] 재고 현황
    with in_tab3:
        st.write("📊 **실시간 재고 현황**")
        def highlight_low_stock(val): return f'color: red' if val < 2 else 'color: black'
        st.dataframe(
            st.session_state.inventory_db.style.map(highlight_low_stock, subset=['현재고']), 
            use_container_width=True,
            column_config={"현재고": st.column_config.NumberColumn("현재고", format="%.2f", help="2 미만 시 붉은색")}
        )
        if st.button("🔄 재고 새로고침"): st.rerun()
