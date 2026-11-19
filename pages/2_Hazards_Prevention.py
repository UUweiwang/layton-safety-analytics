from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Hazards & Prevention", layout="wide")
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "teammates" / "jenny"

NAVY = "#17324D"
BLUE = "#38B6DE"
ORANGE = "#F59A54"
GREEN = "#16A34A"
GRID = "#E2E8F0"

st.markdown("""<style>
.stApp {background-color: #F8FAFC;}
h1, h2, h3 {color: #17324D !important;}
div[data-testid="stMetric"] {background-color: white; padding: 12px;
 border: 1px solid #DCE5EF; border-radius: 10px;}
</style>""", unsafe_allow_html=True)


def load_csv(filename):
    paths = sorted(DATA_DIR.rglob(filename))
    if not paths:
        st.error(f"Missing CSV: data/teammates/jenny/{filename}")
        st.stop()
    return pd.read_csv(paths[0])


def style(fig, height=420):
    fig.update_layout(
        template="plotly_white", height=height, paper_bgcolor="white",
        plot_bgcolor="white", font=dict(family="Arial", size=13, color=NAVY),
        legend=dict(orientation="h", y=1.12, x=0),
        margin=dict(l=15, r=15, t=55, b=30),
        hoverlabel=dict(bgcolor="white"),
    )
    fig.update_xaxes(gridcolor=GRID)
    fig.update_yaxes(gridcolor=GRID)
    return fig


project = load_csv("member3_project_kpis.csv")
active = load_csv("active_project_management_priority.csv")
project_types = load_csv("project_type_executive_summary.csv")
hazards = load_csv("issue_hazard_summary.csv")
incident_hazards = load_csv("hazard_by_incident_classification.csv")
followup = load_csv("good_catch_followup_by_severity.csv")

st.title("Hazards & Prevention")
st.caption("Layton Construction Safety Analytics | Synthetic dataset | Jenny's key analyses, recreated as interactive charts")

selected = st.multiselect(
    "Select Projects (updates project-level KPIs and active-project priorities)",
    options=sorted(project["JOB_ID"].astype(str).unique()),
    default=sorted(project["JOB_ID"].astype(str).unique()),
)
filtered = project[project["JOB_ID"].isin(selected)]
if filtered.empty:
    st.warning("Select at least one project.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Safety Issues", f"{filtered['TOTAL_ISSUES'].sum():,.0f}")
c2.metric("Unresolved Issues", f"{filtered['UNRESOLVED_ISSUES'].sum():,.0f}")
c3.metric("Unresolved High/Critical", f"{filtered['HIGH_CRITICAL_UNRESOLVED'].sum():,.0f}")
hours = filtered["TOTAL_HOURS"].sum()
rate = (filtered["GOOD_CATCHES"].sum() * 200000 / hours) if hours else 0
c4.metric("Good Catches / 200k Hours", f"{rate:.1f}")
st.caption("KPI totals reflect the selected projects. High/Critical counts are recorded unresolved safety issues, not Good Catch follow-up labels.")

st.divider()
st.subheader("Jenny's Three Priority Analyses")
st.caption("Blue and orange echo Jenny's original charts, while the interactive visuals use the same white background as the team dashboard.")
t1, t2, t3 = st.tabs(["1. Serious hazards", "2. Frequency vs consequence", "3. Project types"])

with t1:
    st.markdown("**Prioritize high-severity hazards after detection**")
    av = active[active["JOB_ID"].isin(selected)].copy()
    if av.empty:
        st.info("No active projects in this selection.")
    else:
        av = av.nlargest(10, "HIGH_CRITICAL_UNRESOLVED").copy()
        av["Other unresolved (Low/Medium)"] = (
            av["UNRESOLVED_ISSUES"] - av["HIGH_CRITICAL_UNRESOLVED"]
        ).clip(lower=0)
        av = av.sort_values("HIGH_CRITICAL_UNRESOLVED")
        f = go.Figure()
        f.add_bar(y=av["JOB_NAME"], x=av["Other unresolved (Low/Medium)"],
                  orientation="h", name="Other unresolved", marker_color=BLUE,
                  customdata=av[["UNRESOLVED_ISSUE_PCT", "MEDIAN_RESOLUTION_DAYS"]].to_numpy(),
                  hovertemplate="%{y}<br>Other unresolved: %{x}<br>All-issue open rate: %{customdata[0]:.1f}%<br>Median resolution: %{customdata[1]:.0f} days<extra></extra>")
        f.add_bar(y=av["JOB_NAME"], x=av["HIGH_CRITICAL_UNRESOLVED"],
                  orientation="h", name="High/Critical unresolved", marker_color=ORANGE,
                  hovertemplate="%{y}<br>High/Critical unresolved: %{x}<extra></extra>")
        f.update_layout(barmode="stack", xaxis_title="Unresolved issues", yaxis_title="",
                        title="Active Projects | Top 10 by Unresolved High/Critical Issues")
        st.plotly_chart(style(f, max(430, len(av)*39 + 135)), use_container_width=True)
        st.caption("Active projects only; top ten ranked by unresolved High/Critical issue count. Hover for unresolved percentage and typical resolution time. Severity grouping assumes the high/critical subset is included within all unresolved issues.")
    st.info("**Management action:** Assign owners to unresolved High/Critical issues; track issue age and closure verification. Do not prioritize projects by raw issue count alone.")

