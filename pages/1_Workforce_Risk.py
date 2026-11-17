
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# 1. Page Setup and Data
# ==========================================

st.set_page_config(
    page_title="Layton Safety Analytics",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent

project = pd.read_csv(
    BASE_DIR / "data" / "processed" / "project_workforce_kpis.csv"
)

# ==========================================
# 2. Dashboard Style
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #F8FAFC;
}
h1, h2, h3 {
    color: #17324D !important;
}
div[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border: 1px solid #DCE5EF;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


def style_chart(fig):
    fig.update_layout(
        template="plotly_white",
        font={"family": "Arial", "size": 15, "color": "#1F2937"},
        title_font={"size": 19, "color": "#111827"},
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=400,
        margin={"l": 30, "r": 25, "t": 60, "b": 40}
    )

    fig.update_xaxes(
        tickfont={"size": 14, "color": "#1F2937"},
        title_font={"size": 15, "color": "#111827"},
        gridcolor="#E2E8F0"
    )

    fig.update_yaxes(
        tickfont={"size": 14, "color": "#1F2937"},
        title_font={"size": 15, "color": "#111827"},
        gridcolor="#E2E8F0"
    )

    return fig


# ==========================================
# 3. Dashboard Header and Filter
# ==========================================

st.title("Workforce & Operational Risk")


st.caption(
    "Synthetic dataset | January 2024 – September 2026"
)

all_jobs = sorted(project["JOB_ID"].unique())

selected_jobs = st.multiselect(
    "Select Projects",
    options=all_jobs,
    default=all_jobs
)

filtered = project[
    project["JOB_ID"].isin(selected_jobs)
].copy()

if filtered.empty:
    st.warning("Please select at least one project.")
    st.stop()


# ==========================================
# 4. KPI Summary
# ==========================================

total_hours = filtered["TOTAL_HOURS"].sum()
overtime_hours = filtered["OVERTIME_HOURS"].sum()
recordable = filtered["RECORDABLE_INCIDENTS"].sum()

overtime_rate = (
    overtime_hours / total_hours * 100
    if total_hours > 0 else 0
)

incident_rate = (
    recordable * 200000 / total_hours
    if total_hours > 0 else 0
)

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Projects",
    filtered["JOB_ID"].nunique()
)

k2.metric(
    "Overtime Rate",
    f"{overtime_rate:.2f}%"
)

k3.metric(
    "Recordable Incidents",
    f"{recordable:.0f}"
)

k4.metric(
    "Incident Rate",
    f"{incident_rate:.3f}"
)


# ==========================================
# 5. Chart 1: Overtime vs Incident Rate
# ==========================================

st.divider()
st.subheader("Project-Level Risk Analysis")

col1, col2 = st.columns(2)

with col1:
    fig1 = px.scatter(
        filtered,
        x="OVERTIME_RATE",
        y="INCIDENT_RATE",
        hover_data=[
            "JOB_ID",
            "AVG_HEADCOUNT",
            "TOTAL_HOURS",
            "RECORDABLE_INCIDENTS"
        ],
        title="Overtime vs. Incident Rate",
        labels={
            "OVERTIME_RATE": "Overtime Rate (%)",
            "INCIDENT_RATE": "Incident Rate per 200,000 Hours"
        },
        color_discrete_sequence=["#1675C5"]
    )

    fig1.update_traces(
        marker={"size": 9, "opacity": 0.85}
    )

    st.plotly_chart(
        style_chart(fig1),
        use_container_width=True
    )

    overtime_corr = filtered["OVERTIME_RATE"].corr(
        filtered["INCIDENT_RATE"]
    )

    if pd.notna(overtime_corr):
        st.metric(
            "Overtime Correlation (Pearson r)",
            f"{overtime_corr:+.3f}"
        )
    else:
        st.info("Correlation unavailable for this selection.")


# ==========================================
# 6. Chart 2: Headcount vs Incident Rate
# ==========================================

