from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Hazards & Prevention", layout="wide")
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "teammates" / "jenny"

NAVY = "#142D4E"       # Enterprise navy
BLUE = "#2864A0"       # Corporate blue
ORANGE = "#D58A32"     # Caution / High-Critical (not decorative)
GREEN = "#287B62"      # Completed status
GRID = "#E5EAF1"

st.markdown("""
<style>
/* Clean executive design: a muted page, white panels and restrained status colors. */
.stApp {background: #F5F7FA; color: #24364D;}
.block-container {max-width: 1320px; padding-top: 1.8rem; padding-bottom: 2.5rem;}
h1, h2, h3 {color: #142D4E !important; letter-spacing: -0.018em;}
h1 {font-weight: 750 !important;}
[data-testid="stMetric"] {
  background: #FFFFFF; border: 1px solid #E1E7EF;
  border-radius: 10px; padding: 18px 18px 14px;
  box-shadow: 0 2px 10px rgba(20,45,78,0.035);
}
[data-testid="stMetricLabel"] {color:#576A82; font-weight:600;}
[data-testid="stMetricValue"] {color:#142D4E;}
[data-testid="stTabs"] button {font-weight:650;}
[data-testid="stAlert"] {border-radius: 9px;}
/* Executive insight panel */
.exec-panel {
  padding: 16px 18px; background: #FFFFFF; border: 1px solid #E1E7EF;
  border-left: 4px solid #2864A0; border-radius: 8px;
  margin: 8px 0 14px;
}
.exec-panel strong {color:#142D4E;}
.action-label {font-size: .75rem; font-weight: 750; letter-spacing:.06em; color:#607389;}
.exec-card {background:#FFFFFF; border:1px solid #E1E7EF; border-radius:9px;
  padding: 16px 18px; min-height: 140px; height:100%;}
.exec-card .card-id {font-size:.72rem; letter-spacing:.07em; color:#63758B; font-weight:700;}
.exec-card .card-title {font-size:1rem; color:#142D4E; font-weight:750; margin:6px 0 8px;}
.exec-card .card-desc {font-size:.88rem; color:#40536A; line-height:1.55;}
</style>
""", unsafe_allow_html=True)


def load_csv(filename):
    paths = sorted(DATA_DIR.rglob(filename))
    if not paths:
        st.error(f"Missing CSV: data/teammates/jenny/{filename}")
        st.stop()
    return pd.read_csv(paths[0])


def style(fig, height=420):
    fig.update_layout(
        template="plotly_white", height=height, paper_bgcolor="white",
        plot_bgcolor="white", font=dict(family="Arial", size=13, color="#24364D"),
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
st.caption("LAYTON SAFETY ANALYTICS  /  MANAGEMENT DASHBOARD  /  SYNTHETIC DATA")
st.markdown("""<div class="exec-panel"><strong>Executive question:</strong> Where should safety leaders focus corrective-action resources, and which prevention measures should be prioritized?</div>""", unsafe_allow_html=True)

selected = st.multiselect(
    "Project selection — updates KPI cards and active-project priorities",
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
c3.metric("High / Critical Open Issues", f"{filtered['HIGH_CRITICAL_UNRESOLVED'].sum():,.0f}")
hours = filtered["TOTAL_HOURS"].sum()
rate = (filtered["GOOD_CATCHES"].sum() * 200000 / hours) if hours else 0
c4.metric("Good Catches / 200k Hours", f"{rate:.1f}")
st.caption("KPI totals reflect the selected projects. High/Critical counts are recorded unresolved safety issues, not Good Catch follow-up labels.")

st.divider()
st.subheader("Safety Priorities")
st.caption("Three complementary analyses. The selected-project filter affects only project-level metrics and active-project ranking.")
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
    st.markdown("""<div class="exec-panel"><span class="action-label">RECOMMENDED ACTION</span><div><strong>Assign accountable owners</strong> to High/Critical items; review issue age and verify closure. Raw counts indicate attention needs, not predicted incident risk.</div></div>""", unsafe_allow_html=True)

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
    st.markdown("""<div class="exec-panel"><span class="action-label">RECOMMENDED ACTION</span><div><strong>Target consequential hazards</strong> such as falls while continuing frequent-category inspections. Frequency alone does not measure severity.</div></div>""", unsafe_allow_html=True)

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
    st.markdown("""<div class="exec-panel"><span class="action-label">RECOMMENDED ACTION</span><div><strong>Adapt safety controls</strong> by project context: pre-task planning, Focus Walks, access equipment and targeted training.</div></div>""", unsafe_allow_html=True)

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

st.divider()
st.subheader("Executive Findings & Actions")
st.caption("Four decisions supported by Jenny's descriptive analysis; supporting detail is in the interactive charts above.")
findings = [
    ("01", "Close serious hazards", "Prioritize High/Critical issues, verify corrective actions, and document ownership."),
    ("02", "Look beyond volume", "Falls may have severe consequences even when their issue frequency is not highest."),
    ("03", "Match controls to sites", "Different project types warrant tailored planning, access controls and training."),
    ("04", "Verify Good Catch follow-up", "Treat status labels as reporting information; confirm actual completion before escalating."),
]
cols = st.columns(2)
for idx, (num, heading, detail) in enumerate(findings):
    with cols[idx % 2]:
        st.markdown(
            f'<div class="exec-card"><div class="card-id">PRIORITY {num}</div>'
            f'<div class="card-title">{heading}</div>'
            f'<div class="card-desc">{detail}</div></div>',
            unsafe_allow_html=True,
        )
        st.write("")
with st.expander("Supporting evidence and caveats", expanded=False):
    st.markdown("""
    - **Open issues:** Jenny's active-project analysis identified 992 safety issues, 481 recorded as unresolved, including 352 High/Critical. These values apply to the specific active-project analytical subset, not necessarily the current project filter.
    - **Project-type comparison:** Reported issue detection rates were comparatively similar (36.7–41.3 per 200,000 person-hours), while incident/LTA rates varied; approximately five to six projects per type limit generalization.
    - **Good Catch records:** Across the synthetic portfolio there were 1,000 Good Catches; among 805 records flagged for follow-up, 395 were labeled Completed and 410 Open. Recorded status is not the same as verified outstanding work. Follow instructor guidance on unconfirmed completion.
    - **Interpretation:** These patterns are descriptive, not causal, real-time or predictive.
    """)
st.caption("Descriptive analysis of synthetic data. Results do not show causation, real-time conditions, or validated predictive risk.")
with st.expander("Industry references"):
    st.markdown("""
- [OSHA — Hazard Identification](https://www.osha.gov/safety-management/hazard-identification)
- [OSHA — Worker Participation](https://www.osha.gov/safety-management/worker-participation)
- [CPWR — Safety Climate Assessment Tool](https://www.cpwr.com/research/management-resources-from-research/safety-culture-and-safety-climate/safety-climate-assessment-tool-s-cat/)
""")
