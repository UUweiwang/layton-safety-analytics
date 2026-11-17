from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# 1. Page configuration and consistent chart style
# --------------------------------------------------

st.set_page_config(
    page_title="Safety Performance & Compliance",
    layout="wide"
)


def style_chart(fig, height=430):
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
        margin={"l": 35, "r": 35, "t": 65, "b": 45}
    )
    return fig


st.markdown(
    """
    <style>
    .stApp {
        background-color: #F8FAFC;
    }
    h1, h2, h3 {
        color: #17324D;
    }
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 2. Load Rishi's validated Excel file
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "teammates" / "rishi"

excel_files = sorted(
    DATA_DIR.rglob("Layton_Safety_Analysis_Validated*.xlsx")
)

if not excel_files:
    st.error(
        "Cannot find Rishi's validated Excel file. "
        "Please check data/teammates/rishi."
    )
    st.stop()

project = pd.read_excel(
    excel_files[0],
    sheet_name="Project KPIs"
)

project.columns = project.columns.str.strip()

numeric_columns = [
    "Total Hours",
    "Qualifying Incidents",
    "LTA Incidents",
    "Incident Rate",
    "LTA Rate",
    "Worked Days",
    "PTP Submitted",
    "Daily PTP %",
    "Worked Weeks",
    "Walks Submitted",
    "Weekly Walk %"
]

for column in numeric_columns:
    project[column] = pd.to_numeric(
        project[column],
        errors="coerce"
    ).fillna(0)


# --------------------------------------------------
# 3. Header and project filter
# --------------------------------------------------

st.title("Safety Performance & Compliance")

st.caption(
    "Layton Construction Safety Analytics | "
    "Synthetic Data | January 2024 – September 2026"
)

all_projects = sorted(project["JOB_ID"].dropna().unique())

selected_projects = st.multiselect(
    "Select Projects",
    options=all_projects,
    default=all_projects
)

filtered = project[
    project["JOB_ID"].isin(selected_projects)
].copy()

if filtered.empty:
    st.warning("Please select at least one project.")
    st.stop()


# --------------------------------------------------
# 4. Calculate weighted portfolio KPIs
# --------------------------------------------------

total_days = filtered["Worked Days"].sum()
ptp_submitted = filtered["PTP Submitted"].sum()

total_weeks = filtered["Worked Weeks"].sum()
walks_submitted = filtered["Walks Submitted"].sum()

missing_ptp = max(total_days - ptp_submitted, 0)
missing_walks = max(total_weeks - walks_submitted, 0)

ptp_rate = (
    ptp_submitted / total_days * 100
    if total_days > 0 else 0
)

walk_rate = (
    walks_submitted / total_weeks * 100
    if total_weeks > 0 else 0
)


# --------------------------------------------------
# 5. KPI cards
# --------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Daily PTP Compliance",
    f"{ptp_rate:.2f}%"
)

c2.metric(
    "Weekly Focus Walk Compliance",
    f"{walk_rate:.2f}%"
)

c3.metric(
    "Missing Daily PTPs",
    f"{missing_ptp:,.0f}"
)

c4.metric(
    "Missing Weekly Walks",
    f"{missing_walks:,.0f}"
)

st.caption(
    "Compliance rates are weighted by worked days "
    "and worked weeks. Missing submissions do not "
    "necessarily mean safety activities did not occur."
)


# --------------------------------------------------
# 6. Compliance vs incident rate
# --------------------------------------------------

st.subheader("Compliance and Safety Performance")

left, right = st.columns(2)

with left:
    fig1 = px.scatter(
        filtered,
        x="Daily PTP %",
        y="Incident Rate",
        hover_name="JOB_ID",
        hover_data={
            "Total Hours": ":,.0f",
            "Qualifying Incidents": True
        },
        title="Daily PTP Compliance vs Incident Rate",
        labels={
            "Daily PTP %": "Daily PTP Compliance",
            "Incident Rate": "Recordable Incident Rate"
        },
        color_discrete_sequence=["#467EAC"]
    )

    fig1.update_xaxes(
        tickformat=".0%",
        range=[0, 1]
    )

    style_chart(fig1, height=430)
    st.plotly_chart(fig1, use_container_width=True)

    correlation_ptp = filtered[
        ["Daily PTP %", "Incident Rate"]
    ].corr().iloc[0, 1]

    if pd.notna(correlation_ptp):
        st.metric(
            "Pearson Correlation (PTP)",
            f"{correlation_ptp:+.3f}"
        )
    else:
        st.caption(
            "Correlation unavailable for this selection."
        )


with right:
    fig2 = px.scatter(
        filtered,
        x="Weekly Walk %",
        y="Incident Rate",
        hover_name="JOB_ID",
        hover_data={
            "Total Hours": ":,.0f",
            "Qualifying Incidents": True
        },
        title="Weekly Walk Compliance vs Incident Rate",
        labels={
            "Weekly Walk %": "Weekly Walk Compliance",
            "Incident Rate": "Recordable Incident Rate"
        },
        color_discrete_sequence=["#467EAC"]
    )

    fig2.update_xaxes(
        tickformat=".0%",
        range=[0, 1]
    )

    style_chart(fig2, height=430)
    st.plotly_chart(fig2, use_container_width=True)

    correlation_walk = filtered[
        ["Weekly Walk %", "Incident Rate"]
    ].corr().iloc[0, 1]

    if pd.notna(correlation_walk):
        st.metric(
            "Pearson Correlation (Weekly Walk)",
            f"{correlation_walk:+.3f}"
        )
    else:
        st.caption(
            "Correlation unavailable for this selection."
        )

st.caption(
    "Incident Rate = Qualifying Incidents × 200,000 "
    "/ Total Hours. Correlations describe associations "
    "and do not establish causation."
)


# --------------------------------------------------
# 7. Missing submissions by project
# --------------------------------------------------

st.subheader("Compliance Gaps by Project")

filtered["Missing PTP"] = (
    filtered["Worked Days"]
    - filtered["PTP Submitted"]
).clip(lower=0)

filtered["Missing Walks"] = (
    filtered["Worked Weeks"]
    - filtered["Walks Submitted"]
).clip(lower=0)

left2, right2 = st.columns(2)

with left2:
    top_ptp = filtered.nlargest(
        10, "Missing PTP"
    ).sort_values("Missing PTP")

    fig3 = px.bar(
        top_ptp,
        x="Missing PTP",
        y="JOB_ID",
        orientation="h",
        title="Top 10 Projects: Missing Daily PTPs",
        labels={
            "Missing PTP": "Missing Submissions",
            "JOB_ID": "Project"
        },
        color_discrete_sequence=["#467EAC"]
    )

    style_chart(fig3, height=450)
    st.plotly_chart(fig3, use_container_width=True)


with right2:
    top_walks = filtered.nlargest(
        10, "Missing Walks"
    ).sort_values("Missing Walks")

    fig4 = px.bar(
        top_walks,
        x="Missing Walks",
        y="JOB_ID",
        orientation="h",
        title="Top 10 Projects: Missing Weekly Walks",
        labels={
            "Missing Walks": "Missing Submissions",
            "JOB_ID": "Project"
        },
        color_discrete_sequence=["#6699C3"]
    )

    style_chart(fig4, height=450)
    st.plotly_chart(fig4, use_container_width=True)


# --------------------------------------------------
# 8. Management findings and recommendations
# --------------------------------------------------

st.subheader("Key Findings & Recommendations")

st.markdown(
    """
    **1. Daily Safety Planning Compliance**

    Daily PTP submission compliance is an important
    indicator of safety documentation consistency.
    Projects with repeated missing submissions should
    receive targeted follow-up.

    **2. Weekly Safety Walk Compliance**

    Weekly Focus Walk submissions provide visibility
    into routine safety oversight. Missing records
    should be reviewed to distinguish documentation
    gaps from activities that were not performed.

    **3. Compliance and Incident Rates**

    Compare project-level compliance rates with
    recordable incident rates to identify projects
    requiring further investigation. Correlation
    alone does not demonstrate that compliance
    causes changes in incident rates.

    **Management Recommendation**

    Prioritize projects with persistent documentation
    gaps and elevated incident rates. Review reporting
    practices, project conditions, and operational
    exposure before deciding on corrective actions.
    """
)
