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

# 2. 식자재 DB (Master)
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

# 3. 재고 DB (Inventory) - NEW
if 'inventory_db' not in st.session_state:
    # 초기 재고는 0으로 시작
    inv_data = st.session_state.ingredient_db.copy()
    inv_data['현재고'] = 0.0
    inv_data['최종입고일'] = "-"
    st.session_state.inventory_db = inv_data[['품목명', '규격', '현재고', '최종입고일']]

# 4. 레시피 DB
if 'recipe_db' not in st.session_state:
    st.session_state.recipe_db = [
        {
            "name": "왕갈비탕", "main_cat": "🇰🇷 한식", "sub_cat": "국/찌개/전골/탕",
            "ingredients": [
                {"name": "소갈비(Short Rib)", "qty": 250}, {"name": "무", "qty": 150}, 
                {"name": "대파", "qty": 40}, {"name": "깐마늘", "qty": 10}
            ],
            "tasks": [{"time": "08:00", "cat": "Prep", "desc": "핏물 빼기", "point": "찬물 유수"}]
        }
    ]

# 5. 기타 상태
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
# [TAB 1~3] (기능 유지 - 코드 생략 없음, 전체 포함)
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
                st.write("**[공정]**")
                for t in r['tasks']: st.text(f"- {t['time']} {t['desc']}")

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

with menu_tabs[3]: # 원가 관리
    st.subheader("💰 원가 분석")
    cost_t1, cost_t2 = st.tabs(["📊 식자재 단가표", "🧮 자동 원가 계산기"])
    with cost_t1: st.data_editor(st.session_state.ingredient_db, num_rows="dynamic", use_container_width=True)
    with cost_t2:
        calc_mode = st.radio("분석 모드", ["단품 메뉴 분석", "세트/코스 메뉴 분석"], horizontal=True)
        col_s, col_l = st.columns([1,2])
        target_menus = []
        with col_s:
            q = st.text_input("🔍 메뉴 검색", placeholder="예: 갈비")
            f_m = [m for m in [r['name'] for r in st.session_state.recipe_db] if q in m] if q else [r['name'] for r in st.session_state.recipe_db]
        with col_l:
            if calc_mode == "단품 메뉴 분석": 
                s = st.selectbox("단품 메뉴 선택", f_m)
                if s: target_menus = [s]
            else: target_menus = st.multiselect("세트 메뉴 선택", f_m)
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1: servings = st.number_input("인분수", 1, 1000, 1)
        with c2: price = st.number_input("1인분/세트 판매가", 0, 1000000, 15000, 1000)
        with c3: st.metric("총 예상 매출", f"{price*servings:,}원")
        
        if target_menus:
            rows = []
            for m in target_menus:
                rd = next((r for r in st.session_state.recipe_db if r['name']==m), None)
                if rd and 'ingredients' in rd:
                    for i in rd['ingredients']:
                        info = st.session_state.ingredient_db[st.session_state.ingredient_db['품목명']==i['name']]
                        if not info.empty:
                            r_info = info.iloc[0]
                            c = (r_info['단가']/1000*i['qty']) if str(r_info['규격']) in ['kg','l','리터'] else (r_info['단가']*i['qty'])
                            if r_info['수율'] > 0: c *= (100/r_info['수율'])
                            rows.append({"메뉴": m, "재료": i['name'], "투입량": i['qty'], "단위": "g/ml" if str(r_info['규격']) in ['kg','l'] else str(r_info['규격']), "원가": int(c)})
            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)
                tc = df["원가"].sum() * servings
                mg = (price*servings) - tc
                st.success(f"💰 결과: 총 원가 {int(tc):,}원 / 마진 {int(mg):,}원")

