import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="팀스파르타 수강생 대시보드", layout="wide", page_icon="🎓")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f0f4ff 0%, #faf8ff 100%);
    font-family: 'Segoe UI', sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #ffffff; }

.dash-title {
    font-size: 2.2rem; font-weight: 800; color: #2d2d5e; margin-bottom: 4px;
}
.dash-subtitle {
    font-size: 0.95rem; color: #7a7a9d; margin-bottom: 20px;
}
.kpi-card {
    background: #ffffff; border-radius: 16px; padding: 22px 24px;
    box-shadow: 0 4px 20px rgba(100,100,200,0.10); border-left: 5px solid;
    margin-bottom: 8px;
}
.kpi-label {
    font-size: 0.80rem; font-weight: 600; letter-spacing: 0.07em;
    text-transform: uppercase; margin-bottom: 6px;
}
.kpi-value { font-size: 1.85rem; font-weight: 800; line-height: 1.1; }
.kpi-sub { font-size: 0.76rem; margin-top: 4px; opacity: 0.65; }
.section-card {
    background: #ffffff; border-radius: 16px; padding: 24px;
    box-shadow: 0 4px 20px rgba(100,100,200,0.08); margin-bottom: 16px;
}
.section-title { font-size: 1.05rem; font-weight: 700; color: #2d2d5e; margin-bottom: 12px; }
label[data-testid="stWidgetLabel"] p { font-weight: 600 !important; color: #2d2d5e !important; }
[data-testid="stSelectbox"] > div > div {
    background: #ffffff; border: 2px solid #e0e4f5; border-radius: 10px;
}
hr { border-color: #e8eaf6 !important; }
.upload-guide {
    text-align: center; padding: 60px 20px; color: #7a7a9d;
    background: #ffffff; border-radius: 16px;
    box-shadow: 0 4px 20px rgba(100,100,200,0.08);
}
.upload-guide h2 { color: #2d2d5e; font-size: 1.6rem; margin-bottom: 12px; }
.upload-guide p { font-size: 1rem; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)


# ── 사이드바: 파일 업로드 ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📂 데이터 업로드")
    st.markdown("두 엑셀 파일을 업로드하면 자동으로 병합합니다.")
    st.markdown("---")

    master_file = st.file_uploader(
        "📋 수강생 마스터 파일",
        type=["xlsx", "xls"],
        help="팀스파르타_수강생_마스터.xlsx",
        key="master",
    )
    activity_file = st.file_uploader(
        "📊 학습활동 파일",
        type=["xlsx", "xls"],
        help="팀스파르타_수강생_학습활동.xlsx",
        key="activity",
    )

    if master_file and activity_file:
        st.success("✅ 두 파일 업로드 완료!")
    elif master_file or activity_file:
        st.warning("⚠️ 나머지 파일도 업로드해주세요.")
    else:
        st.info("👆 파일을 업로드하면 대시보드가 활성화됩니다.")

    st.markdown("---")
    st.markdown("**병합 기준:** `student_id`")
    st.markdown("**필요 파일:**")
    st.markdown("- 팀스파르타_수강생_마스터.xlsx")
    st.markdown("- 팀스파르타_수강생_학습활동.xlsx")


# ── 업로드 전 안내 화면 ────────────────────────────────────────────────────────
if not (master_file and activity_file):
    st.markdown('<p class="dash-title">🎓 팀스파르타 수강생 대시보드</p>', unsafe_allow_html=True)
    st.markdown('<p class="dash-subtitle">수강생 마스터 × 학습활동 데이터를 병합하여 분석합니다</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="upload-guide">
        <h2>📂 파일을 업로드해주세요</h2>
        <p>
            왼쪽 사이드바에서 두 엑셀 파일을 업로드하면<br>
            자동으로 병합하여 대시보드를 표시합니다.<br><br>
            <strong>팀스파르타_수강생_마스터.xlsx</strong> &nbsp;+&nbsp;
            <strong>팀스파르타_수강생_학습활동.xlsx</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── 데이터 로드 & 병합 ─────────────────────────────────────────────────────────
@st.cache_data
def load_and_merge(mf, af):
    master = pd.read_excel(mf)
    activity = pd.read_excel(af)
    df = pd.merge(master, activity, on="student_id", how="inner")
    df["등록일"] = pd.to_datetime(df["등록일"], errors="coerce")
    df["최근접속일"] = pd.to_datetime(df["최근접속일"], errors="coerce")
    return master, activity, df

master_df, activity_df, df = load_and_merge(master_file, activity_file)

# ── 제목 ──────────────────────────────────────────────────────────────────────
st.markdown('<p class="dash-title">🎓 팀스파르타 수강생 대시보드</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="dash-subtitle">수강생 {len(df):,}명 · 마스터 {len(master_df):,}행 × 학습활동 {len(activity_df):,}행 병합 완료</p>',
    unsafe_allow_html=True,
)

# ── 필터 ──────────────────────────────────────────────────────────────────────
fc1, fc2, fc3, _ = st.columns([1, 1, 1, 1])

with fc1:
    track_opts = ["전체"] + sorted(df["트랙명"].dropna().unique().tolist())
    sel_track = st.selectbox("🗂️ 트랙명", track_opts)

with fc2:
    status_opts = ["전체"] + sorted(df["수강상태"].dropna().unique().tolist())
    sel_status = st.selectbox("📌 수강상태", status_opts)

with fc3:
    risk_opts = ["전체"] + sorted(df["이탈위험도"].dropna().unique().tolist())
    sel_risk = st.selectbox("⚠️ 이탈위험도", risk_opts)

fdf = df.copy()
if sel_track != "전체":
    fdf = fdf[fdf["트랙명"] == sel_track]
if sel_status != "전체":
    fdf = fdf[fdf["수강상태"] == sel_status]
if sel_risk != "전체":
    fdf = fdf[fdf["이탈위험도"] == sel_risk]

st.markdown("---")

if fdf.empty:
    st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다.")
    st.stop()

# ── KPI 카드 ──────────────────────────────────────────────────────────────────
total_students = len(fdf)
avg_attendance = fdf["출석률(%)"].mean()
avg_assignment = fdf["과제제출률(%)"].mean()
completion_rate = (fdf["수강상태"] == "수료").sum() / total_students * 100
employment_rate = (fdf["취업연계여부"] == "연계완료").sum() / total_students * 100

k1, k2, k3, k4, k5 = st.columns(5)

kpi_data = [
    (k1, "👥 수강생 수", f"{total_students:,}명", "필터 적용 인원", "#6366f1"),
    (k2, "📅 평균 출석률", f"{avg_attendance:.1f}%", "전체 평균", "#10b981"),
    (k3, "📝 평균 과제제출률", f"{avg_assignment:.1f}%", "전체 평균", "#f59e0b"),
    (k4, "🎓 수료율", f"{completion_rate:.1f}%", "수료 / 전체", "#3b82f6"),
    (k5, "💼 취업연계율", f"{employment_rate:.1f}%", "연계완료 / 전체", "#ec4899"),
]

for col, label, value, sub, color in kpi_data:
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{color};">
            <div class="kpi-label" style="color:{color};">{label}</div>
            <div class="kpi-value" style="color:{color};">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: 트랙별 현황 + 수강상태 분포 + 이탈위험도 ───────────────────────────
r1c1, r1c2, r1c3 = st.columns([1.4, 1, 1])

with r1c1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📚 트랙별 수강생 수</p>', unsafe_allow_html=True)
    track_cnt = fdf["트랙명"].value_counts().reset_index()
    track_cnt.columns = ["트랙명", "수강생 수"]
    fig = px.bar(
        track_cnt, x="수강생 수", y="트랙명", orientation="h",
        color="수강생 수",
        color_continuous_scale=[[0, "#c7d2fe"], [1, "#6366f1"]],
        text="수강생 수", height=320,
    )
    fig.update_traces(textposition="outside", marker_line_width=0)
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False,
        yaxis=dict(autorange="reversed", title=""),
        xaxis=dict(title="", showgrid=True, gridcolor="#f0f0f8"),
        margin=dict(t=10, b=10, l=10, r=60),
        font=dict(family="Segoe UI", size=12),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r1c2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📌 수강상태 분포</p>', unsafe_allow_html=True)
    status_cnt = fdf["수강상태"].value_counts().reset_index()
    status_cnt.columns = ["수강상태", "인원"]
    colors_status = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#3b82f6"]
    fig2 = px.pie(
        status_cnt, names="수강상태", values="인원",
        color_discrete_sequence=colors_status, height=300,
        hole=0.45,
    )
    fig2.update_traces(textposition="outside", textinfo="percent+label")
    fig2.update_layout(
        paper_bgcolor="white", showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        font=dict(family="Segoe UI", size=12),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r1c3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">⚠️ 이탈위험도 분포</p>', unsafe_allow_html=True)
    risk_cnt = fdf["이탈위험도"].value_counts().reset_index()
    risk_cnt.columns = ["이탈위험도", "인원"]
    risk_color = {"낮음": "#10b981", "보통": "#f59e0b", "높음": "#ef4444"}
    fig3 = px.pie(
        risk_cnt, names="이탈위험도", values="인원",
        color="이탈위험도",
        color_discrete_map=risk_color,
        height=300, hole=0.45,
    )
    fig3.update_traces(textposition="outside", textinfo="percent+label")
    fig3.update_layout(
        paper_bgcolor="white", showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        font=dict(family="Segoe UI", size=12),
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Row 2: 출석률 × 과제제출률 산점도 + 트랙별 학습지표 ──────────────────────
r2c1, r2c2 = st.columns([1.1, 0.9])

with r2c1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🔍 출석률 × 과제제출률 (이탈위험도별)</p>', unsafe_allow_html=True)
    fig4 = px.scatter(
        fdf,
        x="출석률(%)", y="과제제출률(%)",
        color="이탈위험도",
        color_discrete_map=risk_color,
        hover_data=["이름", "트랙명", "수강상태", "퀴즈평균점수"],
        height=360,
        opacity=0.8,
    )
    fig4.update_traces(marker=dict(size=9, line=dict(width=0.5, color="white")))
    fig4.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#f0f0f8", title="출석률 (%)"),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f8", title="과제제출률 (%)"),
        legend=dict(title="이탈위험도", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=30, b=20, l=20, r=20),
        font=dict(family="Segoe UI", size=12),
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r2c2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📈 트랙별 평균 학습지표</p>', unsafe_allow_html=True)
    track_avg = (
        fdf.groupby("트랙명")[["출석률(%)", "과제제출률(%)", "퀴즈평균점수"]]
        .mean()
        .round(1)
        .reset_index()
    )
    fig5 = go.Figure()
    metrics = [
        ("출석률(%)", "#6366f1"),
        ("과제제출률(%)", "#10b981"),
        ("퀴즈평균점수", "#f59e0b"),
    ]
    for col, color in metrics:
        fig5.add_trace(go.Bar(
            name=col, x=track_avg["트랙명"], y=track_avg[col],
            marker_color=color, opacity=0.85,
        ))
    fig5.update_layout(
        barmode="group",
        plot_bgcolor="white", paper_bgcolor="white",
        height=340,
        xaxis=dict(title="", tickangle=-20),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f8", title="점수 / %"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=30, b=20, l=20, r=20),
        font=dict(family="Segoe UI", size=11),
    )
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Row 3: 유입채널 + 과정 브랜드 × 취업연계여부 ──────────────────────────────
r3c1, r3c2 = st.columns(2)

with r3c1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📣 유입채널별 수강생 수</p>', unsafe_allow_html=True)
    channel_cnt = fdf["유입채널"].value_counts().reset_index()
    channel_cnt.columns = ["유입채널", "수강생 수"]
    fig6 = px.bar(
        channel_cnt, x="유입채널", y="수강생 수",
        color="수강생 수",
        color_continuous_scale=[[0, "#fde68a"], [1, "#f59e0b"]],
        text="수강생 수", height=300,
    )
    fig6.update_traces(textposition="outside", marker_line_width=0)
    fig6.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False,
        xaxis=dict(title=""),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f8", title="수강생 수"),
        margin=dict(t=20, b=10, l=10, r=10),
        font=dict(family="Segoe UI", size=12),
    )
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r3c2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">💼 취업연계 현황</p>', unsafe_allow_html=True)
    emp_cnt = fdf["취업연계여부"].value_counts().reset_index()
    emp_cnt.columns = ["취업연계여부", "인원"]
    emp_color = {"연계완료": "#10b981", "대상아님": "#94a3b8", "진행중": "#3b82f6", "미연계": "#ef4444"}
    fig7 = px.bar(
        emp_cnt, x="취업연계여부", y="인원",
        color="취업연계여부",
        color_discrete_map=emp_color,
        text="인원", height=300,
    )
    fig7.update_traces(textposition="outside", marker_line_width=0)
    fig7.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False,
        xaxis=dict(title=""),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f8", title="인원"),
        margin=dict(t=20, b=10, l=10, r=10),
        font=dict(family="Segoe UI", size=12),
    )
    st.plotly_chart(fig7, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── 상세 데이터 테이블 ─────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 병합된 수강생 상세 데이터 보기", expanded=False):
    display_cols = [
        "student_id", "이름", "트랙명", "수강상태",
        "출석률(%)", "과제제출률(%)", "주간학습시간(h)",
        "퀴즈평균점수", "프로젝트제출수", "멘토링참여횟수",
        "만족도설문점수", "이탈위험도", "취업연계여부",
        "유입채널", "국비지원여부",
    ]
    show_df = fdf[display_cols].copy()
    show_df["출석률(%)"] = show_df["출석률(%)"].round(1)
    show_df["과제제출률(%)"] = show_df["과제제출률(%)"].round(1)
    st.dataframe(show_df, use_container_width=True, hide_index=True)
    st.caption(f"총 {len(show_df):,}명 표시 중 (원본 마스터 {len(master_df):,}행 + 학습활동 {len(activity_df):,}행 병합)")
