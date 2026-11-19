"""Jenny's curated executive dashboard: project priorities, consequences, and type-based prevention.
Source: synthetic Layton competition CSVs; no PNG assets required.
"""
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Hazards & Prevention", page_icon="🛡️", layout="wide")
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "teammates" / "jenny"

NAVY = "#18334F"
BLUE = "#376F9E"
AMBER = "#CF8434"
MUTED = "#77869B"
GRID = "#E8EDF3"

st.markdown("""
<style>
.stApp { background-color: #F7F9FC; }
.block-container { max-width: 1280px; padding-top: 1.8rem; padding-bottom: 3rem; }
h1, h2, h3 { color: #18334F !important; letter-spacing: -.015em; }
[data-testid="stMetric"] {background:#FFF; border:1px solid #E3E9F0; border-radius:9px; padding:14px 16px;}
[data-testid="stMetricValue"] {color:#18334F;}
[data-testid="stMetricLabel"] {color:#576B80; font-weight:600;}
.executive-intro {background:#FFF; border-left:4px solid #376F9E; border-radius:6px;
  padding:15px 19px; color:#34495D; border-top:1px solid #E3E9F0;
  border-right:1px solid #E3E9F0; border-bottom:1px solid #E3E9F0;}
.action-strip {background:#EFF4FA; border-left:3px solid #CF8434; border-radius:5px;
  padding:12px 16px; color:#253B52; margin:8px 0 18px;}
.section-kicker {letter-spacing:.095em; font-size:.75rem; font-weight:750; color:#66798D; margin-top:10px;}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data(name):
    # Existing repository uses this location; nested folders are supported.
    matches = sorted(DATA_DIR.rglob(name))
    if not matches:
        st.error(f"Required data file not found: data/teammates/jenny/{name}")
        st.stop()
    return pd.read_csv(matches[0])


def chart_style(fig, height=420, legend=False, left=30, bottom=60):
    fig.update_layout(
        template="plotly_white", height=height, title=None,
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Arial", size=13, color="#31465D"),
        margin=dict(l=left, r=26, t=30, b=bottom),
        hoverlabel=dict(bgcolor="#FFFFFF", font_size=13),
        showlegend=legend,
        legend=dict(orientation="h", x=0, y=-0.18, xanchor="left", yanchor="top",
                    font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, showline=False, automargin=True)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, showline=False, automargin=True)
    return fig

project = load_data("member3_project_kpis.csv")
active = load_data("active_project_management_priority.csv")
incident = load_data("hazard_by_incident_classification.csv")
project_types = load_data("project_type_executive_summary.csv")
followup = load_data("good_catch_followup_by_severity.csv")

st.title("Hazards & Prevention")
st.caption("LAYTON SAFETY ANALYTICS  |  EXECUTIVE DECISION VIEW  |  SYNTHETIC DATA")
st.markdown('<div class="executive-intro"><strong>Management question:</strong> Which active projects need attention, which hazards can have serious consequences, and how should prevention differ by project type?</div>', unsafe_allow_html=True)
st.write("")

choices = sorted(project["JOB_ID"].astype(str).unique().tolist())
selected = st.multiselect("Filter projects for the overview and priority list", choices, default=choices)
filtered = project[project["JOB_ID"].astype(str).isin(selected)]
active_filtered = active[active["JOB_ID"].astype(str).isin(selected)].copy()
if filtered.empty:
    st.info("Select one or more projects to view the dashboard.")
    st.stop()

# Portfolio selection KPIs. The active-project count is separately labeled.
c1, c2, c3, c4 = st.columns(4)
c1.metric("Selected projects", f"{filtered['JOB_ID'].nunique():,}")
c2.metric("Active projects selected", f"{active_filtered['JOB_ID'].nunique():,}")
c3.metric("Unresolved safety issues", f"{filtered['UNRESOLVED_ISSUES'].sum():,.0f}")
c4.metric("High / Critical unresolved", f"{filtered['HIGH_CRITICAL_UNRESOLVED'].sum():,.0f}")
st.caption("KPI counts are based on selected projects. Open safety issues are separate from Good Catch follow-up labels.")

# Section 1 - the most actionable prioritization (full-width, no tab/expander).
st.divider()
st.markdown('<div class="section-kicker">01  /  RESOURCE PRIORITIZATION</div>', unsafe_allow_html=True)
st.subheader("Focus first on serious open issues at active sites")
st.write("Rank active projects by their **recorded unresolved High/Critical safety issues** — an attention queue, not a prediction of future incidents.")
if active_filtered.empty:
    st.info("No active projects are included in the current selection.")
else:
    ranked = active_filtered.nlargest(8, "HIGH_CRITICAL_UNRESOLVED").sort_values("HIGH_CRITICAL_UNRESOLVED")
    ranked["Other unresolved"] = (ranked["UNRESOLVED_ISSUES"] - ranked["HIGH_CRITICAL_UNRESOLVED"]).clip(lower=0)
    fig = go.Figure()
    fig.add_bar(
        y=ranked["JOB_NAME"], x=ranked["Other unresolved"], orientation="h",
        name="Other unresolved", marker_color=BLUE,
        hovertemplate="%{y}<br>Other unresolved issues: %{x}<extra></extra>",
    )
    fig.add_bar(
        y=ranked["JOB_NAME"], x=ranked["HIGH_CRITICAL_UNRESOLVED"], orientation="h",
        name="High/Critical unresolved", marker_color=AMBER,
        customdata=ranked[["JOB_ID", "UNRESOLVED_ISSUE_PCT", "SAFETY_INCIDENT_RATE"]].to_numpy(),
        hovertemplate="%{y} (%{customdata[0]})<br>High/Critical unresolved: %{x}<br>All-issue unresolved: %{customdata[1]:.1f}%<br>Historical incident rate: %{customdata[2]:.2f}<extra></extra>",
    )
    fig.update_layout(barmode="stack", xaxis_title="Recorded unresolved safety issues", yaxis_title="")
    st.plotly_chart(chart_style(fig, height=max(450, len(ranked)*50+165), legend=True, left=30, bottom=100), use_container_width=True, config={"displaylogo": False})
    st.markdown('<div class="action-strip"><strong>Action:</strong> Assign an owner to each serious unresolved item, verify its current site status and due date, and confirm corrective-action closure.</div>', unsafe_allow_html=True)
    st.caption("Top 8 active projects by recorded High/Critical unresolved count; bar segments show other vs serious unresolved issues. Project selection updates this chart. Large sites may have more reports, so do not treat counts as risk probabilities.")

# Section 2 - consequences rather than generic issue frequency.
st.divider()
st.markdown('<div class="section-kicker">02  /  INJURY CONSEQUENCES</div>', unsafe_allow_html=True)
st.subheader("Consider severity — not only frequency")
st.write("The incident categories show why prevention should consider **potential consequences**, including lost-time injuries, rather than only total reports.")
classifications = ["First Aid", "Lost Time Accident", "REC", "RECR"]
colors = {"First Aid": BLUE, "Lost Time Accident": AMBER, "REC": NAVY, "RECR": MUTED}
severity = incident.copy()
severity["Incident records"] = severity[classifications].sum(axis=1)
severity = severity.sort_values("Incident records", ascending=True)
fig = go.Figure()
for label in classifications:
    fig.add_bar(
        x=severity[label], y=severity["OSHA_HAZARD_CATEGORY"], orientation="h",
        name=label, marker_color=colors[label],
        hovertemplate="%{y}<br>" + label + ": %{x}<extra></extra>",
    )
fig.update_layout(barmode="stack", xaxis_title="Recorded injured workers", yaxis_title="")
st.plotly_chart(chart_style(fig, height=400, legend=True, bottom=100), use_container_width=True, config={"displaylogo": False})
st.markdown('<div class="action-strip"><strong>Action:</strong> Prioritize controls for consequential hazards such as falls, alongside high-volume hazards. Use pre-task planning, access protection, and targeted safety checks.</div>', unsafe_allow_html=True)
st.caption("All-project incident classification totals; unaffected by project filter. One row represents one injured worker, not necessarily a unique accident event. REC/RECR are retained as case codes; no unsupported category definitions are assumed.")

# Section 3 - focused comparison with no legend overlap.
st.divider()
st.markdown('<div class="section-kicker">03  /  CONTEXT-SPECIFIC PREVENTION</div>', unsafe_allow_html=True)
st.subheader("Adapt prevention to the type of construction project")
st.write("Compare **exposure-adjusted** qualifying injury rates and lost-time rates across project types; differences guide questions, not causal conclusions.")
typ = project_types.sort_values("SAFETY_INCIDENT_RATE", ascending=False)
fig = go.Figure()
fig.add_bar(
    x=typ["PROJECT_TYPE"], y=typ["SAFETY_INCIDENT_RATE"],
    name="Qualifying incident rate", marker_color=BLUE,
    customdata=typ[["PROJECT_COUNT", "TOP_SEVERE_HAZARD"]].to_numpy(),
    hovertemplate="%{x}<br>Incident rate: %{y:.2f}<br>Projects: %{customdata[0]}<br>Key severe hazard: %{customdata[1]}<extra></extra>",
)
fig.add_bar(
    x=typ["PROJECT_TYPE"], y=typ["LTA_RATE"],
    name="Lost-time injury rate", marker_color=AMBER,
    hovertemplate="%{x}<br>Lost-time rate: %{y:.2f}<extra></extra>",
)
fig.update_layout(barmode="group", xaxis_title="", yaxis_title="Cases per 200,000 person-hours")
fig.update_xaxes(tickangle=-20)
st.plotly_chart(chart_style(fig, height=430, legend=True, bottom=130), use_container_width=True, config={"displaylogo": False})
st.markdown('<div class="action-strip"><strong>Action:</strong> Tailor inspections, pre-task coordination and worker training to each project type; verify the leading hazards and site conditions before allocating resources.</div>', unsafe_allow_html=True)
st.caption("Portfolio-wide by project type, unaffected by the project filter. Small groups of roughly 5–6 projects; descriptive comparisons only. LTA is a subset of qualifying incidents and is not additive to the total rate.")

st.divider()
st.subheader("Executive Recommendations")
a, b, c = st.columns(3)
with a:
    with st.container(border=True):
        st.markdown("**1. Clear serious issues**")
        st.write("Prioritize verified High/Critical issues at active projects and assign accountable owners.")
with b:
    with st.container(border=True):
        st.markdown("**2. Prevent severe outcomes**")
        st.write("Focus on consequential hazards, not just the categories reported most frequently.")
with c:
    with st.container(border=True):
        st.markdown("**3. Verify follow-through**")
        st.write("Confirm completed actions, align safety controls with project context, and audit reporting quality.")

recorded_completed = int(followup["COMPLETED_FOLLOWUPS"].sum())
recorded_open = int(followup["OPEN_FOLLOWUPS"].sum())
st.info(
    f"**Good Catch reporting note:** {recorded_completed:,} follow-ups are labeled Completed and {recorded_open:,} labeled Open in the source data. "
    "Per instructor clarification, unconfirmed follow-up work may be assumed completed for this exercise. "
    "These labels must not be interpreted as verified outstanding hazards. Good Catches are not directly linked to issues or incidents."
)
st.caption("All findings use synthetic case data, not live Layton operational data. Descriptive associations do not establish causation. No original PNG charts are required for this page.")
