import streamlit as st
import pandas as pd
from datetime import datetime, time
import random
import os
import json

# 1. 페이지 설정
st.set_page_config(page_title="Chef_dskim 통합 관리 시스템", layout="wide")

# =========================================================
# [파일 저장/로드 시스템] - 핵심 엔진
# =========================================================
DATA_PATH = {
    "ingredients": "db_ingredients.csv",
    "inventory": "db_inventory.csv",
    "recipes": "db_recipes.json"
}

# (1) 시간 객체 직렬화 헬퍼 (JSON 저장용)
class TimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, time):
            return obj.strftime('%H:%M')
        return super().default(obj)

# (2) 데이터 저장 함수
def save_data():
    # 1. 식자재 DB (CSV)
    if 'ingredient_db' in st.session_state:
        st.session_state.ingredient_db.to_csv(DATA_PATH['ingredients'], index=False)
    # 2. 재고 DB (CSV)
    if 'inventory_db' in st.session_state:
        st.session_state.inventory_db.to_csv(DATA_PATH['inventory'], index=False)
    # 3. 레시피 DB (JSON)
    if 'recipe_db' in st.session_state:
        with open(DATA_PATH['recipes'], 'w', encoding='utf-8') as f:
            json.dump(st.session_state.recipe_db, f, cls=TimeEncoder, ensure_ascii=False, indent=4)

# (3) 데이터 로드 및 초기화 함수
def load_and_init_data():
    # A. 카테고리 (고정값)
    global CATEGORY_TREE
    CATEGORY_TREE = {
        "🇰🇷 한식": ["국/찌개/전골/탕", "찜", "구이", "조림", "볶음", "무침/나물", "김치/장류", "밥/죽/면"],
        "🇯🇵 일식": ["사시미/스시", "구이(야키)", "튀김(아게)", "찜(무시)", "조림(니모노)", "면류(라멘/소바)", "돈부리"],
        "🇨🇳 중식": ["튀김/볶음", "탕/찜", "냉채", "면류", "만두/딤섬"],
        "🍝 양식": ["에피타이저", "파스타", "스테이크/메인", "스튜/수프", "샐러드"],
        "🍞 베이커리": ["제빵(Bread)", "제과(Cake/Cookie)", "디저트", "샌드위치"],
        "🍷 주류/음료": ["와인", "사케", "전통주", "칵테일", "커피/음료"],
        "📦 기타": ["소스/드레싱", "가니쉬", "향신료 배합", "이유식/환자식"]
    }

    # B. 식자재 DB 로드
    if os.path.exists(DATA_PATH['ingredients']):
        st.session_state.ingredient_db = pd.read_csv(DATA_PATH['ingredients'])
    elif 'ingredient_db' not in st.session_state:
        # 파일 없으면 기초 데이터 생성
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
        save_data() # 초기값 저장

    # C. 재고 DB 로드
    if os.path.exists(DATA_PATH['inventory']):
        st.session_state.inventory_db = pd.read_csv(DATA_PATH['inventory'])
    elif 'inventory_db' not in st.session_state:
        inv_data = st.session_state.ingredient_db.copy()
        inv_data['현재고'] = 0.0 
        inv_data['최종변동일'] = "-"
        st.session_state.inventory_db = inv_data[['품목명', '규격', '현재고', '최종변동일']]
        save_data()

    # D. 레시피 DB 로드
    if os.path.exists(DATA_PATH['recipes']):
        with open(DATA_PATH['recipes'], 'r', encoding='utf-8') as f:
            st.session_state.recipe_db = json.load(f)
    elif 'recipe_db' not in st.session_state:
        st.session_state.recipe_db = [
            {
                "name": "왕갈비탕", "main_cat": "🇰🇷 한식", "sub_cat": "국/찌개/전골/탕",
                "ingredients": [{"name": "소갈비(Short Rib)", "qty": 250}, {"name": "무", "qty": 150}, {"name": "대파", "qty": 40}, {"name": "깐마늘", "qty": 10}],
                "tasks": [{"time": "08:00", "cat": "Prep", "desc": "핏물 빼기", "point": "찬물 유수"}]
            }
        ]
        save_data()

    # E. 기타 세션 초기화
    if 'cost_cart' not in st.session_state: st.session_state.cost_cart = []
    if 'sell_cart' not in st.session_state: st.session_state.sell_cart = []
    if 'schedule_df' not in st.session_state:
        st.session_state.schedule_df = pd.DataFrame([{"시작 시간": time(9,0), "종료 시간": time(9,30), "구분": "Prep", "세부 작업 내용": "오픈 준비", "체크 포인트": "온도", "완료": False}])
    if 'nav_depth' not in st.session_state: st.session_state.nav_depth = 0
    if 'selected_main' not in st.session_state: st.session_state.selected_main = ""
    if 'selected_sub' not in st.session_state: st.session_state.selected_sub = ""

