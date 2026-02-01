import streamlit as st
import pandas as pd
from datetime import datetime, time

# 1. 페이지 설정
st.set_page_config(page_title="Chef_dskim 통합관리시스템", layout="wide")

# --- [데이터베이스] 메뉴별 표준 공정 (SOP) ---
# 셰프님의 노하우가 담긴 '메뉴별 작업 레시피'입니다.
# 나중에는 엑셀에서 불러오도록 할 수 있습니다.
MENU_SOP_DB = {
    "갈비탕": [
        {"start": time(8, 0), "end": time(9, 0), "cat": "Prep", "task": "갈비 핏물 빼기 (찬물 유수)", "point": "30분마다 물 교체"},
        {"start": time(9, 30), "end": time(11, 0), "cat": "Cooking", "task": "갈비탕 초벌 삶기 & 기름 제거", "point": "월계수잎, 통후추 투입"},
        {"start": time(11, 0), "end": time(11, 30), "cat": "Service", "task": "당면 불리기 및 뚝배기 세팅", "point": "미지근한 물 사용"}
    ],
    "양념갈비": [
        {"start": time(14, 0), "end": time(15, 0), "cat": "Prep", "task": "갈비 원육 포션 작업 (다이아몬드 칼집)", "point": "일정한 두께 유지"},
        {"start": time(15, 0), "end": time(16, 0), "cat": "Cooking", "task": "양념 소스 배합 및 숙성", "point": "염도 1.2% 체크"},
        {"start": time(17, 0), "end": time(17, 30), "cat": "Service", "task": "숯불 피우기 및 석쇠 준비", "point": "백탄 사용 권장"}
    ],
    "육회": [
        {"start": time(16, 0), "end": time(16, 30), "cat": "Prep", "task": "우둔살 근막 제거 및 채썰기", "point": "고기 온도 차갑게 유지"},
        {"start": time(16, 30), "end": time(16, 45), "cat": "Cooking", "task": "배 채썰기 및 갈변 방지", "point": "설탕물 살짝 담그기"}
    ]
}

# --- [데이터베이스] 매일 하는 고정 업무 (루틴) ---
DAILY_ROUTINE = [
    {"start": time(9, 0), "end": time(9, 30), "cat": "Prep", "task": "오픈 준비 (환기, 조명, 식자재 검수)", "point": "냉장고 온도 확인", "done": False},
    {"start": time(21, 30), "end": time(22, 0), "cat": "Clean", "task": "주방 마감 청소 및 발주", "point": "가스 밸브 잠금 확인", "done": False}
]

# 2. 세션 상태 초기화
if 'schedule_df' not in st.session_state:
    # 처음엔 '고정 업무'만 로드
    df = pd.DataFrame(DAILY_ROUTINE)
    # 데이터프레임 컬럼명 통일
    df.columns = ["시작 시간", "종료 시간", "구분", "세부 작업 내용", "체크 포인트", "완료"]
    st.session_state.schedule_df = df

# 사이드바
with st.sidebar:
    st.header("📊 시스템 상태")
    st.success("SOP 엔진: 대기 중")
    st.info(f"오늘: {datetime.now().strftime('%Y-%m-%d')}")

st.title("👨‍🍳 MISOYON 통합 관리 시스템")

# 탭 메뉴
menu_tabs = st.tabs(["⏱️ 오퍼레이션(Main)", "📋 메뉴 & 레시피", "🧪 R&D", "💰 원가", "📸 입고"])

# --- [메인: 메뉴 연동 타임테이블] ---
with menu_tabs[0]:
    st.subheader("📅 자동화된 현장 오퍼레이션")
    
    # 1. 메뉴 선택 구역
    with st.expander("🔻 오늘의 판매 메뉴 설정 (터치하여 선택)", expanded=True):
        selected_menus = st.multiselect(
            "오늘 판매하거나 작업할 메뉴를 모두 선택하세요:",
            list(MENU_SOP_DB.keys()),
            help="선택하면 해당 메뉴의 작업 공정이 타임테이블에 자동으로 추가됩니다."
        )
        
        if st.button("🚀 타임테이블 자동 생성"):
            # 기본 루틴으로 리셋
            base_df = pd.DataFrame(DAILY_ROUTINE)
            base_df.columns = ["시작 시간", "종료 시간", "구분", "세부 작업 내용", "체크 포인트", "완료"]
            
            # 선택된 메뉴의 작업들 추가
            new_tasks = []
            for menu in selected_menus:
                for task in MENU_SOP_DB[menu]:
                    new_tasks.append({
                        "시작 시간": task["start"],
                        "종료 시간": task["end"],
                        "구분": task["cat"],
                        "세부 작업 내용": f"[{menu}] {task['task']}", # 메뉴명 태그 붙임
                        "체크 포인트": task["point"],
                        "완료": False
                    })
            
            if new_tasks:
                sop_df = pd.DataFrame(new_tasks)
                # 기존 루틴 + 메뉴별 작업 합치기
                final_df = pd.concat([base_df, sop_df], ignore_index=True)
            else:
                final_df = base_df
                
            # 시간순 정렬 (Start Time 기준)
            final_df = final_df.sort_values(by="시작 시간").reset_index(drop=True)
            
            # 세션에 저장
            st.session_state.schedule_df = final_df
            st.success(f"✅ {len(selected_menus)}개 메뉴에 대한 최적의 동선이 생성되었습니다.")
            st.rerun()

    st.divider()

    # 2. 타임테이블 에디터 (결과 확인 및 수정)
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.write("### 🕒 오늘의 타임테이블")
    with col2:
        if st.button("초기화"):
            st.session_state.schedule_df = pd.DataFrame(DAILY_ROUTINE).rename(columns={"start":"시작 시간", "end":"종료 시간", "cat":"구분", "task":"세부 작업 내용", "point":"체크 포인트", "done":"완료"})
            st.rerun()

    edited_df = st.data_editor(
        st.session_state.schedule_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "시작 시간": st.column_config.TimeColumn("Start", format="HH:mm"),
            "종료 시간": st.column_config.TimeColumn("End", format="HH:mm"),
            "구분": st.column_config.SelectboxColumn("Cat", options=["Prep", "Cooking", "Service", "Clean", "R&D"]),
            "세부 작업 내용": st.column_config.TextColumn("Task", width="large"),
            "체크 포인트": st.column_config.TextColumn("Point", width="medium"),
            "완료": st.column_config.CheckboxColumn("Done", default=False)
        },
        hide_index=True
    )
    
    st.session_state.schedule_df = edited_df

    # 진행률
    total = len(edited_df)
    done = edited_df["완료"].sum()
    if total > 0:
        st.progress(done/total, text=f"공정 진행률: {int(done/total*100)}%")

# --- [나머지 탭] ---
with menu_tabs[1]: st.write("준비 중")
with menu_tabs[2]: st.write("준비 중")
with menu_tabs[3]: st.write("준비 중")
with menu_tabs[4]: st.write("준비 중")
