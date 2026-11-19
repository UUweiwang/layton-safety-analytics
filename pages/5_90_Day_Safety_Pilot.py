"""Layton Safety Analytics | 90-Day Pilot Plan.
Standalone Streamlit page; all numbers are illustrative and sourced from the
team's synthetic-data analysis and Rishi's finalized pilot proposal.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="90-Day Safety Pilot | Layton", page_icon="🦺", layout="wide")

NAVY = "#17324D"
BLUE = "#2B6597"
AMBER = "#C68A38"
BG = "#F5F7FA"
GREY = "#627489"
BORDER = "#DDE5EC"
RED = "#A74642"

st.markdown(f"""
<style>
.stApp {{background: {BG};}}
h1,h2,h3 {{color: {NAVY} !important;}}
.block-container {{max-width: 1320px; padding-top: 2rem; padding-bottom: 3rem;}}
div[data-testid='stMetric'] {{background:#FFFFFF; padding:17px; border:1px solid {BORDER}; border-radius:12px;}}
div[data-testid='stMetricLabel'] {{color:{GREY};}}
.pilot-card {{background:white; border:1px solid {BORDER}; border-radius:12px; padding:20px 22px; height:100%;}}
.pilot-card h4 {{color:{NAVY}; margin:0 0 12px 0; font-size:1.08rem;}}
.pilot-card p {{color:#334155; margin:0; line-height:1.65;}}
.section-note {{color:{GREY}; font-size:.93rem; margin-bottom:13px;}}
.eyebrow {{color:{BLUE}; font-size:.81rem; letter-spacing:.12em; font-weight:700; text-transform:uppercase;}}
.pilot-callout {{background:#EAF1F8; border-left:4px solid {BLUE}; padding:17px 21px; border-radius:8px; color:{NAVY};}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="eyebrow">Management decision | Proposed pilot</div>', unsafe_allow_html=True)
st.title("90-Day Safety Improvement Pilot")
st.markdown("**From descriptive safety insights to a measurable, bounded action plan.**")
st.caption("Four active projects | Synthetic case data | Rishi's illustrative planning assumptions — not Layton's actual operating costs")

k1,k2,k3,k4=st.columns(4)
k1.metric("Pilot Projects", "4")
k2.metric("Pilot Duration", "90 days")
k3.metric("Proposed Budget", "$29,210")
k4.metric("Pilot Cost Break-even", "~92.9%", help="Illustrative reduction in expected injury costs required to cover the 90-day budget; not an operational target.")

st.divider()
st.subheader("01 | Why These Four Projects?")
st.markdown('<div class="section-note">A balanced shortlist combining observed incident rates, preventive-process completion and verified serious-issue records. This is not a validated predictive risk score.</div>', unsafe_allow_html=True)

pilot = pd.DataFrame([
    {"Project":"JOB-024", "Incident rate":1.613, "Daily PTP":83.47, "Weekly Walk":72.73, "High/Critical open":22, "Reason":"Elevated rate + weak checklist completion"},
    {"Project":"JOB-001", "Incident rate":2.257, "Daily PTP":87.64, "Weekly Walk":83.33, "High/Critical open":38, "Reason":"High historical incident rate"},
    {"Project":"JOB-002", "Incident rate":1.118, "Daily PTP":89.94, "Weekly Walk":81.25, "High/Critical open":42, "Reason":"Large serious-issue backlog"},
    {"Project":"JOB-017", "Incident rate":0.000, "Daily PTP":82.08, "Weekly Walk":80.77, "High/Critical open":28, "Reason":"Zero incidents but weaker leading indicators"},
])
st.dataframe(pilot, hide_index=True, use_container_width=True, column_config={
    "Incident rate":st.column_config.NumberColumn("Incident rate / 200k h", format="%.3f"),
    "Daily PTP":st.column_config.NumberColumn("Daily PTP (%%)", format="%.2f"),
    "Weekly Walk":st.column_config.NumberColumn("Weekly Walk (%%)", format="%.2f"),
    "High/Critical open":st.column_config.NumberColumn("High/Critical open",format="%d"),
})
st.caption("High/Critical unresolved values use Rishi's adjusted analytical treatment excluding open-status records at completed projects. Verify current site status, severity and owners before action.")

st.divider()
st.subheader("02 | Implementation Roadmap")
phases=[
    ("Days 1–30", "Assess & Prepare", "Confirm site conditions and project stage; establish fresh PTP / walk baselines; train supervisors; verify severe hazards; assign corrective-action owners.", "Evidence: baseline completion, hazard aging, named owners and labor time"),
    ("Days 31–60", "Implement & Monitor", "Prompt missing daily PTPs; schedule weekly Focus Walks; escalate serious hazards weekly; document completed corrective actions.", "Evidence: weekly compliance, verified closure and actual staffing time"),
    ("Days 61–90", "Evaluate & Decide", "Compare with pilot-start baselines and matched non-pilot sites when possible; assess realized process gains, incident exposure and actual costs; decide whether to refine or scale.", "Evidence: process indicators, hours, incidents and pilot spending"),
]
columns=st.columns(3, gap="medium")
for col,(period,title,desc,evidence) in zip(columns,phases):
    with col:
        st.markdown(f'<div class="pilot-card"><div class="eyebrow">{period}</div><h4>{title}</h4><p>{desc}</p><p style="margin-top:14px;color:{GREY};font-size:.88rem">{evidence}</p></div>',unsafe_allow_html=True)

st.divider()
st.subheader("03 | Proposed Success Measures")
g1,g2,g3=st.columns(3)
g1.metric("Daily PTP target", "95%", "Pilot proposal")
g2.metric("Weekly Focus Walk target", "95%", "Pilot proposal")
g3.metric("Serious open issues", "−25%", "From verified pilot-start baseline")
st.markdown('<div class="pilot-callout"><b>Measure what is verifiable.</b> Confirm Good Catch completion evidence rather than interpreting original <i>Open</i> labels as proven outstanding hazards. Monitor exposure-adjusted incident rates over a longer horizon; 90 days may be too short to detect changes reliably in rare injury outcomes.</div>',unsafe_allow_html=True)

st.divider()
st.subheader("04 | Illustrative 90-Day Budget")
budget=pd.DataFrame([
    {"Component":"Supervisor verification", "Amount":7280},
    {"Component":"Safety specialist review", "Amount":6240},
    {"Component":"Worker training", "Amount":2160},
    {"Component":"Pilot coordination", "Amount":3380},
    {"Component":"Dashboard monitoring", "Amount":2340},
    {"Component":"Corrective-action allowance", "Amount":4000},
    {"Component":"Contingency (15%)", "Amount":3810},
])
bc,bt=st.columns([1.4,1],gap="large")
with bc:
    fig=go.Figure(go.Bar(x=budget["Amount"],y=budget["Component"],orientation="h",marker_color=BLUE,
                         text=budget["Amount"].map(lambda x:f"${x:,.0f}"),textposition="outside",cliponaxis=False))
    fig.update_layout(template="plotly_white",height=340,margin=dict(l=12,r=76,t=15,b=32),
                      paper_bgcolor="white",plot_bgcolor="white",showlegend=False,
                      xaxis_title="Estimated cost (USD)",yaxis=dict(autorange="reversed"),
                      font=dict(family="Arial",size=13,color=NAVY))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with bt:
    st.metric("Base work + allowance", "$25,400")
    st.metric("Contingency (15%)", "$3,810")
    st.metric("Total proposed 90-day budget", "$29,210")
    st.caption("Labor rates, hours, staff count and $4,000 remediation allowance are assumptions. Actual hazard-remediation expenses could be materially higher.")

st.divider()
st.subheader("05 | Short-Term Financial Reality Check")
st.markdown('<div class="section-note">Expected-value illustration for these four sites and 90 days. These are not predicted realized savings or validated treatment effects.</div>',unsafe_allow_html=True)
scenarios=pd.DataFrame([
    {"Assumed injury-cost reduction":"5%", "Gross avoided costs":1573, "Net after pilot cost":-27637},
    {"Assumed injury-cost reduction":"10%", "Gross avoided costs":3146, "Net after pilot cost":-26064},
    {"Assumed injury-cost reduction":"20%", "Gross avoided costs":6291, "Net after pilot cost":-22919},
])
fc,ft=st.columns([1.4,1],gap="large")
with fc:
    fig=go.Figure(go.Bar(x=scenarios["Assumed injury-cost reduction"],y=scenarios["Net after pilot cost"],
                         marker_color=[RED]*3,text=scenarios["Net after pilot cost"].map(lambda x:f"−${abs(x):,.0f}"),
                         textposition="outside"))
    fig.update_layout(template="plotly_white",height=310,margin=dict(l=35,r=10,t=32,b=50),
                      paper_bgcolor="white",plot_bgcolor="white",font=dict(family="Arial",size=13,color=NAVY),
                      yaxis_title="Net benefit (USD)",xaxis_title="Assumed reduction",showlegend=False)
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with ft:
    st.metric("Modeled pilot exposure", "177,437 h")
    st.metric("Expected injury cost (no pilot)", "~$31,456")
    st.metric("Break-even cost reduction", "~92.9%")
    st.caption("Assumes historical incidents per worked hour and severity mix continue for 65 hypothetical workdays per site. The full-portfolio annual simulator uses different time and project scopes and must not be directly compared with this pilot budget.")

st.warning("**Decision implication:** This 90-day model does not show an easy financial break-even. Pilot justification should emphasize testing operational feasibility, corrective-action quality, and prevention processes — not promising immediate injury-cost savings.",icon="⚖️")

st.divider()
st.subheader("06 | Management Recommendation")
st.markdown("""
**Run a bounded, measurement-led pilot before scaling.** Start with four sites, verify baseline conditions and true outstanding hazards, assign accountable owners and capture actual staffing and corrective-action costs. At day 90, evaluate PTP / Focus Walk completion, severe-hazard follow-through and reporting quality. Use longer exposure-adjusted monitoring for injury outcomes and consider matched comparison sites when feasible.
""")
st.caption("Sources: Team's synthetic Layton case analysis and Rishi Valluru's finalized pilot proposal. Industry context: OSHA Safety Pays, NSC Injury Facts and BLS; model-specific unit injury costs are illustrative assumptions ($50,000 per LTA and $15,000 per other qualifying case), not Layton or OSHA category estimates. No causal effect is claimed.")
