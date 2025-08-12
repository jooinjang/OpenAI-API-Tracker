import json
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
openai_org_id = os.environ.get("OPENAI_ORG_KEY")

from utils import (
    get_total_cost,
    group_by_date,
    group_by_model,
    group_by_userID,
    build_userinfo,
    get_name_with_userID,
    get_userID_with_name,
    rebuild_to_cost,
    list_api_keys,
    list_organization_projects,
    get_project_api_keys,
    get_organization_users,
    calculate_project_usage,
    find_budget_overages,
    delete_api_key,
    bulk_delete_api_keys,
    save_project_budgets,
    load_project_budgets,
    reset_project_budgets
)

# Import Apple design system
from components_design import load_apple_design_system, AppleComponents, AppleCharts, AppleForms, safe_plotly_chart, safe_dataframe, EnhancedComponents


st.set_page_config(layout="wide", page_title="OpenAI Usage Tracker")

# Load Apple design system
load_apple_design_system()

# 앱 초기화 시 저장된 예산 로드
if 'project_budgets' not in st.session_state:
    st.session_state.project_budgets = load_project_budgets()

# Enhanced Sidebar Navigation
st.sidebar.title("📊 OpenAI Usage Tracker")
st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)

# User Data Upload - Apple Style
with st.sidebar:
    uploaded_user_file = AppleComponents.render_sidebar_file_upload(
        title="사용자별 데이터",
        description="User 기준 JSON 파일을 선택하세요",
        file_type="json",
        key="user_data_upload",
        icon="👤"
    )

# Compact status messages for user data
if uploaded_user_file is not None:
    try:
        st.session_state.uploaded_data = json.load(uploaded_user_file)
        with st.sidebar:
            EnhancedComponents.render_compact_sidebar_status("사용자별 데이터 업로드 완료", "success")
    except json.JSONDecodeError:
        with st.sidebar:
            EnhancedComponents.render_compact_sidebar_status("JSON 형식 오류", "error")
    except Exception as e:
        with st.sidebar:
            EnhancedComponents.render_compact_sidebar_status(f"파일 오류: {str(e)[:20]}...", "error")

# Project Data Upload - Apple Style
with st.sidebar:
    uploaded_project_file = AppleComponents.render_sidebar_file_upload(
        title="프로젝트별 데이터", 
        description="Project 기준 JSON 파일을 선택하세요",
        file_type="json",
        key="project_data_upload",
        icon="🏗️"
    )

# Compact status messages for project data
if uploaded_project_file is not None:
    try:
        st.session_state.project_usage_data = json.load(uploaded_project_file)
        with st.sidebar:
            EnhancedComponents.render_compact_sidebar_status("프로젝트별 데이터 업로드 완료", "success")
    except json.JSONDecodeError:
        with st.sidebar:
            EnhancedComponents.render_compact_sidebar_status("JSON 형식 오류", "error")
    except Exception as e:
        with st.sidebar:
            EnhancedComponents.render_compact_sidebar_status(f"파일 오류: {str(e)[:20]}...", "error")

st.sidebar.markdown('</div>', unsafe_allow_html=True)


st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "기능 선택",
    ["📈 전체 사용량", "👤 사용자별 분석", "🔑 API 키 관리", "💰 사용 한도 관리"]
)