with col2:
    fig2 = px.scatter(
        filtered,
        x="AVG_HEADCOUNT",
        y="INCIDENT_RATE",
        hover_data=[
            "JOB_ID",
            "OVERTIME_RATE",
            "TOTAL_HOURS",
            "RECORDABLE_INCIDENTS"
        ],
        title="Headcount vs. Incident Rate",
        labels={
            "AVG_HEADCOUNT": "Average Daily Headcount",
            "INCIDENT_RATE": "Incident Rate per 200,000 Hours"
        },
        color_discrete_sequence=["#1675C5"]
    )

    fig2.update_traces(
        marker={"size": 9, "opacity": 0.85}
    )

    st.plotly_chart(
        style_chart(fig2),
        use_container_width=True
    )

    headcount_corr = filtered["AVG_HEADCOUNT"].corr(
        filtered["INCIDENT_RATE"]
    )

    if pd.notna(headcount_corr):
        st.metric(
            "Headcount Correlation (Pearson r)",
            f"{headcount_corr:+.3f}"
        )
    else:
        st.info("Correlation unavailable for this selection.")


# ==========================================
# 7. Annual Workforce & Safety Trends
# ==========================================

st.divider()
st.subheader("Annual Workforce & Safety Trends")

annual = pd.DataFrame({
    "YEAR": ["2024", "2025", "2026 (Jan–Sep)"],
    "OVERTIME_RATE": [10.27, 9.96, 10.43],
    "INCIDENT_RATE": [1.646, 0.870, 0.444]
})

col3, col4 = st.columns(2)


# Chart 3: Annual Overtime Rate
with col3:
    fig3 = px.line(
        annual,
        x="YEAR",
        y="OVERTIME_RATE",
        markers=True,
        title="Annual Overtime Rate",
        labels={
            "YEAR": "Year",
            "OVERTIME_RATE": "Overtime Rate (%)"
        }
    )

    fig3.update_xaxes(type="category")

    fig3.update_traces(
        line={"color": "#1675C5", "width": 3},
        marker={"size": 10, "color": "#1675C5"}
    )

    st.plotly_chart(
        style_chart(fig3),
        use_container_width=True
    )


# Chart 4: Annual Recordable Incident Rate
with col4:
    fig4 = px.line(
        annual,
        x="YEAR",
        y="INCIDENT_RATE",
        markers=True,
        title="Annual Recordable Incident Rate",
        labels={
            "YEAR": "Year",
            "INCIDENT_RATE": "Incidents per 200,000 Hours"
        }
    )

    fig4.update_xaxes(type="category")

    fig4.update_traces(
        line={"color": "#0F766E", "width": 3},
        marker={"size": 10, "color": "#0F766E"}
    )

    st.plotly_chart(
        style_chart(fig4),
        use_container_width=True
    )

st.caption(
    "Note: Annual trends summarize all projects and do not "
    "change with the project filter. 2026 covers January–September "
    "only. Incident rates are normalized per 200,000 work hours."
)


# ==========================================
# 8. Key Findings & Recommendations
# ==========================================

st.divider()
st.subheader("Key Findings & Recommendations")

st.markdown("""
**Finding 1 — Overtime and Safety Risk**

Overtime rate shows a weak positive correlation with
recordable incident rate (r = 0.152).

**Finding 2 — Workforce Size and Safety Risk**

Average headcount also shows a weak positive correlation
with incident rate (r = 0.164).

**Finding 3 — Annual Safety Trends**

Recordable incident rates declined from 2024 to 2026,
while overtime rates remained around 10%.

**Management Recommendation**

Monitor overtime exposure and workforce conditions alongside
safety inspections, hazard reporting, and project characteristics.
Investigate projects with elevated incident rates before making
operational policy changes.
""")

st.caption(
    "Findings are based on all 40 projects. "
    "Correlations do not establish causation. "
    "Results are based on synthetic data."
)