# 앱 실행 시 최초 로드 실행
load_and_init_data()

# =========================================================
# 사이드바 & 헤더
# =========================================================
with st.sidebar:
    st.header("📊 시스템 상태")
    st.info(f"오늘: {datetime.now().strftime('%Y-%m-%d')}")
    st.success("✅ 데이터 저장소 연결됨")
    
    st.divider()
    if st.button("💾 수동 저장 (강제)"):
        save_data()
        st.toast("모든 데이터가 안전하게 저장되었습니다.")
        
    if st.button("🏠 홈으로"): st.session_state.nav_depth = 0; st.rerun()
    
    with st.expander("⚠ 위험 구역"):
        if st.button("🔥 공장 초기화 (데이터 삭제)"):
            if os.path.exists(DATA_PATH['ingredients']): os.remove(DATA_PATH['ingredients'])
            if os.path.exists(DATA_PATH['inventory']): os.remove(DATA_PATH['inventory'])
            if os.path.exists(DATA_PATH['recipes']): os.remove(DATA_PATH['recipes'])
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

st.title("👨‍🍳 Chef_dskim 통합 관리 시스템")
menu_tabs = st.tabs(["⏱️ 오퍼레이션", "📖 메뉴 & 레시피", "🧪 R&D/레시피 등록", "💰 원가 관리", "📸 입고 & 재고"])

