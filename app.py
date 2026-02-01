import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="Chef_dskim 통합관리시스템", layout="wide")

# 2. 세션 상태 (타임테이블 데이터 메모리)
if 'schedule_df' not in st.session_state:
    # 셰프님의 대회 자료 스타일을 반영한 기본 템플릿
    data = {
        "시작 시간": ["09:00", "09:30", "11:00", "11:30", "14:30", "17:00"],
        "종료 시간": ["09:30", "11:00", "11:30", "14:30", "17:00", "22:00"],
        "구분": ["Prep (준비)", "Cooking (조리)", "Service (준비)", "Service (런치)", "R&D/Break", "Service (디너)"],
        "세부 작업 내용": [
            "육수 불 올리기 및 농도 체크, 채소 전처리", 
            "갈비 원물 포션 작업 (20kg)", 
            "런치 예약석 세팅 및 가니쉬 준비", 
            "런치 오퍼레이션 집중 (메인: 갈비탕)", 
            "신메뉴(불고기 소스) 염도 테스트", 
            "디너 예약(8인) 초벌 및 마감 정산"
        ],
        "체크 포인트": ["육수 온도 95도 유지", "수율 50% 준수", "테이블 웨어 확인", "홀/주방 소통", "염도계 1.2%", "매출 누락 확인"],
        "완료": [False, False, False, False, False, False]
    }
    st.session_state.schedule_df = pd.DataFrame(data)

# 사이드바
with st.sidebar:
    st.header("📊 시스템 상태")
    st.success("대회급 타임테이블: 가동")
    st.info(f"오늘: {datetime.now().strftime('%Y-%m-%d')}")

# 헤더
st.markdown("### 👨‍🍳 Chef_dskim 통합관리시스템")

# 탭 메뉴 (메인을 가장 정밀하게)
menu_tabs = st.tabs([
    "⏱️ 정밀 오퍼레이션(Main)", 
    "📋 메뉴 & 레시피", 
    "🧪 R&D & 개발", 
    "💰 원가 & 자재", 
    "📸 입고 & 재고"
])

# --- [메인: 대회 수준 정밀 타임테이블 (Excel 스타일 에디터)] ---
with menu_tabs[0]:
    st.subheader(f"📅 오늘의 현장 오퍼레이션 (Time & Action)")
    
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.caption("💡 엑셀처럼 클릭하여 시간과 내용을 직접 수정하세요. 행을 추가하거나 삭제할 수 있습니다.")
    with col2:
        if st.button("🔄 리셋 (기본값)"):
            st.session_state.pop('schedule_df')
            st.rerun()

    # 엑셀처럼 편집 가능한 데이터 그리드 (Data Editor)
    # 셰프님이 대회 자료에서 보셨던 그 '표' 형태입니다.
    edited_df = st.data_editor(
        st.session_state.schedule_df,
        num_rows="dynamic", # 행 추가/삭제 가능
        use_container_width=True,
        column_config={
            "시작 시간": st.column_config.TimeColumn("Start", format="HH:mm"),
            "종료 시간": st.column_config.TimeColumn("End", format="HH:mm"),
            "구분": st.column_config.SelectboxColumn(
                "Category",
                options=["Prep (준비)", "Cooking (조리)", "Plating (담기)", "Service (제공)", "Clean (정리)", "R&D"]
            ),
            "세부 작업 내용": st.column_config.TextColumn("Detail Task", width="large"),
            "체크 포인트": st.column_config.TextColumn("Critical Point (확인)", width="medium"),
            "완료": st.column_config.CheckboxColumn("Done", default=False)
        },
        hide_index=True
    )

    # 수정된 내용 실시간 반영 (통계 표시)
    st.session_state.schedule_df = edited_df
    
    # 진행률 표시
    total_tasks = len(edited_df)
    completed_tasks = edited_df["완료"].sum()
    if total_tasks > 0:
        progress = completed_tasks / total_tasks
        st.progress(progress, text=f"오늘의 공정률: {int(progress*100)}% ({completed_tasks}/{total_tasks})")
    
    # 미완료 작업 중 가장 급한 것 강조
    st.divider()
    not_done = edited_df[edited_df["완료"] == False]
    if not not_done.empty:
        next_task = not_done.iloc[0]
        st.warning(f"🔔 **현재 우선순위 작업**: [{next_task['시작 시간']}~{next_task['종료 시간']}] {next_task['세부 작업 내용']} (Check: {next_task['체크 포인트']})")
    else:
        st.success("🎉 오늘의 모든 공정이 완료되었습니다. 고생하셨습니다, 셰프님!")

# --- [나머지 탭 유지] ---
with menu_tabs[1]:
    st.write("메뉴 관리 화면")
with menu_tabs[2]:
    st.write("R&D 화면")
with menu_tabs[3]:
    st.write("원가 관리 화면")
with menu_tabs[4]:
    st.write("재고 관리 화면")