with t2:
    st.markdown("**Consider severity as well as how often hazards are reported**")
    left, right = st.columns(2)
    with left:
        h = hazards.sort_values("ISSUE_COUNT", ascending=True)
        f = px.bar(h, x="ISSUE_COUNT", y="HAZARD_CATEGORY", orientation="h",
                   color_discrete_sequence=[BLUE],
                   labels={"ISSUE_COUNT": "Safety issue records", "HAZARD_CATEGORY": ""},
                   title="Reported Issue Categories | Frequency")
        st.plotly_chart(style(f, 455), use_container_width=True)
    with right:
        ih = incident_hazards.copy()
        severity_cols = [c for c in ["First Aid", "Lost Time Accident", "REC", "RECR"] if c in ih.columns]
        long = ih.melt(id_vars="OSHA_HAZARD_CATEGORY", value_vars=severity_cols,
                       var_name="Classification", value_name="Count")
        f = px.bar(long, x="Count", y="OSHA_HAZARD_CATEGORY", orientation="h",
                   color="Classification", barmode="stack",
                   color_discrete_map={"First Aid": BLUE, "Lost Time Accident": ORANGE,
                                       "REC": NAVY, "RECR": "#7C8BA1"},
                   labels={"OSHA_HAZARD_CATEGORY": "", "Count": "Incident records"},
                   title="Incident Hazards | Injury Classifications")
        st.plotly_chart(style(f, 455), use_container_width=True)
    st.caption("Portfolio-wide, unaffected by project selection. Issue HAZARD_CATEGORY and incident OSHA_HAZARD_CATEGORY are different classification systems; the two charts are comparisons, not linked records. LTA is shown separately; REC/RECR meanings should follow the case guide.")
    st.info("**Management action:** Prioritize fall-prevention controls for serious outcomes, while maintaining targeted checks for frequently reported issue categories. Frequency alone is not a severity score.")

with t3:
    st.markdown("**Tailor prevention to project type, without claiming causation**")
    typ = project_types.sort_values("SAFETY_INCIDENT_RATE", ascending=False)
    f = go.Figure()
    f.add_bar(x=typ["PROJECT_TYPE"], y=typ["SAFETY_INCIDENT_RATE"], name="Safety incident rate", marker_color=BLUE,
              customdata=typ[["PROJECT_COUNT", "TOP_SEVERE_HAZARD"]].to_numpy(),
              hovertemplate="%{x}<br>Incident rate: %{y:.2f}<br>Projects: %{customdata[0]}<br>Severe hazard: %{customdata[1]}<extra></extra>")
    f.add_bar(x=typ["PROJECT_TYPE"], y=typ["LTA_RATE"], name="Lost Time Accident rate", marker_color=ORANGE,
              hovertemplate="%{x}<br>LTA rate: %{y:.2f}<extra></extra>")
    f.update_layout(barmode="group", title="Safety and LTA Rates by Project Type",
                    xaxis_title="", yaxis_title="Incidents per 200,000 person-hours")
    st.plotly_chart(style(f, 450), use_container_width=True)
    st.caption("Portfolio-wide (not filtered). Each type includes about 5–6 projects; results are exploratory and exposure-adjusted, not proof that any project type is inherently riskier.")
    st.info("**Management action:** Tailor pre-task planning, safety walks, access equipment, and training to each project's dominant hazards.")

st.divider()
st.subheader("Good Catch Reporting | Recorded Follow-up Status")
with st.expander("Explore Good Catch follow-ups by severity (source labels)", expanded=False):
    long = followup.melt(id_vars="POTENTIAL_SEVERITY",
                        value_vars=["COMPLETED_FOLLOWUPS", "OPEN_FOLLOWUPS"],
                        var_name="Status", value_name="Count")
    long["Status"] = long["Status"].map({"COMPLETED_FOLLOWUPS": "Recorded Completed", "OPEN_FOLLOWUPS": "Recorded Open"})
    f = px.bar(long, x="POTENTIAL_SEVERITY", y="Count", color="Status", barmode="stack",
               color_discrete_map={"Recorded Completed": GREEN, "Recorded Open": ORANGE},
               title="Good Catch Follow-up Labels by Potential Severity")
    st.plotly_chart(style(f, 370), use_container_width=True)
    st.caption("Portfolio-wide; does not change with project selection. Instructor guidance recommends assuming follow-ups without confirmed completion are completed for this exercise. 'Recorded Open' does not establish that hazards are still unresolved. Validate actual completion before operational use.")

st.subheader("Four Key Findings & Recommended Actions")
st.markdown("""
**1. Resolve serious hazards with accountability.** In Jenny's active-project analysis, 992 issues were identified; 481 were recorded unresolved and 352 were High/Critical. Verify owners, issue age, corrective actions, and closure.

**2. Look beyond frequency.** Fall-related incidents can carry severe consequences. Prioritize work-at-height controls and safer access methods, not only commonly reported issues.

**3. Adapt prevention by project type.** Issue detection rates were relatively similar (36.7–41.3 per 200,000 person-hours), while incident and LTA rates varied. Use project-specific planning; small project-type samples limit generalization.

**4. Encourage Good Catches as a reporting indicator.** The synthetic portfolio contains 1,000 Good Catches; among 805 labeled as requiring follow-up, 395 were recorded Completed and 410 Open. Source status labels are not verified unresolved hazards; document completion consistently and reinforce reporting.
""")
st.caption("Descriptive analysis of synthetic data. Results do not show causation, real-time conditions, or validated predictive risk.")
with st.expander("Industry references"):
    st.markdown("""
- [OSHA — Hazard Identification](https://www.osha.gov/safety-management/hazard-identification)
- [OSHA — Worker Participation](https://www.osha.gov/safety-management/worker-participation)
- [CPWR — Safety Climate Assessment Tool](https://www.cpwr.com/research/management-resources-from-research/safety-culture-and-safety-climate/safety-climate-assessment-tool-s-cat/)
""")