# =========================================================
# [TAB 1] 오퍼레이션 (로드된 데이터 사용)
# =========================================================
with menu_tabs[0]:
    st.subheader("📅 현장 오퍼레이션")
    with st.expander("➕ [작업 추가] 메뉴 검색", expanded=False):
        menu_names = [r['name'] for r in st.session_state.recipe_db]
        selected = st.multiselect("메뉴 선택", menu_names)
        if st.button("🚀 공정 추가") and selected:
            new_rows = []
            for m_name in selected:
                target_recipe = next((item for item in st.session_state.recipe_db if item["name"] == m_name), None)
                if target_recipe:
                    for task in target_recipe['tasks']:
                        # JSON 로드 시 시간은 문자열이므로 변환 필요
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
                st.success("공정 추가됨")
                # 타임테이블은 매일 초기화되므로 굳이 파일저장 안해도 되지만, 필요 시 여기서 save_data 호출
    
    edited_schedule = st.data_editor(
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
    st.session_state.schedule_df = edited_schedule

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
                    ing_display.append(f"{i['name']} {i['qty']}g/ml/ea")
                st.info(", ".join(ing_display) if ing_display else "등록된 재료 없음")
                st.write("**[공정]**")
                for t in r['tasks']: st.text(f"- {t['time']} {t['desc']}")

# =========================================================
# [TAB 3] R&D (저장 기능 적용)
# =========================================================
with menu_tabs[2]:
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
                
                save_data() # [핵심] 파일로 영구 저장
                st.success(f"✅ [{nm}] 저장 완료! (파일에 기록됨)")

# =========================================================
# [TAB 4] 원가 관리
# =========================================================
with menu_tabs[3]:
    st.subheader("💰 원가 분석")
    cost_t1, cost_t2 = st.tabs(["📊 식자재 단가표", "🧮 메뉴 원가 분석"])
    
    with cost_t1:
        edited_ing_db = st.data_editor(st.session_state.ingredient_db, num_rows="dynamic", use_container_width=True)
        # 단가표 수정 시 자동 저장
        if not edited_ing_db.equals(st.session_state.ingredient_db):
            st.session_state.ingredient_db = edited_ing_db
            save_data() # 저장
    
    with cost_t2:
        c_left, c_right = st.columns([1, 1])
        with c_left:
            st.markdown("#### 1. 메뉴 구성")
            cost_search_q = st.text_input("🔍 메뉴 검색", placeholder="예: 갈비", key="cost_q")
            all_menus = [r['name'] for r in st.session_state.recipe_db]
            filtered_menus = [m for m in all_menus if cost_search_q in m] if cost_search_q else all_menus
            cost_target = st.selectbox("검색 결과 선택", filtered_menus, key="cost_sel")
            if st.button("⬇️ 목록에 담기", key="add_cost"):
                if cost_target not in st.session_state.cost_cart: st.session_state.cost_cart.append(cost_target)
            st.divider()
            servings = st.number_input("인분수", 1, 1000, 1, key="cost_serv")
            sales_price = st.number_input("총 판매가 (원)", 0, 10000000, 15000, 1000, key="cost_price")
        
        with c_right:
            st.markdown("#### 2. 분석 결과")
            if st.session_state.cost_cart:
                st.write("📋 **대상 목록**")
                for i, m in enumerate(st.session_state.cost_cart):
                    c1, c2 = st.columns([0.8, 0.2])
                    c1.text(f"- {m}")
                    if c2.button("X", key=f"del_cost_{i}"):
                        st.session_state.cost_cart.pop(i); st.rerun()
                if st.button("🗑️ 비우기", key="clear_cost"): st.session_state.cost_cart = []; st.rerun()
                
                st.divider()
                calculated_rows = []
                for m_name in st.session_state.cost_cart:
                    recipe_data = next((r for r in st.session_state.recipe_db if r['name'] == m_name), None)
                    if recipe_data and 'ingredients' in recipe_data:
                        for ing in recipe_data['ingredients']:
                            ing_info = st.session_state.ingredient_db[st.session_state.ingredient_db['품목명'] == ing['name']]
                            if not ing_info.empty:
                                row = ing_info.iloc[0]
                                unit = str(row['규격']).lower().strip()
                                cost = (row['단가']/1000*ing['qty']) if unit in ['kg','l','리터'] else (row['단가']*ing['qty'])
                                if row['수율'] > 0: cost *= (100/row['수율'])
                                unit_display = "g/ml" if unit in ['kg','l'] else unit
                                calculated_rows.append({"구분": m_name, "재료명": ing['name'], "투입": ing['qty'], "단위": unit_display, "원가": int(cost)})
                
                if calculated_rows:
                    res_df = pd.DataFrame(calculated_rows)
                    with st.expander("상세 내역"): st.dataframe(res_df)
                    tc = res_df["원가"].sum() * servings
                    mg = sales_price - tc
                    rate = (tc / sales_price * 100) if sales_price > 0 else 0
                    st.success(f"💰 결과 ({servings}인분)")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("총 원가", f"{int(tc):,}원")
                    m2.metric("마진", f"{int(mg):,}원")
                    m3.metric("원가율", f"{rate:.1f}%", delta_color="inverse")

# =========================================================
# [TAB 5] 입고 & 재고 (저장 기능 적용)
# =========================================================
with menu_tabs[4]:
    st.subheader("📸 스마트 입고 & 재고 관리")
    in_tab1, in_tab2, in_tab3 = st.tabs(["📥 입고 등록 (OCR)", "📤 판매/소진 등록", "📦 재고 현황"])
    
    with in_tab1:
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
                
                save_data() # [핵심] 저장
                st.success("입고 및 저장 완료")
                del st.session_state.ocr_data
                st.rerun()

    with in_tab2:
        col_sell_left, col_sell_right = st.columns([1, 1])
        with col_sell_left:
            st.markdown("#### 1. 판매 메뉴 등록")
            sell_q = st.text_input("🔍 메뉴 검색", placeholder="예: 갈비", key="sell_q")
            all_menus_sell = [r['name'] for r in st.session_state.recipe_db]
            filtered_sell = [m for m in all_menus_sell if sell_q in m] if sell_q else all_menus_sell
            c_sel, c_qty = st.columns([0.7, 0.3])
            with c_sel: sell_target = st.selectbox("메뉴 선택", filtered_sell, key="sell_sel")
            with c_qty: sell_qty_input = st.number_input("수량", 1, 1000, 1, key="sell_qty_in")
            if st.button("⬇️ 리스트 추가"):
                st.session_state.sell_cart.append({"menu": sell_target, "qty": sell_qty_input})
        
        with col_sell_right:
            st.markdown("#### 2. 판매 예정 리스트")
            if st.session_state.sell_cart:
                st.dataframe(pd.DataFrame(st.session_state.sell_cart), use_container_width=True, hide_index=True)
                c_clear, c_confirm = st.columns(2)
                with c_clear:
                    if st.button("🗑️ 비우기"): st.session_state.sell_cart = []; st.rerun()
                with c_confirm:
                    if st.button("🚀 재고 차감 실행"):
                        for item in st.session_state.sell_cart:
                            recipe = next((r for r in st.session_state.recipe_db if r['name'] == item['menu']), None)
                            if recipe and 'ingredients' in recipe:
                                for ing in recipe['ingredients']:
                                    inv_row = st.session_state.inventory_db[st.session_state.inventory_db['품목명'] == ing['name']]
                                    if not inv_row.empty:
                                        idx = inv_row.index[0]
                                        unit = str(inv_row.iloc[0]['규격']).lower()
                                        deduct = (ing['qty'] * item['qty']) / 1000 if unit in ['kg','l','리터'] else (ing['qty'] * item['qty'])
                                        st.session_state.inventory_db.at[idx, '현재고'] -= deduct
                        
                        save_data() # [핵심] 저장
                        st.session_state.sell_cart = []
                        st.success("재고 차감 및 저장 완료")
                        st.rerun()

    with in_tab3:
        st.write("📊 **실시간 재고 현황**")
        def highlight_low_stock(val): return f'color: red' if val < 2 else 'color: black'
        st.dataframe(st.session_state.inventory_db.style.map(highlight_low_stock, subset=['현재고']), use_container_width=True)
        if st.button("🔄 새로고침"): st.rerun()
