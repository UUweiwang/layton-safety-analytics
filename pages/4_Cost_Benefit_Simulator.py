"""Layton Safety Analytics — incident prevention financial scenarios.

All incident counts are from a *synthetic* data snapshot (safety_incidents.csv).
Rishi's category-based dollar amounts are illustrative assumptions, not Layton
financial records and not published industry averages. The model is sensitivity
arithmetic, not causal/predictive estimation of intervention effectiveness.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Incident Prevention | Cost-Benefit Simulator",
    page_icon="💼",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #F8FAFC; }
    h1, h2, h3 { color: #17324D !important; }
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border: 1px solid #DCE5EF;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

NAVY = "#17324D"
CLASSES = ["First Aid", "Lost Time Accident", "REC", "RECR"]
HISTORY = pd.DataFrame(
    [
        {"Year": "2024", "First Aid": 28, "Lost Time Accident": 14, "REC": 5, "RECR": 3},
        {"Year": "2025", "First Aid": 25, "Lost Time Accident": 6, "REC": 5, "RECR": 6},
        {"Year": "2026 (Jan–Sep)", "First Aid": 23, "Lost Time Accident": 4, "REC": 3, "RECR": 1},
    ]
)
HISTORY["All incident records"] = HISTORY[CLASSES].sum(axis=1)

st.title("Incident Prevention | Cost-Benefit Simulator")
st.caption("Layton Construction Safety Analytics | Synthetic data | Illustrative financial scenarios, not a forecast")
st.write(
    "Use historical **injury records** as a reference, then test how *assumed* "
    "incident reductions and prevention costs could affect financial outcomes. "
    "Each record corresponds to an injured worker; records are not necessarily "
    "unique multi-worker events or OSHA-recordable cases."
)

st.divider()
st.subheader("1. Historical Incident Overview")
cols = st.columns(3)
cols[0].metric("2024 | Full year", "50")
cols[1].metric("2025 | Full year", "42")
cols[2].metric("2026 | Jan–Sep", "31")

long_history = HISTORY.melt(
    id_vars="Year", value_vars=CLASSES,
    var_name="Incident Classification", value_name="Records"
)
fig = px.bar(
    long_history, x="Year", y="Records", color="Incident Classification",
    barmode="stack", title="Incident Records by Year and Classification",
    color_discrete_map={
        "First Aid": "#93BFE8", "Lost Time Accident": "#EA8C35",
        "REC": "#1D72B8", "RECR": "#0F766E"
    },
)
fig.update_layout(
    template="plotly_white", paper_bgcolor="white", plot_bgcolor="white",
    height=390, font={"family": "Arial", "size": 14, "color": "#1F2937"},
    title_font={"size": 18, "color": NAVY},
    margin={"l": 25, "r": 25, "t": 65, "b": 30},
)
fig.update_yaxes(gridcolor="#E2E8F0")
st.plotly_chart(fig, use_container_width=True)
with st.expander("View incident classification counts"):
    st.dataframe(HISTORY, hide_index=True, use_container_width=True)
st.caption(
    "Source: synthetic safety_incidents.csv. 2026 only includes January–September. "
    "These are all logged injury records, including First Aid—not OSHA recordable counts. "
    "REC and RECR labels are used as supplied; their exact definitions require confirmation."
)

st.divider()
st.subheader("2. Prevention Investment Scenarios")
st.info(
    "Historical record counts come from the synthetic dataset. "
    "Cost per case, prevention effectiveness, and program investment are adjustable "
    "assumptions—not actual Layton cost data, estimates of causal effect, or a prediction."
)

period = st.selectbox(
    "Historical reference (full years only)",
    ["2025 (42 injury records)", "2024 (50 injury records)"],
    index=0,
)
baseline = HISTORY.iloc[1] if period.startswith("2025") else HISTORY.iloc[0]

mode = st.radio(
    "Cost calculation approach",
    ["Severity-based assumptions (Rishi)", "Blended cost per record (original)"],
    horizontal=True,
    help="The severity-based method avoids applying the same assumed cost to First Aid and lost-time cases. Neither method predicts avoided incidents.",
)

left, right = st.columns(2)
with left:
    reduction_pct = st.slider(
        "Assumed reduction in each incident classification (%)",
        min_value=0, max_value=50, value=20, step=5,
        help="Same reduction percentage applied to each classification for simplicity. No observed effectiveness is implied.",
    )
with right:
    investment = st.slider(
        "Assumed annual prevention investment ($)",
        min_value=0, max_value=250000, value=80000, step=5000,
        help="Hypothetical yearly program cost, not a Layton quotation.",
    )

costs = {}
if mode.startswith("Severity"):
    st.markdown("**Cost assumptions by recorded classification**")
    c1, c2, c3 = st.columns(3)
    with c1:
        costs["Lost Time Accident"] = st.number_input(
            "Lost Time Accident: cost per case ($)",
            min_value=0, max_value=250000, value=50000, step=5000,
            help="Rishi's illustrative assumption; NCCI's national claims average is only a contextual reference.",
        )
    with c2:
        other_cost = st.number_input(
            "REC / RECR: cost per case ($)",
            min_value=0, max_value=150000, value=15000, step=2500,
            help="Rishi's illustrative assumption applied to these two dataset labels. Their precise definitions are not confirmed.",
        )
        costs["REC"] = other_cost
        costs["RECR"] = other_cost
    with c3:
        costs["First Aid"] = st.number_input(
            "First Aid: cost per case ($)",
            min_value=0, max_value=10000, value=0, step=250,
            help="Default $0 excludes First Aid costs from the financial estimate for conservatism; it does NOT mean actual First Aid costs nothing.",
        )
    st.caption(
        "The default $0 for First Aid means its costs are **not estimated**; "
        "they are not proven to be zero. Change this input if credible First Aid "
        "cost information becomes available. REC and RECR are grouped as other "
        "non-First-Aid records for sensitivity analysis, not classified as OSHA recordables."
    )
else:
    blended_cost = st.slider(
        "Assumed blended cost per injury record ($)",
        min_value=0, max_value=75000, value=15000, step=1000,
        help="Original simplified model: applies one hypothetical average to all records, including First Aid.",
    )
    costs = {name: blended_cost for name in CLASSES}
    st.warning(
        "Blended mode prices First Aid and lost-time accidents identically. "
        "Use only as a simplified sensitivity check, not an industry average."
    )

rows = []
for category in CLASSES:
    count = int(baseline[category])
    unit_cost = float(costs[category])
    rows.append({
        "Category": category,
        "Recorded cases": count,
        "Assumed cost per case ($)": unit_cost,
        "Baseline assumed cost ($)": count * unit_cost,
    })
case_table = pd.DataFrame(rows)
base_cost = float(case_table["Baseline assumed cost ($)"].sum())
assumed_avoided = sum(int(baseline[cat]) for cat in CLASSES) * reduction_pct / 100.0
gross = base_cost * reduction_pct / 100.0
net = gross - investment
roi = 100.0 * net / investment if investment > 0 else None

with st.expander("See exactly how the category-level baseline is calculated"):
    st.dataframe(
        case_table.style.format({
            "Assumed cost per case ($)": "${:,.0f}",
            "Baseline assumed cost ($)": "${:,.0f}",
        }),
        use_container_width=True, hide_index=True,
    )
    st.write(f"**Total assumed baseline injury cost: ${base_cost:,.0f}**")

st.divider()
st.subheader("3. Financial Impact — What-if Results")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Expected records avoided", f"{assumed_avoided:.1f}")
k2.metric("Gross cost avoidance", f"${gross:,.0f}")
k3.metric("Net benefit", f"${net:,.0f}")
k4.metric("Illustrative ROI", f"{roi:.1f}%" if roi is not None else "N/A")

st.caption(
    "Baseline assumed cost = sum(case count × assumed category cost). "
    "Gross avoidance = baseline assumed cost × assumed reduction %. "
    "Net benefit = gross avoidance − annual investment. "
    "ROI = net benefit / investment (undefined when investment is $0). "
    "Fractional avoided cases are scenario expectations, not observed outcomes. "
    "This assumes the same proportional reduction in all categories."
)

scenarios = []
for pct in [10, 20, 30]:
    saved = base_cost * pct / 100.0
    benefit = saved - investment
    scenario_roi = 100 * benefit / investment if investment > 0 else None
    scenarios.append({
        "Assumed reduction": f"{pct}%",
        "Gross savings": f"${saved:,.0f}",
        "Net benefit": f"${benefit:,.0f}",
        "ROI": f"{scenario_roi:.1f}%" if scenario_roi is not None else "N/A",
    })
st.markdown("**Sensitivity: 10%, 20%, and 30% assumed reductions**")
st.dataframe(pd.DataFrame(scenarios), hide_index=True, use_container_width=True)

if base_cost > 0:
    threshold = 100.0 * investment / base_cost
    if threshold <= 100:
        st.write(
            f"**Illustrative break-even reduction:** {threshold:.1f}% "
            "under the selected cost and investment assumptions."
        )
    else:
        st.write("**Break-even:** More than a 100% reduction would be required under these assumptions.")
else:
    st.write("**Break-even:** Not defined when the assumed baseline injury cost is $0.")

st.divider()
st.subheader("4. Industry Context and Assumption Sources")
st.markdown(
    """
    **Industry references (context; not Layton-specific prices):**

    - [OSHA Safety Pays](https://www.osha.gov/safetypays/estimator): demonstrates direct and indirect
      injury costs and the potential profitability impact. OSHA cautions that it is an awareness tool,
      not a detailed estimate of an individual employer's actual injury costs.
    - [National Safety Council — Work Injury Costs](https://injuryfacts.nsc.org/work/costs/):
      **$48,000 per medically consulted work injury (2024)**, a broad societal economic cost estimate,
      not equivalent to the cost borne by an individual employer.
    - [NSC / NCCI — Workers' Compensation Costs](https://injuryfacts.nsc.org/work/costs/workers-compensation-costs/):
      **$50,076 per workers' compensation claim** for accidents occurring in 2023–2024,
      an average across covered claims, not an average for the dataset's Lost Time Accident category.

    **Rishi's scenario assumptions:** $50,000 per Lost Time Accident and $15,000 per
    other selected non-First-Aid record (REC/RECR). These figures are **illustrative**;
    they are not published benchmark rates. First Aid is excluded by default until
    a credible per-case cost is provided.
    """
)

st.subheader("5. Management Recommendation")
st.markdown(
    """
    1. Prioritize high-severity unresolved hazards, then verify completed corrective actions.
    2. Coordinate subcontractor schedules and investigate project-level incident-rate patterns.
    3. Track PTP and safety-walk completion alongside exposure-adjusted incident rates.
    4. Pilot prevention measures, record actual program costs and injury cost by class,
       then compare outcomes before making any realized-savings claim.
    """
)
st.warning(
    "These results are not a prediction or an estimate of Layton's actual savings. "
    "The dataset is synthetic; event labels, cost assumptions, intervention effectiveness, "
    "and causality have not been externally validated."
)
st.caption("Layton Construction Safety Analytics | KPMG Data Analytics Challenge 2026")
