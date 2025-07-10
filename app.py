import json
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

from utils import (
    get_total_cost,
    group_by_date,
    group_by_model,
    group_by_userID,
    build_userinfo,
    get_name_with_userID,
    get_userID_with_name,
    rebuild_to_cost,
)


st.set_page_config(layout="wide")

if "userinfo" not in st.session_state:
    st.session_state.userinfo = False
# 파일 업로드 섹션
st.title("OpenAI API Usage Visualizer")

st.subheader("Upload File")
uploaded_file = st.file_uploader(
    "OpenAI Platform - Usage - Cost 탭에서 원하는 기간을 설정하고 User를 기준으로 다운받은 파일을 업로드하세요 (JSON)",
    type="json",
)

if uploaded_file is not None:
    st.subheader("OpenAI API Usage.")
    if not st.session_state.userinfo:
        build_userinfo()
        with open("userinfo.json") as fp:
            st.session_state.userinfo = json.load(fp)

    data = json.load(uploaded_file)

    with st.expander("Total Usage"):
        # 2025년 구조만 지원
        data_ = data  # 전체 data 객체 전달
        
        st.subheader("Total ($) : {:.4f}".format(get_total_cost(data_)[0]))
        grouped_data = group_by_userID(data_)
        userID = grouped_data.keys()  # 사용자 ID
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

        st.dataframe(
            df,
            column_config={
                "name": "User ID",
                "Total Usage(USD)": st.column_config.NumberColumn(
                    "Total Usage",
                    format="%.4f $",
                    help="총 사용량 (달러)",
                ),
                "usage_history": st.column_config.LineChartColumn(
                    "usage transition",
                    y_min=0,
                    y_max=1000,
                    help="사용량 추이 그래프",
                    width=400,
                ),
            },
        )

    with st.expander("Daily Usage by User (관리자에게 문의하세요)"):
        flag = True
        if flag:
            # 2025년 구조만 지원
            data_ = data  # 전체 data 객체 전달

            grouped_data = group_by_userID(data_)
            userID = grouped_data.keys()  # 사용자 ID
            names = sorted(
                [get_name_with_userID(uid, st.session_state.userinfo) or (f"Unknown ({uid[:8]}...)" if uid is not None else "Unknown User") for uid in userID]
            )

            username = st.selectbox(
                label="Username",
                options=names,
            )

            uid = get_userID_with_name(username, st.session_state.userinfo)
            
            # 사용자를 찾지 못한 경우 처리
            if uid is None or uid not in grouped_data:
                st.error(f"사용자 '{username}'의 데이터를 찾을 수 없습니다.")
                st.stop()
            
            personal_total_cost = get_total_cost(grouped_data[uid])[0]
            st.subheader("Total ($) : {:.4f}".format(personal_total_cost))

            # 예시 데이터 생성
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

            data = {"date": date, "model": models, "Total Usage ($)": amounts}

            df = pd.DataFrame(data)

            # 누적 막대그래프 생성
            fig = px.bar(
                df,
                x="date",
                y="Total Usage ($)",
                color="model",
                title="모델별 사용량 합계",
                labels={"Value": "값", "Category": "카테고리"},
                text_auto=True,
            )
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
            st.plotly_chart(fig)

else:
    st.info("파일을 업로드하면 데이터 분석 및 시각화를 진행할 수 있습니다.")
