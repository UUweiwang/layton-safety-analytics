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
active_priority = load_csv("active_project_management_priority.csv")
project_types = load_csv("project_type_executive_summary.csv")


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

fig1.update_layout(coloraxis_showscale=False)
style_chart(fig1, height=480)

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

fig2.update_layout(coloraxis_showscale=False)
style_chart(fig2, height=480)

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

fig3.update_traces(
    marker_color="#16A34A",
    selector={"name": "COMPLETED_FOLLOWUPS"}
)
fig3.update_traces(
    marker_color="#F59E0B",
    selector={"name": "OPEN_FOLLOWUPS"}
)
fig3.for_each_trace(lambda trace: trace.update(
    name={"COMPLETED_FOLLOWUPS": "Completed", "OPEN_FOLLOWUPS": "Open"}.get(trace.name, trace.name),
    legendgroup={"COMPLETED_FOLLOWUPS": "Completed", "OPEN_FOLLOWUPS": "Open"}.get(trace.name, trace.name)
))

style_chart(fig3, height=420)

st.plotly_chart(fig3, use_container_width=True)

st.caption(
    "Follow-up status covers all projects and does "
    "not change with the project filter."
)

# Original labels are retained for transparency. The instructor advised
# treating follow-ups without confirmed completion as completed for this exercise.
# Do not interpret the "Open" source label as a verified unresolved hazard.
recorded_completed = followup["COMPLETED_FOLLOWUPS"].sum()
recorded_open = followup["OPEN_FOLLOWUPS"].sum()
critical_open_label = followup.loc[
    followup["POTENTIAL_SEVERITY"].astype(str).str.lower() == "critical",
    "OPEN_FOLLOWUPS"
].sum()
st.info(
    f"**Data interpretation:** The synthetic source data labels "
    f"{recorded_completed:,.0f} Good Catch follow-ups as Completed and "
    f"{recorded_open:,.0f} as Open (including "
    f"{critical_open_label:,.0f} Critical-severity records). "
    "These are recorded labels, **not independently verified outstanding hazards**. "
    "Instructor clarification recommends assuming follow-ups without "
    "confirmed completion are completed for this exercise. "
    "Before taking management action, validate the actual follow-up and "
    "corrective-action status with the project team."
)


# New: active projects to prioritize for corrective action
st.subheader("Active Project Priorities")
st.caption("Active projects only. Ranked by the number of unresolved High/Critical issues; this is a prioritization view, not a predicted risk score.")
active_view = active_priority[active_priority["JOB_ID"].isin(selected_projects)].copy()
if not active_view.empty:
    top_active = active_view.nlargest(10, "HIGH_CRITICAL_UNRESOLVED").sort_values("HIGH_CRITICAL_UNRESOLVED")
    fig4 = px.bar(
        top_active,
        x="HIGH_CRITICAL_UNRESOLVED", y="JOB_NAME", orientation="h",
        color="HIGH_CRITICAL_UNRESOLVED", color_continuous_scale="OrRd",
        labels={"HIGH_CRITICAL_UNRESOLVED": "Open High/Critical Issues", "JOB_NAME": "Active Project"},
        title="Active Projects with the Most Unresolved High/Critical Issues"
    )
    fig4.update_layout(coloraxis_showscale=False)
    style_chart(fig4, height=470)
    st.plotly_chart(fig4, use_container_width=True)
    st.info("Management action: assign accountable owners and verify closure of high-severity issues on priority projects.")
else:
    st.info("No active projects in the current selection.")

# New: comparison across project types (portfolio-wide summary)
st.subheader("Safety Performance by Project Type")
st.caption("Portfolio-wide comparison; this chart does not respond to the project selector above.")
fig5 = px.bar(
    project_types.sort_values("SAFETY_INCIDENT_RATE", ascending=False),
    x="PROJECT_TYPE", y="SAFETY_INCIDENT_RATE",
    color="SAFETY_INCIDENT_RATE", color_continuous_scale="Blues",
    hover_data=["PROJECT_COUNT", "LTA_RATE", "TOP_SEVERE_HAZARD"],
    labels={"PROJECT_TYPE": "Project Type", "SAFETY_INCIDENT_RATE": "Safety Incident Rate"},
    title="Safety Incident Rate Across Project Types"
)
fig5.update_layout(coloraxis_showscale=False)
style_chart(fig5, height=430)
st.plotly_chart(fig5, use_container_width=True)
st.caption("Compare rates rather than raw incident counts; differences are descriptive and do not establish causation.")

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

    Track documented follow-up status and improve closure records.
    Because the instructor advised assuming unconfirmed follow-ups are
    completed for this exercise, validate statuses before treating a
    recorded Open label as an outstanding safety hazard.

    **4. Project-Specific Prevention**

    Tailor prevention programs to the hazard profiles and safety rates of different project types.

    **Management Recommendation**

    Combine issue volume, severity, resolution progress,
    and Good Catch reporting when prioritizing safety
    management resources. These descriptive metrics do
    not establish causal relationships.
    """
)