# Enhanced main title with dark theme support
st.markdown("""
<div style="color: var(--text-primary); margin-bottom: 2rem;">
    <h1 style="color: inherit; font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem;">
        OpenAI API Usage Visualizer
    </h1>
</div>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "userinfo" not in st.session_state:
    st.session_state.userinfo = False
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None
if "project_usage_data" not in st.session_state:
    st.session_state.project_usage_data = None

# 전체 사용량 페이지
if page == "📈 전체 사용량":
    if st.session_state.uploaded_data is None:
        AppleComponents.render_apple_alert(
            "먼저 왼쪽 사이드바에서 사용자별 사용량 데이터를 업로드해주세요.",
            "warning"
        )
    else:
        # Apple-style section header
        AppleComponents.render_section_header(
            "전체 사용량 분석",
            "OpenAI API 사용량 전체 분석 및 시각화 대시보드"
        )
        
        if not st.session_state.userinfo:
            build_userinfo()
            with open("userinfo.json") as fp:
                st.session_state.userinfo = json.load(fp)

        data = st.session_state.uploaded_data
        
        # 2025년 구조만 지원
        data_ = data  # 전체 data 객체 전달
        
        total_cost = get_total_cost(data_)[0]
        
        # Process user data first
        grouped_data = group_by_userID(data_)
        userID = grouped_data.keys()  # 사용자 ID
        
        # Apple-style metrics display
        total_requests = sum(len(data["data"]) for data in data_.values() if "data" in data)
        active_users = len([uid for uid in userID if uid is not None])
        
        metrics = [
            {"value": f"${total_cost:.2f}", "label": "총 비용", "icon": "💰", "change": None, "change_type": "neutral"},
            {"value": f"{total_requests:,}", "label": "API 요청", "icon": "⚡", "change": None, "change_type": "neutral"},
            {"value": f"{active_users}", "label": "활성 사용자", "icon": "👥", "change": None, "change_type": "neutral"},
            {"value": "100%", "label": "시스템 상태", "icon": "✅", "change": None, "change_type": "positive"}
        ]
        AppleComponents.render_apple_metrics(metrics, columns=4)
        total_usage, cost_transition = [], []
        names = []
        
        for uid in userID:
            name = get_name_with_userID(uid, st.session_state.userinfo)
            if name is not None:  # None이 아닌 경우만 추가
                names.append(name)
                tu, ct = get_total_cost(grouped_data[uid])
                total_usage.append(tu)
                cost_transition.append(ct)
            else:
                # 이름을 찾을 수 없는 경우 user_id를 사용
                if uid is not None:
                    names.append(f"Unknown ({uid[:8]}...)")
                else:
                    names.append("Unknown User")
                tu, ct = get_total_cost(grouped_data[uid])
                total_usage.append(tu)
                cost_transition.append(ct)

        df = pd.DataFrame(
            {
                "Username": names,
                "User ID": userID,
                "Total Usage(USD)": total_usage,
                "usage_history": cost_transition,
            }
        )

        # Apple-style data table
        def render_user_summary():
            # 데이터프레임을 더 읽기 쉽게 포맷팅
            display_df = df.copy()
            display_df["Total Usage(USD)"] = display_df["Total Usage(USD)"].apply(lambda x: f"${x:.4f}")
            
            # 주요 컬럼만 표시
            display_columns = ["Username", "User ID", "Total Usage(USD)"]
            safe_dataframe(display_df[display_columns], use_container_width=True)
        
        # Apple-style card layout
        AppleComponents.render_apple_card(
            "사용자별 사용량 분석",
            render_user_summary,
            subtitle="모든 사용자의 API 사용량 및 비용 정보",
            icon="👥"
        )

# 사용자별 분석 페이지
elif page == "👤 사용자별 분석":
    if st.session_state.uploaded_data is None:
        AppleComponents.render_apple_alert(
            "먼저 왼쪽 사이드바에서 사용자별 사용량 데이터를 업로드해주세요.",
            "warning"
        )
    else:
        # Apple-style section header
        AppleComponents.render_section_header(
            "사용자별 분석",
            "개별 사용자의 API 사용 패턴 및 상세 분석"
        )
        
        if not st.session_state.userinfo:
            build_userinfo()
            with open("userinfo.json") as fp:
                st.session_state.userinfo = json.load(fp)

        data = st.session_state.uploaded_data
        
        # 2025년 구조만 지원
        data_ = data  # 전체 data 객체 전달

        grouped_data = group_by_userID(data_)
        userID = grouped_data.keys()  # 사용자 ID
        names = sorted(
            [get_name_with_userID(uid, st.session_state.userinfo) or (f"Unknown ({uid[:8]}...)" if uid is not None else "Unknown User") for uid in userID]
        )

        username = st.selectbox(
            label="👤 사용자 선택",
            options=names,
        )

        uid = get_userID_with_name(username, st.session_state.userinfo)
        
        # 사용자를 찾지 못한 경우 처리
        if uid is None or uid not in grouped_data:
            st.error(f"사용자 '{username}'의 데이터를 찾을 수 없습니다.")
            st.stop()
        
        # 사용자 통계 표시
        col1, col2, col3 = st.columns(3)
        
        personal_total_cost = get_total_cost(grouped_data[uid])[0]
        total_records = len(grouped_data[uid])
        avg_cost_per_request = personal_total_cost / total_records if total_records > 0 else 0
        
        with col1:
            st.metric("💰 총 사용 비용", f"${personal_total_cost:.4f}")
        with col2:
            st.metric("📊 총 요청 수", f"{total_records}")
        with col3:
            st.metric("📈 평균 요청당 비용", f"${avg_cost_per_request:.4f}")

        # 날짜별 모델 사용량 차트
        st.subheader("📅 날짜별 모델 사용량")
        data_date = group_by_date(grouped_data[uid])

        data_date_models = [
            [k, rebuild_to_cost(group_by_model(data_date[k]))]
            for k in data_date.keys()
        ]

        date = []
        models = []
        amounts = []
        for x in data_date_models:
            d = x[0]
            model_logs = x[1]
            for k in model_logs.keys():
                date.append(d)
                models.append(k)
                amounts.append(model_logs[k]["total_cost"])

        chart_data = {"date": date, "model": models, "Total Usage ($)": amounts}
        df = pd.DataFrame(chart_data)

        # 누적 막대그래프 생성
        fig = px.bar(
            df,
            x="date",
            y="Total Usage ($)",
            color="model",
            title=f"{username}의 모델별 일일 사용량",
            labels={"date": "날짜", "Total Usage ($)": "사용량 ($)", "model": "모델"},
            text_auto=True,
        )
        
        # Y축 범위 설정
        if personal_total_cost < 10:
            fig.update_yaxes(range=[0, 10])
        elif personal_total_cost < 50:
            fig.update_yaxes(range=[0, 50])
        elif personal_total_cost < 100:
            fig.update_yaxes(range=[0, 100])
        elif personal_total_cost < 1000:
            fig.update_yaxes(range=[0, 500])
        elif personal_total_cost < 3000:
            fig.update_yaxes(range=[0, 1500])
        else:
            fig.update_yaxes(range=[0, 3000])

        # 그래프 레이아웃 업데이트
        fig.update_layout(barmode="stack")

        # Streamlit 앱에 그래프 표시
        safe_plotly_chart(fig, use_container_width=True)

# API 키 관리 페이지
elif page == "🔑 API 키 관리":
    # Enhanced page header
    EnhancedComponents.render_page_header(
        "API 키 관리",
        "조직의 OpenAI API 키 관리 및 모니터링"
    )
    
    EnhancedComponents.render_custom_alert(
        "이 기능은 관리자 권한이 필요합니다. 조직의 API 키를 관리할 수 있습니다.",
        alert_type="warning",
        title="관리자 권한 필요"
    )
    
    # 관리자 API 키 입력 폼
    with st.expander("🔐 관리자 인증", expanded=True):
        admin_api_key = st.text_input(
            "관리자 API 키", 
            type="password",
            placeholder="sk-...",
            help="조직 관리자 권한이 있는 OpenAI API 키를 입력하세요"
        )
        
        # 조직 ID는 환경변수에서 가져옴
        if openai_org_id:
            EnhancedComponents.render_inline_alert(f"조직 ID: {openai_org_id[:15]}...", "info")
        else:
            EnhancedComponents.render_inline_alert("환경변수에 OPENAI_ORG_KEY가 설정되지 않았습니다", "error")
        
        # 인증 상태 표시
        if admin_api_key and openai_org_id:
            EnhancedComponents.render_inline_alert("관리자 인증 정보가 준비되었습니다", "success")
        elif admin_api_key and not openai_org_id:
            EnhancedComponents.render_inline_alert("환경변수 OPENAI_ORG_KEY를 설정해주세요", "error")
        elif not admin_api_key and openai_org_id:
            EnhancedComponents.render_inline_alert("관리자 API 키를 입력해주세요", "warning")
        else:
            EnhancedComponents.render_inline_alert("관리자 API 키와 조직 ID가 모두 필요합니다", "error")
    
    # 인증 정보가 모두 준비된 경우에만 탭 표시
    if admin_api_key and openai_org_id:
        tab1, tab2, tab3 = st.tabs(["📋 프로젝트 목록", "🔍 프로젝트별 API 키", "👥 조직 사용자"])
    else:
        EnhancedComponents.render_custom_alert("관리자 API 키를 먼저 입력해주세요", "info", compact=True)
    
    # 탭 내용을 조건부로 표시
    if admin_api_key and openai_org_id:
        with tab1:
            st.subheader("📋 조직 프로젝트 목록")
            
            if st.button("🔄 프로젝트 목록 새로고침"):
                with st.spinner("프로젝트 정보를 가져오는 중..."):
                    projects = list_organization_projects(admin_api_key)
                    
                    if projects:
                        st.session_state.projects = projects
                        st.success(f"✅ {len(projects)}개의 프로젝트를 가져왔습니다.")
                    else:
                        st.error("❌ 프로젝트 목록을 가져오는데 실패했습니다. 관리자 권한과 API 키 설정을 확인해주세요.")
            
            # 저장된 프로젝트 목록 표시
            if hasattr(st.session_state, 'projects') and st.session_state.projects:
                projects_data = []
                
                for project in st.session_state.projects:
                    projects_data.append({
                        "프로젝트 ID": project.get("id", "N/A"),
                        "프로젝트 이름": project.get("name", "Unnamed"),
                        "생성일": pd.to_datetime(project.get("created_at", 0), unit='s').strftime('%Y-%m-%d %H:%M:%S') if project.get("created_at") else "N/A",
                        "상태": project.get("status", "unknown"),
                        "보관됨": "예" if project.get("archived_at") else "아니오",
                    })
                
                projects_df = pd.DataFrame(projects_data)
                st.dataframe(projects_df)
                
                # 프로젝트 통계
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 전체 프로젝트", len(projects_data))
                with col2:
                    active_projects = len([p for p in st.session_state.projects if p.get("status") == "active"])
                    st.metric("✅ 활성 프로젝트", active_projects)
                with col3:
                    archived_projects = len([p for p in st.session_state.projects if p.get("archived_at")])
                    st.metric("📦 보관된 프로젝트", archived_projects)
                    
            else:
                st.warning("프로젝트 목록을 가져오려면 '🔄 프로젝트 목록 새로고침' 버튼을 클릭하세요.")
        
        with tab2:
            st.subheader("🔍 프로젝트별 API 키 관리")
            
            if hasattr(st.session_state, 'projects') and st.session_state.projects:
                # 프로젝트 선택
                project_options = [(p["name"], p["id"]) for p in st.session_state.projects]
                selected_project_name = st.selectbox(
                    "프로젝트 선택",
                    options=[name for name, _ in project_options],
                    help="API 키를 확인할 프로젝트를 선택하세요"
                )
                
                if selected_project_name:
                    # 선택된 프로젝트 ID 찾기
                    selected_project_id = next(proj_id for name, proj_id in project_options if name == selected_project_name)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        EnhancedComponents.render_inline_alert(f"선택된 프로젝트: {selected_project_name} ({selected_project_id[:20]}...)", "info")
                    with col2:
                        if st.button("🔄 API 키 새로고침"):
                            with st.spinner("API 키 정보를 가져오는 중..."):
                                project_api_keys = get_project_api_keys(selected_project_id, admin_api_key)
                                
                                if project_api_keys:
                                    st.session_state.selected_project_api_keys = project_api_keys
                                    st.session_state.selected_project_name = selected_project_name
                                    st.success(f"✅ {len(project_api_keys)}개의 API 키를 가져왔습니다.")
                                else:
                                    st.error("❌ API 키 목록을 가져오는데 실패했습니다.")
                    
                    # Enhanced API 키 목록 표시 with centered layout
                    if (hasattr(st.session_state, 'selected_project_api_keys') and 
                        st.session_state.selected_project_api_keys and
                        hasattr(st.session_state, 'selected_project_name') and
                        st.session_state.selected_project_name == selected_project_name):
                        
                        # Prepare API keys data
                        api_keys_data = []
                        for api_key in st.session_state.selected_project_api_keys:
                            api_keys_data.append({
                                "API 키 ID": api_key.get("id", "N/A"),
                                "이름": api_key.get("name", "Unnamed") or "Unnamed",
                                "축약된 키": api_key.get("redacted_value", "N/A")[:50] + "..." if api_key.get("redacted_value") else "N/A",
                                "생성일": pd.to_datetime(api_key.get("created_at", 0), unit='s').strftime('%Y-%m-%d %H:%M:%S') if api_key.get("created_at") else "N/A",
                                "소유자": api_key.get("owner", {}).get("email", "N/A") if isinstance(api_key.get("owner"), dict) else "N/A",
                            })
                        
                        api_keys_df = pd.DataFrame(api_keys_data)
                        
                        # Render API keys table in centered container
                        def render_api_keys_content():
                            EnhancedComponents.render_enhanced_table(
                                api_keys_df,
                                title="🔑 API 키 목록",
                                searchable=True
                            )
                            
                            # API 키 통계 in compact layout
                            metrics = [
                                {"value": len(api_keys_data), "label": "API 키 개수"},
                                {"value": len(set([key.get("owner", {}).get("email") for key in st.session_state.selected_project_api_keys if isinstance(key.get("owner"), dict) and key.get("owner", {}).get("email")])), "label": "고유 소유자"},
                                {"value": f"{selected_project_name}", "label": "프로젝트"}
                            ]
                            EnhancedComponents.render_metric_cards(metrics, columns=3)
                        
                        EnhancedComponents.render_centered_container(render_api_keys_content)
                    else:
                        st.info("API 키 정보를 보려면 '🔄 API 키 새로고침' 버튼을 클릭하세요.")
            else:
                st.warning("먼저 '📋 프로젝트 목록' 탭에서 프로젝트 목록을 새로고침하세요.")
        
        with tab3:
            st.subheader("👥 조직 사용자 목록")
            
            if st.button("🔄 사용자 목록 새로고침"):
                with st.spinner("사용자 정보를 가져오는 중..."):
                    users = get_organization_users(admin_api_key)
                    
                    if users:
                        st.session_state.org_users = users
                        st.success(f"✅ {len(users)}명의 사용자를 가져왔습니다.")
                    else:
                        st.error("❌ 사용자 목록을 가져오는데 실패했습니다.")
            
            # 저장된 사용자 목록 표시
            if hasattr(st.session_state, 'org_users') and st.session_state.org_users:
                users_data = []
                
                for user in st.session_state.org_users:
                    users_data.append({
                        "사용자 ID": user.get("id", "N/A"),
                        "이름": user.get("name", "N/A"),
                        "이메일": user.get("email", "N/A"),
                        "역할": user.get("role", "N/A"),
                        "추가일": pd.to_datetime(user.get("added_at", 0), unit='s').strftime('%Y-%m-%d %H:%M:%S') if user.get("added_at") else "N/A",
                    })
                
                users_df = pd.DataFrame(users_data)
                st.dataframe(users_df)
                
                # 사용자 통계
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("👥 전체 사용자", len(users_data))
                with col2:
                    owners = len([u for u in st.session_state.org_users if u.get("role") == "owner"])
                    st.metric("👑 소유자", owners)
                with col3:
                    members = len([u for u in st.session_state.org_users if u.get("role") == "member"])
                    st.metric("👤 멤버", members)
                    
            else:
                st.warning("사용자 목록을 가져오려면 '🔄 사용자 목록 새로고침' 버튼을 클릭하세요.")

# 사용 한도 관리 페이지
elif page == "💰 사용 한도 관리":
    # Enhanced page header
    EnhancedComponents.render_page_header(
        "사용 한도 관리",
        "프로젝트별 예산 설정 및 사용량 모니터링"
    )
    
    EnhancedComponents.render_custom_alert(
        "이 기능은 관리자 권한이 필요합니다. 프로젝트별 사용 한도를 설정하고 모니터링할 수 있습니다.",
        alert_type="info",
        title="사용 한도 관리"
    )
    
    # 관리자 API 키 입력 폼
    with st.expander("🔐 관리자 인증", expanded=True):
        admin_api_key = st.text_input(
            "관리자 API 키", 
            type="password",
            placeholder="sk-...",
            help="조직 관리자 권한이 있는 OpenAI API 키를 입력하세요",
            key="budget_admin_key"
        )
        
        # 조직 ID는 환경변수에서 가져옴
        if openai_org_id:
            st.info(f"📋 조직 ID: {openai_org_id[:15]}...")
        else:
            st.error("❌ 환경변수에 OPENAI_ORG_KEY가 설정되지 않았습니다.")
        
        # 인증 상태 표시
        if admin_api_key and openai_org_id:
            st.success("✅ 관리자 인증 정보가 준비되었습니다.")
        elif admin_api_key and not openai_org_id:
            st.error("❌ 환경변수 OPENAI_ORG_KEY를 설정해주세요.")
        elif not admin_api_key and openai_org_id:
            st.warning("⚠️ 관리자 API 키를 입력해주세요.")
        else:
            st.error("❌ 관리자 API 키와 조직 ID가 모두 필요합니다.")
    
    # 인증 정보가 모두 준비된 경우에만 탭 표시
    if admin_api_key and openai_org_id:
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 프로젝트별 예산 설정", "📊 일괄 예산 설정", "📈 예산 모니터링", "⚠️ 초과 사용 관리"])
    else:
        EnhancedComponents.render_custom_alert("관리자 API 키를 먼저 입력해주세요", "info", compact=True)
    
    # 탭 내용을 조건부로 표시
    if admin_api_key and openai_org_id:
        with tab1:
            st.subheader("🎯 프로젝트별 예산 설정")
            
            # 프로젝트 목록 가져오기
            if st.button("🔄 프로젝트 목록 새로고침", key="budget_refresh_projects"):
                with st.spinner("프로젝트 정보를 가져오는 중..."):
                    projects = list_organization_projects(admin_api_key)
                    
                    if projects:
                        st.session_state.budget_projects = projects
                        # 세션 상태에 예산 정보 초기화 (존재하지 않는 경우에만)
                        if 'project_budgets' not in st.session_state:
                            st.session_state.project_budgets = {}
                        st.success(f"✅ {len(projects)}개의 프로젝트를 가져왔습니다.")
                    else:
                        st.error("❌ 프로젝트 목록을 가져오는데 실패했습니다.")
            
            # 프로젝트별 예산 설정
            if hasattr(st.session_state, 'budget_projects') and st.session_state.budget_projects:
                st.subheader("💳 개별 프로젝트 예산 설정")
                
                # 세션 상태에 예산 정보 초기화
                if 'project_budgets' not in st.session_state:
                    st.session_state.project_budgets = {}
                
                # 각 프로젝트별로 예산 입력 폼 생성
                for i, project in enumerate(st.session_state.budget_projects):
                    project_id = project["id"]
                    project_name = project["name"]
                    project_status = project.get("status", "unknown")
                    
                    # 활성 프로젝트이면서 Default project가 아닌 경우만 예산 설정 가능
                    if project_status == "active" and project_name.lower() != "default project":
                        with st.expander(f"📋 {project_name} ({project_id[:20]}...)", expanded=False):
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                current_budget = st.session_state.project_budgets.get(project_id, 0.0)
                                new_budget = st.number_input(
                                    f"월별 예산 (USD)",
                                    min_value=0.0,
                                    max_value=10000.0,
                                    value=float(current_budget),
                                    step=10.0,
                                    key=f"budget_{project_id}",
                                    help=f"{project_name}의 월별 사용 한도를 USD로 설정하세요"
                                )
                            
                            with col2:
                                if st.button(f"💾 저장", key=f"save_{project_id}"):
                                    st.session_state.project_budgets[project_id] = new_budget
                                    # 파일에 저장
                                    if save_project_budgets(st.session_state.project_budgets):
                                        st.success(f"✅ {project_name} 예산이 ${new_budget:.2f}로 설정되고 저장되었습니다.")
                                    else:
                                        st.warning(f"⚠️ {project_name} 예산은 설정되었지만 파일 저장에 실패했습니다.")
                            
                            with col3:
                                if st.button(f"🗑️ 삭제", key=f"delete_{project_id}"):
                                    if project_id in st.session_state.project_budgets:
                                        del st.session_state.project_budgets[project_id]
                                        # 파일에 저장
                                        if save_project_budgets(st.session_state.project_budgets):
                                            st.success(f"✅ {project_name}의 예산 설정이 삭제되고 저장되었습니다.")
                                        else:
                                            st.warning(f"⚠️ {project_name}의 예산은 삭제되었지만 파일 저장에 실패했습니다.")
                                        # 페이지 새로고침을 위한 대체 방법
                                        try:
                                            st.experimental_rerun()
                                        except AttributeError:
                                            # 구버전 Streamlit용 대체
                                            try:
                                                st.experimental_rerun()
                                            except AttributeError:
                                                # experimental_rerun도 없는 경우, 메시지만 표시
                                                st.info("💡 페이지를 새로고침하면 삭제가 반영됩니다.")
                            
                            # 현재 설정된 예산 표시
                            if project_id in st.session_state.project_budgets:
                                st.info(f"현재 설정된 예산: ${st.session_state.project_budgets[project_id]:.2f}")
                    elif project_name.lower() == "default project":
                        st.info(f"ℹ️ {project_name}는 기본 프로젝트이므로 예산 설정에서 제외됩니다.")
                    else:
                        st.warning(f"⚠️ {project_name}는 비활성 상태이므로 예산 설정을 할 수 없습니다.")
                        
                # 설정된 예산 요약
                if st.session_state.project_budgets:
                    st.subheader("📊 설정된 예산 요약")
                    budget_summary = []
                    total_budget = 0
                    
                    for project_id, budget in st.session_state.project_budgets.items():
                        project_name = next((p["name"] for p in st.session_state.budget_projects if p["id"] == project_id), "Unknown")
                        budget_summary.append({
                            "프로젝트": project_name,
                            "프로젝트 ID": project_id[:20] + "...",
                            "월별 예산": f"${budget:.2f}",
                        })
                        total_budget += budget
                    
                    if budget_summary:
                        budget_df = pd.DataFrame(budget_summary)
                        st.dataframe(budget_df)
                        
                        # 총 예산 표시
                        st.metric("💰 총 월별 예산", f"${total_budget:.2f}")
                        
            else:
                st.warning("먼저 '🔄 프로젝트 목록 새로고침' 버튼을 클릭하여 프로젝트를 불러오세요.")
        
        with tab2:
            st.subheader("📊 일괄 예산 설정")
            
            if hasattr(st.session_state, 'budget_projects') and st.session_state.budget_projects:
                active_projects = [p for p in st.session_state.budget_projects if p.get("status") == "active" and p.get("name", "").lower() != "default project"]
                
                if active_projects:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        bulk_budget = st.number_input(
                            "모든 활성 프로젝트에 적용할 월별 예산 (USD)",
                            min_value=0.0,
                            max_value=10000.0,
                            value=100.0,
                            step=10.0,
                            help="모든 활성 프로젝트에 동일하게 적용될 월별 사용 한도를 설정하세요"
                        )
                    
                    with col2:
                        if st.button("🔄 모든 프로젝트에 적용"):
                            # 세션 상태에 예산 정보 초기화
                            if 'project_budgets' not in st.session_state:
                                st.session_state.project_budgets = {}
                            
                            # 모든 활성 프로젝트에 예산 적용
                            for project in active_projects:
                                st.session_state.project_budgets[project["id"]] = bulk_budget
                            
                            # 파일에 저장
                            if save_project_budgets(st.session_state.project_budgets):
                                st.success(f"✅ {len(active_projects)}개의 활성 프로젝트에 ${bulk_budget:.2f} 예산이 일괄 적용되고 저장되었습니다!")
                            else:
                                st.warning(f"⚠️ {len(active_projects)}개 프로젝트에 예산이 적용되었지만 파일 저장에 실패했습니다.")
                            # 페이지 새로고침을 위한 대체 방법
                            try:
                                st.experimental_rerun()
                            except AttributeError:
                                # 구버전 Streamlit용 대체
                                try:
                                    st.experimental_rerun()
                                except AttributeError:
                                    # experimental_rerun도 없는 경우, 메시지만 표시
                                    st.info("💡 페이지를 새로고침하면 업데이트된 예산을 확인할 수 있습니다.")
                    
                    # 적용 예정 프로젝트 미리보기
                    st.subheader("📋 적용 예정 프로젝트")
                    st.write(f"다음 **{len(active_projects)}개**의 활성 프로젝트에 **${bulk_budget:.2f}**가 적용됩니다:")
                    st.info("ℹ️ Default project는 예산 설정에서 자동으로 제외됩니다.")
                    
                    preview_data = []
                    for project in active_projects:
                        current_budget = st.session_state.get('project_budgets', {}).get(project["id"], 0.0)
                        preview_data.append({
                            "프로젝트": project["name"],
                            "현재 예산": f"${current_budget:.2f}",
                            "적용될 예산": f"${bulk_budget:.2f}",
                            "변경 사항": f"${bulk_budget - current_budget:+.2f}"
                        })
                    
                    preview_df = pd.DataFrame(preview_data)
                    st.dataframe(preview_df)
                    
                    # 총계 정보
                    current_total = sum(st.session_state.get('project_budgets', {}).get(p["id"], 0.0) for p in active_projects)
                    new_total = len(active_projects) * bulk_budget
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("현재 총 예산", f"${current_total:.2f}")
                    with col2:
                        st.metric("적용 후 총 예산", f"${new_total:.2f}")
                    with col3:
                        change = new_total - current_total
                        st.metric("변경 금액", f"${change:+.2f}")
                    
                    # 예산 초기화 기능
                    st.markdown("---")
                    st.subheader("🗑️ 예산 초기화")
                    st.warning("⚠️ **주의**: 아래 버튼을 클릭하면 모든 프로젝트의 예산 설정이 완전히 삭제됩니다.")
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("🗑️ 모든 예산 초기화", key="reset_all_budgets"):
                            # 확인을 위한 세션 상태 설정
                            st.session_state.reset_confirm = True
                    
                    with col2:
                        if hasattr(st.session_state, 'reset_confirm') and st.session_state.reset_confirm:
                            if st.button("✅ 초기화 확인", key="confirm_reset"):
                                # 세션 상태와 파일 모두 초기화
                                st.session_state.project_budgets = {}
                                if reset_project_budgets():
                                    st.success("✅ 모든 프로젝트 예산이 초기화되고 파일이 삭제되었습니다.")
                                else:
                                    st.warning("⚠️ 세션 예산은 초기화되었지만 파일 삭제에 실패했습니다.")
                                # 확인 상태 초기화
                                if 'reset_confirm' in st.session_state:
                                    del st.session_state.reset_confirm
                                st.experimental_rerun()
                    
                    with col3:
                        if hasattr(st.session_state, 'reset_confirm') and st.session_state.reset_confirm:
                            if st.button("❌ 취소", key="cancel_reset"):
                                del st.session_state.reset_confirm
                                st.experimental_rerun()
                        
                else:
                    st.warning("⚠️ 활성 상태인 프로젝트가 없습니다.")
            else:
                st.warning("먼저 '🎯 프로젝트별 예산 설정' 탭에서 프로젝트 목록을 새로고침하세요.")
        
        with tab3:
            st.subheader("📈 예산 모니터링")
            st.info("💡 이 기능은 업로드된 프로젝트별 사용량 데이터와 설정된 예산을 비교하여 사용률을 분석합니다.")
            
            # 프로젝트별 사용량 데이터 상태 확인
            if st.session_state.project_usage_data is not None:
                # 파일 구조 간단 확인
                if isinstance(st.session_state.project_usage_data, dict) and "data" in st.session_state.project_usage_data:
                    buckets_count = len(st.session_state.project_usage_data["data"])
                    st.success(f"✅ 프로젝트별 사용량 데이터가 준비되었습니다 ({buckets_count}개의 데이터 버킷)")
                else:
                    st.warning("⚠️ 업로드된 데이터의 구조가 예상과 다릅니다.")
            else:
                st.warning("⚠️ 왼쪽 사이드바에서 프로젝트별 사용량 데이터를 먼저 업로드해주세요.")
            
            # 예산 모니터링은 프로젝트별 사용량 데이터가 있고 예산이 설정된 경우에만 가능
            if (hasattr(st.session_state, 'project_budgets') and st.session_state.project_budgets and 
                st.session_state.project_usage_data is not None):
                
                # 실제 사용량 데이터에서 프로젝트별 비용 추출
                st.subheader("💹 프로젝트별 예산 대비 사용률")
                
                # 프로젝트별 사용량 계산 (세션 상태의 프로젝트 데이터 사용)
                project_usage = calculate_project_usage(st.session_state.project_usage_data)
                
                # 예산이 설정된 프로젝트들의 모니터링 정보
                monitoring_data = []
                
                for project_id, budget in st.session_state.project_budgets.items():
                    project_name = next((p["name"] for p in st.session_state.get('budget_projects', []) if p["id"] == project_id), "Unknown")
                    
                    # 실제 사용량 가져오기
                    actual_usage = 0
                    if project_id in project_usage:
                        actual_usage = project_usage[project_id]["total_cost"]
                    
                    usage_rate = (actual_usage / budget) * 100 if budget > 0 else 0
                    
                    # 상태 결정 (초과 사용 관리와 동일한 기준)
                    if actual_usage > budget:
                        status = "🔴 위험 (초과)"
                    elif usage_rate >= 90:
                        status = "🟠 경고"
                    elif usage_rate >= 70:
                        status = "🟡 주의"
                    else:
                        status = "🟢 안전"
                    
                    monitoring_data.append({
                        "프로젝트": project_name,
                        "예산": f"${budget:.2f}",
                        "사용량": f"${actual_usage:.2f}",
                        "사용률": f"{usage_rate:.1f}%",
                        "상태": status,
                        "남은 예산": f"${max(0, budget - actual_usage):.2f}"
                    })
                
                if monitoring_data:
                    # 프로젝트별 예산 대비 사용률 테이블 (전체 너비 사용)
                    st.subheader("📋 프로젝트별 예산 사용 현황")
                    monitoring_df = pd.DataFrame(monitoring_data)
                    
                    # 전체 너비를 활용하여 테이블 표시
                    # Streamlit 1.12.0에서 width를 조정하는 방법
                    st.dataframe(monitoring_df, width=1200, height=400)
                    
                    # 요약 통계 (실제 데이터 기반)
                    total_budget = sum(st.session_state.project_budgets.values())
                    total_usage = sum(float(row["사용량"][1:]) for row in monitoring_data)  # $ 제거 후 float 변환
                    overall_usage_rate = (total_usage / total_budget) * 100 if total_budget > 0 else 0
                    
                    # 초과 프로젝트 개수 계산
                    overage_count = len([row for row in monitoring_data if "초과" in row["상태"]])
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📊 총 예산", f"${total_budget:.2f}")
                    with col2:
                        st.metric("💸 총 사용량", f"${total_usage:.2f}")
                    with col3:
                        st.metric("📈 전체 사용률", f"{overall_usage_rate:.1f}%")
                    with col4:
                        st.metric("🚨 초과 프로젝트", f"{overage_count}개", delta=f"-{overage_count}" if overage_count > 0 else None)
                    
                    # 경고 알림 (개수만 표시)
                    high_usage_projects = [row for row in monitoring_data if float(row["사용률"][:-1]) >= 90]
                    if high_usage_projects:
                        st.error(f"⚠️ {len(high_usage_projects)}개 프로젝트가 예산의 90% 이상을 사용했습니다!")
                else:
                    st.info("예산이 설정된 프로젝트가 없습니다.")
                    
            elif not hasattr(st.session_state, 'project_budgets') or not st.session_state.project_budgets:
                st.warning("⚠️ 먼저 프로젝트별 예산을 설정해주세요.")
            elif st.session_state.project_usage_data is None:
                st.warning("⚠️ 왼쪽 사이드바에서 프로젝트별 사용량 JSON 파일을 업로드해주세요.")
            else:
                st.warning("⚠️ 예산 설정과 프로젝트별 사용량 데이터가 모두 필요합니다.")
        
        with tab4:
            st.subheader("⚠️ 초과 사용 관리")
            st.info("💡 이 기능은 설정된 예산을 초과하여 사용한 프로젝트를 분석하고 관리합니다.")
            
            # 프로젝트별 사용량 데이터 상태 확인
            if st.session_state.project_usage_data is not None:
                # 파일 구조 간단 확인
                if isinstance(st.session_state.project_usage_data, dict) and "data" in st.session_state.project_usage_data:
                    buckets_count = len(st.session_state.project_usage_data["data"])
                    st.success(f"✅ 프로젝트별 사용량 데이터가 준비되었습니다 ({buckets_count}개의 데이터 버킷)")
                else:
                    st.warning("⚠️ 업로드된 데이터의 구조가 예상과 다릅니다.")
            else:
                st.warning("⚠️ 왼쪽 사이드바에서 프로젝트별 사용량 데이터를 먼저 업로드해주세요.")
            
            # 초과 사용 분석은 예산이 설정되어 있고 프로젝트별 사용량 데이터가 있는 경우에만 가능
            if (hasattr(st.session_state, 'project_budgets') and st.session_state.project_budgets and 
                st.session_state.project_usage_data is not None):
                
                # 프로젝트별 사용량 계산
                if st.button("🔍 초과 사용 분석 실행", key="overage_analysis"):
                    with st.spinner("프로젝트별 사용량을 분석하는 중..."):
                        # 프로젝트별 사용량 계산 (세션 상태의 프로젝트 데이터 사용)
                        project_usage = calculate_project_usage(st.session_state.project_usage_data)
                        st.session_state.project_usage = project_usage
                        
                        # 예산 초과 프로젝트 찾기
                        projects_info = getattr(st.session_state, 'budget_projects', None)
                        overages = find_budget_overages(
                            project_usage, 
                            st.session_state.project_budgets, 
                            projects_info
                        )
                        st.session_state.budget_overages = overages
                        
                        if overages:
                            st.error(f"⚠️ {len(overages)}개 프로젝트가 예산을 초과했습니다!")
                        else:
                            st.success("✅ 모든 프로젝트가 예산 내에서 사용 중입니다.")
                
                # 초과 사용 분석 결과 표시
                if hasattr(st.session_state, 'budget_overages') and st.session_state.budget_overages:
                    st.subheader("🚨 예산 초과 프로젝트")
                    
                    overage_data = []
                    total_overage = 0
                    
                    for overage in st.session_state.budget_overages:
                        overage_data.append({
                            "프로젝트": overage["project_name"],
                            "예산": f"${overage['budget']:.2f}",
                            "실제 사용": f"${overage['actual_usage']:.2f}",
                            "초과 금액": f"${overage['overage_amount']:.2f}",
                            "초과율": f"{overage['overage_percentage']:.1f}%",
                            "상태": "🔴 위험" if overage['overage_percentage'] > 50 else "🟡 주의"
                        })
                        total_overage += overage["overage_amount"]
                    
                    # 초과 프로젝트 테이블
                    overage_df = pd.DataFrame(overage_data)
                    st.dataframe(overage_df)
                    
                    # 초과 사용 요약 통계
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🚨 초과 프로젝트", f"{len(st.session_state.budget_overages)}개")
                    with col2:
                        total_budget = sum(st.session_state.project_budgets.values())
                        st.metric("📊 총 예산", f"${total_budget:.2f}")
                    with col3:
                        st.metric("💸 총 초과 금액", f"${total_overage:.2f}")
                    with col4:
                        total_budget_sum = sum(st.session_state.project_budgets.values()) if st.session_state.project_budgets else 0
                        overage_rate = (total_overage / total_budget_sum) * 100 if total_budget_sum > 0 else 0
                        st.metric("📈 전체 초과율", f"{overage_rate:.1f}%")
                    
                    # 프로젝트별 API 키 관리
                    st.subheader("🔑 프로젝트별 API 키 관리")
                    st.info("💡 예산을 초과한 프로젝트의 API 키를 관리하고 필요시 삭제할 수 있습니다.")
                    
                    # 프로젝트 선택
                    selected_project = st.selectbox(
                        "API 키를 관리할 프로젝트 선택",
                        options=[overage["project_name"] for overage in st.session_state.budget_overages],
                        help="예산을 초과한 프로젝트의 API 키를 확인하고 관리할 수 있습니다",
                        key="overage_project_select"
                    )
                    
                    if selected_project:
                        # 선택된 프로젝트의 정보 찾기
                        selected_overage = next(
                            (overage for overage in st.session_state.budget_overages 
                             if overage["project_name"] == selected_project), 
                            None
                        )
                        
                        if selected_overage:
                            project_id = selected_overage["project_id"]
                            
                            # 프로젝트 정보 표시
                            st.warning(f"⚠️ **{selected_project}** 프로젝트 - 예산 초과: ${selected_overage['overage_amount']:.2f}")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("💰 설정 예산", f"${selected_overage['budget']:.2f}")
                            with col2:
                                st.metric("💸 실제 사용", f"${selected_overage['actual_usage']:.2f}")
                            with col3:
                                st.metric("📊 초과율", f"{selected_overage['overage_percentage']:.1f}%")
                            
                            # API 키 목록 가져오기
                            if st.button("🔄 API 키 목록 새로고침", key="refresh_overage_api_keys"):
                                with st.spinner("API 키 목록을 가져오는 중..."):
                                    from utils import get_project_api_keys
                                    api_keys = get_project_api_keys(project_id, admin_api_key)
                                    
                                    if api_keys:
                                        st.session_state.overage_api_keys = api_keys
                                        st.session_state.overage_project_id = project_id
                                        st.success(f"✅ {len(api_keys)}개의 API 키를 가져왔습니다.")
                                    else:
                                        st.warning("API 키를 찾을 수 없습니다.")
                                        st.session_state.overage_api_keys = []
                            
                            # API 키 목록 표시 및 관리
                            if hasattr(st.session_state, 'overage_api_keys') and st.session_state.overage_api_keys:
                                st.subheader("🗝️ API 키 목록")
                                
                                # API 키 데이터 준비
                                api_key_data = []
                                for key in st.session_state.overage_api_keys:
                                    # 날짜 형식 처리
                                    created_at = key.get("created_at", "N/A")
                                    if created_at != "N/A" and isinstance(created_at, (int, float)):
                                        try:
                                            from datetime import datetime
                                            created_at = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M:%S")
                                        except:
                                            created_at = str(created_at)
                                    
                                    last_used = key.get("last_used_at", "미사용")
                                    if last_used and last_used != "미사용" and isinstance(last_used, (int, float)):
                                        try:
                                            from datetime import datetime
                                            last_used = datetime.fromtimestamp(last_used).strftime("%Y-%m-%d %H:%M:%S")
                                        except:
                                            last_used = str(last_used)
                                    elif not last_used:
                                        last_used = "미사용"
                                    
                                    api_key_data.append({
                                        "키 이름": str(key.get("name", "N/A")),
                                        "키 ID": str(key.get("id", "N/A")),
                                        "생성일": str(created_at),
                                        "마지막 사용": str(last_used),
                                        "소유자": str(key.get("owner", {}).get("name", "N/A") if key.get("owner") else "N/A")
                                    })
                                
                                # API 키 테이블 표시
                                api_keys_df = pd.DataFrame(api_key_data)
                                st.dataframe(api_keys_df)
                                
                                # API 키 선택 및 삭제
                                st.subheader("🗑️ API 키 삭제")
                                
                                # 개별 삭제
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    selected_key_name = st.selectbox(
                                        "삭제할 API 키 선택",
                                        options=["선택하세요..."] + [key.get("name", f"ID: {key.get('id', 'Unknown')}") for key in st.session_state.overage_api_keys],
                                        key="select_key_to_delete"
                                    )
                                
                                with col2:
                                    if st.button("🗑️ 선택한 키 삭제", key="delete_single_key", disabled=(selected_key_name == "선택하세요...")):
                                        if selected_key_name != "선택하세요...":
                                            # 선택된 키 정보 찾기
                                            selected_key = None
                                            for key in st.session_state.overage_api_keys:
                                                key_name = key.get("name", f"ID: {key.get('id', 'Unknown')}")
                                                if key_name == selected_key_name:
                                                    selected_key = key
                                                    break
                                            
                                            if selected_key:
                                                # 확인 팝업 (세션 상태로 관리)
                                                st.session_state.delete_confirm = {
                                                    "type": "single",
                                                    "project_name": selected_project,
                                                    "key_name": selected_key.get("name", "N/A"),
                                                    "key_id": selected_key.get("id"),
                                                    "project_id": project_id
                                                }
                                
                                # 일괄 삭제
                                st.markdown("---")
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.warning("⚠️ **위험**: 프로젝트의 모든 API 키를 일괄 삭제합니다.")
                                    
                                with col2:
                                    if st.button("🗑️ 전체 키 삭제", key="delete_all_keys"):
                                        # 일괄 삭제 확인 팝업
                                        st.session_state.delete_confirm = {
                                            "type": "bulk",
                                            "project_name": selected_project,
                                            "key_count": len(st.session_state.overage_api_keys),
                                            "keys": st.session_state.overage_api_keys,
                                            "project_id": project_id
                                        }
                
                # 삭제 확인 팝업 처리
                if hasattr(st.session_state, 'delete_confirm') and st.session_state.delete_confirm:
                    confirm_data = st.session_state.delete_confirm
                    
                    if confirm_data["type"] == "single":
                        # 개별 키 삭제 확인
                        st.error(f"⚠️ **삭제 확인**")
                        st.write(f"**프로젝트**: {confirm_data['project_name']}")
                        st.write(f"**API 키 이름**: {confirm_data['key_name']}")
                        st.write(f"**키 ID**: {confirm_data['key_id']}")
                        st.write("이 작업은 되돌릴 수 없습니다. 정말 삭제하시겠습니까?")
                        
                        col1, col2, col3 = st.columns([1, 1, 2])
                        
                        with col1:
                            if st.button("✅ 삭제 확인", key="confirm_delete"):
                                with st.spinner("API 키를 삭제하는 중..."):
                                    from utils import delete_api_key
                                    success = delete_api_key(
                                        confirm_data["project_id"], 
                                        confirm_data["key_id"], 
                                        admin_api_key
                                    )
                                    
                                    if success:
                                        st.success(f"✅ API 키 '{confirm_data['key_name']}'가 성공적으로 삭제되었습니다.")
                                        # API 키 목록 새로고침
                                        from utils import get_project_api_keys
                                        updated_keys = get_project_api_keys(confirm_data["project_id"], admin_api_key)
                                        st.session_state.overage_api_keys = updated_keys if updated_keys else []
                                    else:
                                        st.error("❌ API 키 삭제에 실패했습니다.")
                                    
                                    # 확인 상태 초기화
                                    del st.session_state.delete_confirm
                                    st.experimental_rerun()
                        
                        with col2:
                            if st.button("❌ 취소", key="cancel_delete"):
                                del st.session_state.delete_confirm
                                st.experimental_rerun()
                    
                    elif confirm_data["type"] == "bulk":
                        # 일괄 삭제 확인
                        st.error(f"⚠️ **일괄 삭제 확인**")
                        st.write(f"**프로젝트**: {confirm_data['project_name']}")
                        st.write(f"**삭제할 키 개수**: {confirm_data['key_count']}개")
                        st.write("**모든 API 키가 삭제되어 프로젝트 접근이 불가능해집니다.**")
                        st.write("이 작업은 되돌릴 수 없습니다. 정말 모든 키를 삭제하시겠습니까?")
                        
                        col1, col2, col3 = st.columns([1, 1, 2])
                        
                        with col1:
                            if st.button("✅ 일괄 삭제 확인", key="confirm_bulk_delete"):
                                with st.spinner("모든 API 키를 삭제하는 중..."):
                                    from utils import bulk_delete_api_keys
                                    
                                    # 키 정보 준비
                                    keys_to_delete = [
                                        (confirm_data["project_id"], key.get("id"), key.get("name", "N/A"))
                                        for key in confirm_data["keys"]
                                    ]
                                    
                                    results = bulk_delete_api_keys(keys_to_delete, admin_api_key)
                                    
                                    if results["success"]:
                                        st.success(f"✅ {len(results['success'])}개의 API 키가 성공적으로 삭제되었습니다.")
                                    
                                    if results["failed"]:
                                        st.error(f"❌ {len(results['failed'])}개의 API 키 삭제에 실패했습니다.")
                                    
                                    # API 키 목록 새로고침
                                    from utils import get_project_api_keys
                                    updated_keys = get_project_api_keys(confirm_data["project_id"], admin_api_key)
                                    st.session_state.overage_api_keys = updated_keys if updated_keys else []
                                    
                                    # 확인 상태 초기화
                                    del st.session_state.delete_confirm
                                    st.experimental_rerun()
                        
                        with col2:
                            if st.button("❌ 취소", key="cancel_bulk_delete"):
                                del st.session_state.delete_confirm
                                st.experimental_rerun()
                
                elif hasattr(st.session_state, 'project_usage') and st.session_state.project_usage:
                    # budget_overages가 존재하고 비어있지 않으면 초과 프로젝트가 있다는 의미
                    if hasattr(st.session_state, 'budget_overages') and st.session_state.budget_overages:
                        # 초과 프로젝트가 있는 경우는 위에서 이미 처리되므로 여기서는 아무것도 하지 않음
                        pass
                    else:
                        # 분석은 완료되었지만 초과 프로젝트가 없는 경우
                        st.success("✅ 현재 모든 프로젝트가 예산 내에서 사용 중입니다.")
                else:
                    st.info("🔍 '초과 사용 분석 실행' 버튼을 클릭하여 분석을 시작하세요.")
                    
            elif not hasattr(st.session_state, 'project_budgets') or not st.session_state.project_budgets:
                st.warning("⚠️ 먼저 프로젝트별 예산을 설정해주세요.")
                st.info("1. '🎯 프로젝트별 예산 설정' 탭에서 예산을 설정하세요.")
                st.info("2. 또는 '📊 일괄 예산 설정' 탭에서 모든 프로젝트에 예산을 적용하세요.")
            elif st.session_state.project_usage_data is None:
                st.warning("⚠️ 왼쪽 사이드바에서 프로젝트별 사용량 JSON 파일을 업로드해주세요.")
                st.info("💡 프로젝트별 사용량 분석을 위해서는 OpenAI에서 다운로드한 프로젝트 기준 JSON 데이터가 필요합니다.")
            else:
                st.warning("⚠️ 예산 설정과 프로젝트별 사용량 데이터가 모두 필요합니다.")

