import streamlit as st

# 셰프님 엑셀 데이터
INGREDIENTS = {
    "갈비(원물)": {"price": 13000, "yield": 50.4},
    "차돌박이": {"price": 18000, "yield": 100},
    "쪽파(실파)": {"price": 4500, "yield": 85}
}

st.set_page_config(page_title="Chef_dskim MMS", layout="wide") # 화면 넓게 쓰기
st.title("👨‍🍳 Chef_dskim 통합 관리 시스템")

# 왼쪽/오른쪽 칸 나누기
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📸 명세표 촬영")
    img_file = st.camera_input("")

with col2:
    st.header("🔍 데이터 대조")
    item = st.selectbox("품목을 선택하세요", list(INGREDIENTS.keys()))
    
    base = INGREDIENTS[item]
    price_input = st.number_input("현재 입고가 입력", value=base["price"])
    
    # 셰프님 엑셀 수식 적용
    real_cost = price_input / (base["yield"] / 100)
    
    st.divider()
    st.subheader(f"📊 {item} 검증 결과")
    st.metric("실질 정육 원가", f"{int(real_cost):,}원")
    st.info(f"💡 엑셀 기준 수율: {base['yield']}%")