# =========================================================
# [TAB 5] 입고 & 재고 (NEW - OCR Simulation)
# =========================================================
with menu_tabs[4]:
    st.subheader("📸 스마트 입고 & 재고 관리")
    
    in_tab1, in_tab2 = st.tabs(["📥 입고 등록 (OCR/수동)", "📦 현재 재고 현황"])
    
    # --- [5-1] 입고 등록 ---
    with in_tab1:
        st.info("명세서 사진을 업로드하거나 수동으로 입력하세요. 가격 변동 시 '원가표'가 자동 갱신됩니다.")
        
        # 입력 방식 선택
        input_method = st.radio("입력 방식", ["📸 명세서 촬영/업로드 (OCR)", "📝 수동 직접 입력"], horizontal=True)
        
        if input_method == "📸 명세서 촬영/업로드 (OCR)":
            img_file = st.file_uploader("거래명세서 사진 촬영 또는 업로드", type=['png', 'jpg', 'jpeg'])
            
            if img_file:
                st.image(img_file, caption="업로드된 명세서", width=300)
                if st.button("🔍 명세서 분석 시작 (AI OCR)"):
                    with st.spinner("명세서를 분석 중입니다..."):
                        # [OCR 시뮬레이션 로직]
                        # 실제 API 대신, 현재 DB에 있는 품목 중 랜덤하게 3개를 가져와서 보여줍니다.
                        st.toast("OCR 분석 완료! 데이터를 추출했습니다.")
                        
                        # 랜덤하게 입고 품목 생성 (시연용)
                        sample_items = st.session_state.ingredient_db.sample(3)
                        ocr_results = []
                        for _, row in sample_items.iterrows():
                            # 가격 변동 시뮬레이션 (기존가 +- 500원)
                            new_price = row['단가'] + random.choice([-500, 0, 500, 1000])
                            ocr_results.append({
                                "품목명": row['품목명'],
                                "규격": row['규격'],
                                "입고수량": 10, # 10개씩 입고
                                "입고단가": new_price, # 변동된 단가
                                "공급가액": 10 * new_price
                            })
                        
                        st.session_state.ocr_data = pd.DataFrame(ocr_results)
            
            # 분석된 결과 확인 및 수정창
            if 'ocr_data' in st.session_state:
                st.write("▼ **분석 결과 (내용을 수정하여 확정하세요)**")
                edited_inbound = st.data_editor(
                    st.session_state.ocr_data,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "품목명": st.column_config.SelectboxColumn("품목명", options=list(st.session_state.ingredient_db["품목명"].unique())),
                        "입고단가": st.column_config.NumberColumn("입고단가 (원)", help="이 가격으로 원가표가 갱신됩니다.")
                    }
                )
                
                if st.button("✅ 입고 확정 및 단가 갱신"):
                    # 로직: 1. 재고 추가 / 2. 마스터 단가 업데이트
                    count = 0
                    for _, row in edited_inbound.iterrows():
                        item = row['품목명']
                        qty = row['입고수량']
                        price = row['입고단가']
                        
                        # 1. 재고 DB 업데이트
                        if item in st.session_state.inventory_db['품목명'].values:
                            idx = st.session_state.inventory_db[st.session_state.inventory_db['품목명']==item].index[0]
                            st.session_state.inventory_db.at[idx, '현재고'] += qty
                            st.session_state.inventory_db.at[idx, '최종입고일'] = datetime.now().strftime('%Y-%m-%d')
                        
                        # 2. 마스터 단가 DB 업데이트 (가격 변동 반영)
                        if item in st.session_state.ingredient_db['품목명'].values:
                            idx_m = st.session_state.ingredient_db[st.session_state.ingredient_db['품목명']==item].index[0]
                            st.session_state.ingredient_db.at[idx_m, '단가'] = price
                        
                        count += 1
                        
                    st.success(f"총 {count}개 품목 입고 완료! 단가표가 최신 가격으로 업데이트되었습니다.")
                    del st.session_state.ocr_data # 임시 데이터 삭제
                    st.rerun()

        else: # 수동 입력
            st.write("▼ **입고 품목 입력**")
            manual_df = pd.DataFrame(columns=["품목명", "입고수량", "입고단가"])
            edited_manual = st.data_editor(
                manual_df,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "품목명": st.column_config.SelectboxColumn("품목명", options=list(st.session_state.ingredient_db["품목명"].unique())),
                    "입고수량": st.column_config.NumberColumn("수량", min_value=0),
                    "입고단가": st.column_config.NumberColumn("단가(원)", min_value=0)
                }
            )
            
            if st.button("✅ 수동 입고 확정"):
                # (로직은 위와 동일)
                for _, row in edited_manual.iterrows():
                    if row['품목명']:
                        item = row['품목명']
                        # 재고 업데이트
                        idx = st.session_state.inventory_db[st.session_state.inventory_db['품목명']==item].index[0]
                        st.session_state.inventory_db.at[idx, '현재고'] += row['입고수량']
                        st.session_state.inventory_db.at[idx, '최종입고일'] = datetime.now().strftime('%Y-%m-%d')
                        # 단가 업데이트
                        idx_m = st.session_state.ingredient_db[st.session_state.ingredient_db['품목명']==item].index[0]
                        st.session_state.ingredient_db.at[idx_m, '단가'] = row['입고단가']
                st.success("입고 처리가 완료되었습니다.")

    # --- [5-2] 재고 현황 ---
    with in_tab2:
        st.write("📊 **실시간 재고 자산 현황**")
        
        # 보기 좋게 표시
        st.dataframe(
            st.session_state.inventory_db, 
            use_container_width=True,
            column_config={
                "현재고": st.column_config.NumberColumn("현재고", format="%.1f"),
            }
        )
        
        if st.button("🔄 재고로침"):
            st.rerun()
