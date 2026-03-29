"""Screen 3: Compare Partners — side-by-side comparison of 2-4 partners."""

import streamlit as st
import pandas as pd
from components.charts import multi_radar_chart, grouped_bar_chart
from scoring.engine import get_scores_dict


st.title("Compare Partners")
st.caption("Select 2–4 partners to compare side by side.")

df = st.session_state.scored_df
all_names = df["partner_name"].tolist()

default = st.session_state.compare_partners if st.session_state.compare_partners else []
# Ensure defaults are valid
default = [n for n in default if n in all_names]

selected = st.multiselect(
    "Select partners to compare",
    options=all_names,
    default=default[:4],
    max_selections=4,
)

if len(selected) < 2:
    st.info("Select at least 2 partners to begin comparison.")
    st.stop()

# Update session state
st.session_state.compare_partners = selected

# Build partner data
partners = []
for name in selected:
    row = df[df["partner_name"] == name].iloc[0]
    partners.append({
        "name": name,
        "row": row,
        "scores": get_scores_dict(row),
    })

# ── Charts ─────────────────────────────────────────────────────
col_radar, col_bar = st.columns(2)
with col_radar:
    st.subheader("Score Profile")
    fig = multi_radar_chart(partners)
    st.plotly_chart(fig, use_container_width=True)
with col_bar:
    st.subheader("Sub-Score Comparison")
    fig = grouped_bar_chart(partners)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Comparison table ───────────────────────────────────────────
st.subheader("Detailed Comparison")

attributes = [
    ("Overall Score", "overall_score"),
    ("Brand Fit", "brand_fit"),
    ("Audience Fit", "audience_fit"),
    ("Conversion Potential", "conversion_potential"),
    ("Content Quality", "content_quality"),
    ("Risk Score", "risk_score"),
    ("Risk Level", "risk_level"),
    ("Recommended Action", "recommended_action"),
    ("Best Use Case", "best_use_case"),
    ("Type", "partner_type"),
    ("Platform", "primary_platform"),
    ("Niche", "niche"),
    ("Followers", "follower_count"),
    ("Engagement Rate", "engagement_rate"),
    ("Est. Cost", "estimated_cost_or_commission"),
    ("Disclosure", "disclosure_quality"),
]

table_data = {}
for label, key in attributes:
    row_vals = {}
    for p in partners:
        val = p["row"][key]
        if isinstance(val, float) and key not in ("engagement_rate",):
            row_vals[p["name"]] = f"{val:.1f}"
        elif key == "follower_count":
            row_vals[p["name"]] = f"{int(val):,}"
        elif key == "engagement_rate":
            row_vals[p["name"]] = f"{val}%"
        else:
            row_vals[p["name"]] = str(val)
    table_data[label] = row_vals

compare_df = pd.DataFrame(table_data).T
compare_df.index.name = "Attribute"
st.dataframe(compare_df, use_container_width=True)

st.divider()

# ── Why one is better ──────────────────────────────────────────
st.subheader("Analysis")

best = max(partners, key=lambda p: p["scores"]["overall"])
others = [p for p in partners if p["name"] != best["name"]]

st.markdown(f"**{best['name']}** leads with an overall score of **{best['scores']['overall']:.0f}**.")

for other in others:
    diff = best["scores"]["overall"] - other["scores"]["overall"]
    # Find biggest sub-score gap
    gaps = []
    score_labels = {
        "brand_fit": "Brand Fit",
        "audience_fit": "Audience Fit",
        "conversion_potential": "Conversion Potential",
        "content_quality": "Content Quality",
        "risk_inverse": "Risk (inverted)",
    }
    for key, label in score_labels.items():
        gap = best["scores"][key] - other["scores"][key]
        gaps.append((label, gap))
    gaps.sort(key=lambda x: abs(x[1]), reverse=True)

    biggest_advantage = gaps[0]
    other_advantage = None
    for label, gap in gaps:
        if gap < 0:
            other_advantage = (label, abs(gap))
            break

    text = f"- vs **{other['name']}** (+{diff:.0f} overall): "
    text += f"Biggest advantage in **{biggest_advantage[0]}** (+{biggest_advantage[1]:.0f}). "
    if other_advantage:
        text += f"{other['name']} is stronger in **{other_advantage[0]}** (+{other_advantage[1]:.0f})."

    st.markdown(text)
