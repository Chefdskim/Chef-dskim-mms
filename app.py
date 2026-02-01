import streamlit as st

# 셰프님의 엑셀 데이터를 기반으로 한 기준 정보 (147종 확장을 위한 구조)
# 여기에 없는 품목을 적으면 기본 수율 100%로 계산됩니다.
INGREDIENTS = {
    "갈비(원물)": {"price": 13000, "yield": 50.4},
    "차돌박이": {"price": 18000, "yield": 100},
    "쪽파(실파)": {"price": 4500, "yield": 85},
    "양파": {"price": 1200, "yield": 90},
    "데리야끼소스": {"price": 8500, "yield": 100}
}

st.set_page_config(page_title="Chef_dskim MMS", layout="wide")
st.title("👨‍🍳 Chef_dskim 스마트 원가 관리")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📸 명세표 촬영")
    img_file = st.camera_input("")

with col2:
    st.header("🔍 품목 입력 및 원가 대조")
    
    # 직접 품목명을 적을 수 있는 입력창 추가
    input_name = st.text_input("확인할 품목명을 입력하세요 (예: 갈비)", "")
    
    # 셰프님이 입력한 품목이 데이터에 있는지 확인
    if input_name in INGREDIENTS:
        base = INGREDIENTS[input_name]
        st.success(f"✅ '{input_name}' 데이터를 찾았습니다. (기준가: {base['price']:,}원 / 수율: {base['yield']}%)")
    elif input_name != "":
        # 데이터에 없는 품목일 경우 임시 설정
        base = {"price": 0, "yield": 100}
        st.warning(f"⚠️ '{input_name}'은 등록되지 않은 품목입니다. 수율을 직접 조정하세요.")
    else:
        # 입력이 없을 때 기본값
        base = {"price": 0, "yield": 100}

    # 입고가 및 수율 조정 (노트북에서 잘 보이도록 배치)
    price_input = st.number_input("오늘의 입고가 입력", value=float(base["price"]))
    yield_input = st.number_input("수율 설정 (%)", value=float(base["yield"]), min_value=1.0, max_value=100.0)
    
    # 셰프님 엑셀 정밀 수식: 입고가 / (수율 / 100)
    real_cost = price_input / (yield_input / 100)
    
    st.divider()
    st.subheader(f"📊 {input_name if input_name else '품목'} 검증 결과")
    
    # 28,769원처럼 소수점까지 정확하게 표시
    st.metric("실질 정육 원가", f"{real_cost:,.0f}원")
    st.caption(f"상세 계산: {price_input:,}원 ÷ {yield_input}% = {real_cost:,.2f}원")

    if base["price"] > 0:
        diff = price_input - base["price"]
        st.metric("기준가 대비 변동", f"{int(diff):,}원", delta=int(diff), delta_color="inverse")
