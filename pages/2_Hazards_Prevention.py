from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


def style_chart(fig, height=450):
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={
            "family": "Arial",
            "size": 15,
            "color": "#1F2937"
        },
        title_font={
            "size": 19,
            "color": "#111827"
        },
        xaxis={
            "tickfont": {"size": 14, "color": "#1F2937"},
            "title_font": {"size": 15, "color": "#1F2937"},
            "gridcolor": "#E2E8F0"
        },
        yaxis={
            "tickfont": {"size": 14, "color": "#1F2937"},
            "title_font": {"size": 15, "color": "#1F2937"},
            "gridcolor": "#E2E8F0"
        },
        legend={"font": {"size": 14}},
        margin={"l": 30, "r": 30, "t": 70, "b": 40}
    )
    return fig
st.set_page_config(
    page_title="Hazards & Prevention",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "teammates" / "jenny"


# Find CSV files, including nested folders
def load_csv(filename):
    matches = list(DATA_DIR.rglob(filename))

    if not matches:
        st.error(f"Cannot find {filename}")
        st.stop()

    return pd.read_csv(matches[0])


# Load Jenny's project-level data
project = load_csv("member3_project_kpis.csv")
hazard = load_csv("issue_hazard_summary.csv")
followup = load_csv("good_catch_followup_by_severity.csv")


# Page header
st.title("Hazards & Prevention")
st.caption(
    "Layton Construction Safety Analytics | "
    "Synthetic Data"
)


# Project filter
selected_projects = st.multiselect(
    "Select Projects",
    options=sorted(project["JOB_ID"].unique()),
    default=sorted(project["JOB_ID"].unique())
)

filtered = project[
    project["JOB_ID"].isin(selected_projects)
]

if filtered.empty:
    st.warning("Please select at least one project.")
    st.stop()


# KPI calculations
total_issues = filtered["TOTAL_ISSUES"].sum()
unresolved = filtered["UNRESOLVED_ISSUES"].sum()
high_critical = filtered["HIGH_CRITICAL_UNRESOLVED"].sum()

total_hours = filtered["TOTAL_HOURS"].sum()
good_catches = filtered["GOOD_CATCHES"].sum()

good_catch_rate = (
    good_catches * 200000 / total_hours
    if total_hours > 0 else 0
)


# KPI cards
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Safety Issues", f"{total_issues:,.0f}")
c2.metric("Unresolved Issues", f"{unresolved:,.0f}")
c3.metric(
    "High/Critical Unresolved",
    f"{high_critical:,.0f}"
)
c4.metric(
    "Good Catch Rate",
    f"{good_catch_rate:.2f}"
)

st.caption(
    "Good Catch Rate = Good Catches per 200,000 "
    "work hours."
)


# Chart 1: Unresolved issues by project
st.subheader("Unresolved Issues by Project")

top_projects = filtered.nlargest(
    10, "UNRESOLVED_ISSUES"
).sort_values("UNRESOLVED_ISSUES")

fig1 = px.bar(
    top_projects,
    x="UNRESOLVED_ISSUES",
    y="JOB_NAME",
    orientation="h",
    color="UNRESOLVED_ISSUES",
    color_continuous_scale="Blues",
    labels={
        "UNRESOLVED_ISSUES": "Unresolved Issues",
        "JOB_NAME": "Project"
    },
    title="Top 10 Projects with Unresolved Safety Issues"
)

fig1.update_layout(
    height=480,
    coloraxis_showscale=False
)

st.plotly_chart(fig1, use_container_width=True)


# Chart 2: Hazard categories
st.subheader("Hazard Category Distribution")

hazard_sorted = hazard.sort_values(
    "ISSUE_COUNT",
    ascending=True
)

fig2 = px.bar(
    hazard_sorted,
    x="ISSUE_COUNT",
    y="HAZARD_CATEGORY",
    orientation="h",
    color="ISSUE_COUNT",
    color_continuous_scale="Blues",
    labels={
        "ISSUE_COUNT": "Number of Safety Issues",
        "HAZARD_CATEGORY": "Hazard Category"
    },
    title="Safety Issues by Hazard Category"
)

fig2.update_layout(
    height=480,
    coloraxis_showscale=False
)

st.plotly_chart(fig2, use_container_width=True)

st.caption(
    "Hazard category distribution covers all projects "
    "and does not change with the project filter."
)


# Chart 3: Good Catch follow-up
st.subheader("Good Catch Follow-up by Severity")

fig3 = px.bar(
    followup,
    x="POTENTIAL_SEVERITY",
    y=["COMPLETED_FOLLOWUPS", "OPEN_FOLLOWUPS"],
    barmode="stack",
    labels={
        "POTENTIAL_SEVERITY": "Potential Severity",
        "value": "Number of Follow-ups",
        "variable": "Follow-up Status"
    },
    title="Completed vs Open Good Catch Follow-ups"
)

fig3.update_layout(height=420)

st.plotly_chart(fig3, use_container_width=True)

st.caption(
    "Follow-up status covers all projects and does "
    "not change with the project filter."
)


# Management interpretation
st.subheader("Key Findings & Recommendations")

st.markdown(
    """
    **1. Unresolved Safety Issues**

    Prioritize projects with high numbers of unresolved
    issues, especially high- and critical-severity cases.

    **2. Hazard Prevention**

    Use frequently reported hazard categories to guide
    targeted inspections and preventive training.

    **3. Good Catch Follow-up**

    Monitor open follow-ups and improve closure processes
    so that reported hazards receive timely attention.

    **Management Recommendation**

    Combine issue volume, severity, resolution progress,
    and Good Catch reporting when prioritizing safety
    management resources. These descriptive metrics do
    not establish causal relationships.
    """
)
