
import streamlit as st
import pandas as pd
from datetime import datetime, time

# 1. 페이지 설정
st.set_page_config(page_title="Chef_dskim 통합관리시스템", layout="wide")

# 2. 세션 상태 (안전한 데이터 초기화)
if 'schedule_df' not in st.session_state:
    # 시스템이 좋아하는 '진짜 시간(time)' 객체로 데이터를 만듭니다.
    data = {
        "시작 시간": [time(9, 0), time(9, 30), time(11, 0), time(11, 30), time(14, 30), time(17, 0)],
        "종료 시간": [time(9, 30), time(11, 0), time(11, 30), time(14, 30), time(17, 0), time(22, 0)],
        "구분": ["Prep (준비)", "Cooking (조리)", "Service (준비)", "Service (런치)", "R&D/Break", "Service (디너)"],
        "세부 작업 내용": [
            "육수 불 올리기 및 농도 체크", 
            "갈비 원물 포션 작업 (20kg)", 
            "런치 예약석 세팅", 
            "런치 오퍼레이션 집중", 
            "신메뉴 소스 테스트", 
            "디너 예약 초벌 및 마감"
        ],
        "체크 포인트": ["온도 95도 유지", "수율 50% 준수", "테이블 웨어", "홀 소통", "염도 1.2%", "매출 확인"],
        "완료": [False, False, False, False, False, False]
    }
    st.session_state.schedule_df = pd.DataFrame(data)

# 사이드바
with st.sidebar:
    st.header("📊 시스템 상태")
    st.success("데이터 엔진: 정상 가동")
    st.info(f"오늘: {datetime.now().strftime('%Y-%m-%d')}")

st.title("👨‍🍳 MISOYON 통합 관리 시스템")

# 탭 메뉴
menu_tabs = st.tabs([
    "⏱️ 타임테이블(Main)", 
    "📋 메뉴 & 레시피", 
    "🧪 R&D", 
    "💰 원가", 
    "📸 입고"
])

# --- [메인: 타임테이블 에디터] ---
with menu_tabs[0]:
    st.subheader("📅 오늘의 현장 오퍼레이션 (Time & Action)")
    
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.caption("💡 표를 클릭하여 시간을 변경하거나 내용을 수정하세요.")
    with col2:
        if st.button("🔄 초기화"):
            del st.session_state['schedule_df']
            st.rerun()

    # 데이터 에디터 (안전 모드 적용)
    try:
        edited_df = st.data_editor(
            st.session_state.schedule_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "시작 시간": st.column_config.TimeColumn("Start", format="HH:mm"),
                "종료 시간": st.column_config.TimeColumn("End", format="HH:mm"),
                "구분": st.column_config.SelectboxColumn(
                    "Category",
                    options=["Prep (준비)", "Cooking (조리)", "Plating (담기)", "Service (제공)", "Clean (정리)", "R&D"]
                ),
                "세부 작업 내용": st.column_config.TextColumn("Detail Task", width="large"),
                "체크 포인트": st.column_config.TextColumn("Point", width="medium"),
                "완료": st.column_config.CheckboxColumn("Done", default=False)
            },
            hide_index=True
        )
        
        # 수정된 데이터 저장
        st.session_state.schedule_df = edited_df
        
        # 진행률 바
        done_count = edited_df["완료"].sum()
        total_count = len(edited_df)
        if total_count > 0:
            st.progress(done_count / total_count, text=f"진행률: {int(done_count/total_count*100)}%")

    except Exception as e:
        st.error(f"⚠️ 시스템 버전 호환성 문제 발생: {e}")
        st.warning("requirements.txt 파일에 'streamlit>=1.24.0'이 포함되어 있는지 확인해주세요.")

# --- [나머지 탭 (구조 유지)] ---
with menu_tabs[1]: st.write("준비 중")
with menu_tabs[2]: st.write("준비 중")
with menu_tabs[3]: st.write("준비 중")
with menu_tabs[4]: st.write("준비 중")
