import streamlit as st

# 셰프님의 엑셀 데이터를 정밀 이식한 마스터 리스트 (주요 품목 우선 등록)
INGREDIENTS = {
    "갈비": {"price": 13000, "yield": 50.4},
    "갈비(원물)": {"price": 13000, "yield": 50.4},
    "차돌박이": {"price": 18000, "yield": 100},
    "쪽파": {"price": 4500, "yield": 85},
    "실파": {"price": 4500, "yield": 85},
    "양파": {"price": 1200, "yield": 90},
    "데리야끼소스": {"price": 8500, "yield": 100},
    "미림": {"price": 3200, "yield": 100},
    "꽃소금": {"price": 1100, "yield": 100},
    "대파": {"price": 3200, "yield": 88},
    "마늘": {"price": 8500, "yield": 95}
}

st.set_page_config(page_title="Chef_dskim MMS", layout="wide")
st.title("👨‍🍳 Chef_dskim 스마트 원가 관리")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📸 명세표 촬영")
    img_file = st.camera_input("")

with col2:
    st.header("🔍 품목 입력 및 원가 대조")
    
    # 셰프님이 검색하기 편하게 '자동 완성' 기능이 있는 선택창으로 변경했습니다.
    # 직접 타이핑하면 목록에서 걸러줍니다.
    input_name = st.selectbox("품목명을 선택하거나 입력하세요", ["직접 입력"] + list(INGREDIENTS.keys()))
    
    if input_name == "직접 입력":
        custom_name = st.text_input("새로운 품목명을 적어주세요")
        base = {"price": 0, "yield": 100}
    else:
        base = INGREDIENTS[input_name]
        st.success(f"✅ '{input_name}' 엑셀 데이터 로드 완료")

    price_input = st.number_input("오늘의 입고가 입력", value=float(base["price"]))
    yield_input = st.number_input("수율 설정 (%)", value=float(base["yield"]), min_value=1.0)
    
    # 셰프님 엑셀 정밀 수식
    real_cost = price_input / (yield_input / 100)
    
    st.divider()
    st.subheader(f"📊 검증 결과")
    
    st.metric("실질 정육 원가", f"{real_cost:,.0f}원")
    st.caption(f"상세 계산: {price_input:,}원 ÷ {yield_input}% = {real_cost:,.2f}원")

    if base["price"] > 0:
        diff = price_input - base["price"]
        st.metric("기준가 대비 변동", f"{int(diff):,}원", delta=int(diff), delta_color="inverse")
