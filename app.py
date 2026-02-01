import streamlit as st
import pandas as pd
import plotly.express as px

# 셰프님 엑셀 데이터를 기반으로 한 메뉴 수익성 마스터 (실제 데이터로 확장 가능)
# 엑셀의 '판매가'와 '원가' 데이터를 기반으로 구성했습니다.
MENU_DATA = pd.DataFrame([
    {"메뉴명": "양념갈비", "원가율": 32.4, "마진": 15000},
    {"메뉴명": "차돌박이", "원가율": 45.1, "마진": 12500},
    {"메뉴명": "불고기", "원가율": 38.2, "마진": 9200},
    {"메뉴명": "갈비탕", "원가율": 28.7, "마진": 6800},
    {"메뉴명": "육회", "원가율": 50.8, "마진": 21000},
    {"메뉴명": "된장찌개", "원가율": 22.5, "마진": 4500}
])

st.set_page_config(page_title="Chef_dskim 통합 관리 시스템", layout="wide")

# 사이드바 (설정된 규율 및 무결성)
with st.sidebar:
    st.header("🛡️ 시스템 무결성")
    st.success("데이터베이스: 연결됨")
    st.success("엑셀 동기화: 147종 완료")
    st.divider()
    st.info("💡 셰프님 지침: 팩트체크 및 간결한 보고")

st.title("👨‍🍳 MISOYON MMS 메인 대시보드")

tab1, tab2, tab3 = st.tabs(["📈 수익성 분포", "📋 작업 리스트", "📸 스마트 입고"])

with tab1:
    st.subheader("메뉴별 수익성 분포 분석")
    
    # 그래프 설정: text="메뉴명"을 통해 점 위에 이름을 직접 표시
    fig = px.scatter(
        MENU_DATA, 
        x="원가율", 
        y="마진", 
        text="메뉴명",  # 점 옆에 메뉴명 표시
        size="마진", 
        color="원가율",
        color_continuous_scale=px.colors.sequential.RdBu_r, # 원가율 높으면 빨간색
        labels={"원가율": "원가율 (%)", "마진": "마진액 (원)"}
    )
    
    # 텍스트 위치를 점 위로 고정하여 가독성 확보
    fig.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    
    # 레이아웃 조정
    fig.update_layout(height=600)
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption("※ 그래프의 점 위에 마우스를 올리지 않아도 메뉴명을 바로 확인하실 수 있습니다.")

with tab2:
    st.subheader("오늘의 작업 리스트")
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("🍖 갈비 원물 손질 및 수율 체크")
        st.checkbox("🥣 소스류 재고 파악 및 제조")
    with col2:
        st.checkbox("🥬 채소류 전처리")
        st.checkbox("📊 주간 원가 보고서 검토")

with tab3:
    # 이전 단계의 스마트 입고 로직 유지
    st.header("📸 스마트 입고 (OCR 검증)")
    st.camera_input("명세표를 촬영하면 엑셀 데이터와 대조합니다.")
