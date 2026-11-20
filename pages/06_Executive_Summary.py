"""Layton Safety Analytics — final Streamlit page.

Upload this file to your repository's `pages/` folder.
The video should already be uploaded at:
assets/videos/Layton_Blackboard_Executive_Recommendations_1080p.mp4
"""
from pathlib import Path
import streamlit as st

VIDEO_FILENAME = "Layton_Blackboard_Executive_Recommendations_1080p.mp4"

st.set_page_config(page_title="Executive Summary | Layton Safety Analytics", page_icon="🎓", layout="wide")

# Path is relative to this file, not to the current working directory.
REPO_ROOT = Path(__file__).resolve().parent.parent
VIDEO_PATH = REPO_ROOT / "assets" / "videos" / VIDEO_FILENAME

st.markdown("### KPMG Layton Safety Analysis")
st.title("Executive Summary & Strategic Recommendations")
st.caption("University of Utah | Student Analysis Project | Synthetic Competition Data")
st.write(
    "A narrated overview of our verified safety findings, financial considerations, "
    "and recommended next steps for a targeted pilot."
)

if VIDEO_PATH.is_file():
    st.video(str(VIDEO_PATH), format="video/mp4")
else:
    st.warning("The video file was not found in the expected GitHub folder.")
    st.code(f"assets/videos/{VIDEO_FILENAME}", language="text")
    st.info("Check that the GitHub video filename matches exactly, including capitalization.")

st.markdown("### Our Recommendation")
st.markdown(
    "**Start small, measure results, and scale based on verified performance.** "
    "Move from reactive safety reporting toward proactive, data-driven safety management."
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Portfolio incident rate", "0.923", help="Qualifying incidents per 200,000 hours across 40 synthetic projects")
with col2:
    st.metric("Daily PTP completion", "87.25%")
with col3:
    st.metric("Weekly Walk completion", "83.15%")

st.markdown("#### 90-day targeted pilot")
st.write(
    "Pilot four active projects. Aim for 95% PTP and Weekly Walk completion; "
    "verify and prioritize high-severity unresolved hazards; assign corrective-action owners; "
    "and monitor follow-through in a centralized dashboard."
)
st.markdown("#### Financial perspective")
st.write(
    "**Illustrative pilot budget: $29,210.** The short-term injury-cost scenarios do not "
    "show immediate break-even. Evaluate operational results, actual costs, and longer-term "
    "safety outcomes before deciding whether to expand."
)

st.divider()
st.caption(
    "All figures are from a synthetic student competition case. Pilot targets, budget, "
    "and cost scenarios are illustrative, not Layton operational forecasts. "
    "Correlations in the analysis do not establish causation."
)
