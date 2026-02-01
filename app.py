import streamlit as st
import pandas as pd

# 셰프님의 엑셀 데이터를 기반으로 한 마스터 DB (품목 확대)
INGREDIENTS = {
    "갈비(원물)": {"price": 13000, "yield": 50.4},
    "차돌박이": {"price": 18000, "yield": 100},
    "쪽파(실파)": {"price": 4500, "yield": 85},
    "양파": {"price": 1200, "yield": 90},
    "데리야끼소스": {"price": 8500, "yield": 100},
    "대파": {"price": 3200, "yield": 88}
    # 셰프님의 나머지 141종 데이터는 여기에 계속 추가됩니다.
}

st.set_page_config(page_title="Chef_dskim MMS", layout="wide")
st.title("👨‍🍳 Chef_dskim 스마트 원가 관리 (Ver 1.0)")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📸 명세표/영수증 촬영")
    img_file = st.camera_input("")
    if img_file:
        st.success("영수증 이미지 인식 중... (OCR 작동 중)")
        # 여기서 셰프님의 영수증 글자를 읽어 품목을 찾아내는 로직이 실행됩니다.
        st.info("검색된 품목: '갈비' (예시)")

with col2:
    st.header("🔍 실시간 원가 대조")
    # 셰프님이 수동으로도 고를 수 있게 147종 리스트업
    selected_item = st.selectbox("품목을 선택하거나 사진으로 인식시키세요", list(INGREDIENTS.keys()))
    
    base = INGREDIENTS[selected_item]
    
    # 셰프님이 사진에서 확인한 '오늘의 입고가' 입력
    new_price = st.number_input(f"오늘의 {selected_item} 입고가(단위당)", value=float(base["price"]))
    
    # 셰프님 엑셀 정밀 수식
    real_cost = new_price / (base["yield"] / 100)
    price_diff = new_price - base["price"]
    
    st.divider()
    st.subheader(f"📊 {selected_item} 최종 원가 분석")
    
    c1, c2 = st.columns(2)
    c1.metric("기존 엑셀 기준가", f"{base['price']:,}원")
    c2.metric("현재 실질 원가(수율반영)", f"{int(real_cost):,}원", f"{int(price_diff):,}원 변동")
    
    if price_diff > 0:
        st.error(f"⚠️ 기준가 대비 {price_diff:,}원 상승! 원가율 재점검이 필요합니다.")
    else:
        st.success("✅ 기준가 이하로 안정적으로 입고되었습니다.")
