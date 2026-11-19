from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Layton Safety Analytics",
    page_icon="🏗️",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

st.title("Layton Construction | Safety Analytics")
st.subheader("Executive Overview")
st.caption("Synthetic dataset | January 2024 – September 2026")

st.markdown(
    """
    This dashboard integrates three complementary areas of
    construction safety analytics:

    **Workforce & Operational Risk**, **Hazards & Prevention**,
    and **Safety Performance & Compliance**.
    """
)

st.subheader("Project Introduction")

video_path = (
    BASE_DIR
    / "assets"
    / "videos"
    / "Layton_AI_Opening_With_Music.mp4"
)

st.video(str(video_path))

st.divider()

# Portfolio-level workforce metrics
project = pd.read_csv(DATA_DIR / "project_workforce_kpis.csv")

project_count = project["JOB_ID"].nunique()
total_hours = project["TOTAL_HOURS"].sum()
overtime_hours = project["OVERTIME_HOURS"].sum()
recordable = project["RECORDABLE_INCIDENTS"].sum()

overtime_rate = (
    overtime_hours / total_hours * 100
    if total_hours > 0 else 0
)

incident_rate = (
    recordable * 200000 / total_hours
    if total_hours > 0 else 0
)

st.subheader("Portfolio Safety Snapshot")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Projects", f"{project_count:,}")
col2.metric("Overtime Rate", f"{overtime_rate:.2f}%")
col3.metric("Recordable Incidents", f"{recordable:,.0f}")
col4.metric("Recordable Incident Rate", f"{incident_rate:.3f}")

st.caption(
    "Portfolio-level metrics based on the workforce analysis. "
    "Incident rate is calculated per 200,000 working hours."
)

st.divider()

st.subheader("Three Analytical Perspectives")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Workforce Risk")
    st.write(
        "Examines overtime exposure, workforce size, "
        "and their relationships with recordable incident rates."
    )
    st.write("**Focus:** Operational risk and workforce planning.")

with col2:
    st.markdown("### Hazards & Prevention")
    st.write(
        "Examines hazard patterns, unresolved safety issues, "
        "and preventive follow-up activities."
    )
    st.write("**Focus:** Hazard identification and prevention.")

with col3:
    st.markdown("### Safety Compliance")
    st.write(
        "Examines daily PTP submissions, weekly safety walks, "
        "and their relationships with incident rates."
    )
    st.write("**Focus:** Compliance monitoring and accountability.")

st.divider()

st.subheader("Preliminary Management Implications")

st.markdown(
    """
    - **Workforce:** Monitor overtime exposure and workforce
      conditions alongside safety outcomes.

    - **Prevention:** Prioritize unresolved hazards and strengthen
      follow-up on preventive actions.

    - **Compliance:** Track missing PTP submissions and weekly
      safety walks to identify potential process gaps.

    - **Integrated monitoring:** Use all three perspectives
      together rather than relying on incident rates alone.
    """
)

st.info(
    "The findings are descriptive and correlational. "
    "They should not be interpreted as evidence of causation. "
    "The 2026 data covers January through September only."
)

st.divider()
st.caption(
    "Layton Construction Safety Analytics | "
    "KPMG Data Analytics Challenge 2026"
)