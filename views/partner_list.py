"""Screen 1: Partner List — triage view with filters."""

import streamlit as st
from components.export import partner_summary_csv

st.title("Partner Scorecard")
st.caption("Review, score, and prioritize creators and affiliates for recruitment.")

df = st.session_state.scored_df

# ── Sidebar Filters ────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    platforms = st.multiselect(
        "Platform",
        options=sorted(df["primary_platform"].unique()),
        default=[],
    )
    partner_types = st.multiselect(
        "Partner Type",
        options=sorted(df["partner_type"].unique()),
        default=[],
    )
    niches = st.multiselect(
        "Niche",
        options=sorted(df["niche"].unique()),
        default=[],
    )
    risk_levels = st.multiselect(
        "Risk Level",
        options=["Low", "Medium", "High", "Critical"],
        default=[],
    )
    score_range = st.slider(
        "Overall Score Range", 0, 100, (0, 100)
    )

# Apply filters
filtered = df.copy()
if platforms:
    filtered = filtered[filtered["primary_platform"].isin(platforms)]
if partner_types:
    filtered = filtered[filtered["partner_type"].isin(partner_types)]
if niches:
    filtered = filtered[filtered["niche"].isin(niches)]
if risk_levels:
    filtered = filtered[filtered["risk_level"].isin(risk_levels)]
filtered = filtered[
    (filtered["overall_score"] >= score_range[0])
    & (filtered["overall_score"] <= score_range[1])
]

# ── Summary metrics ────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Partners", len(filtered))
col2.metric("Avg Score", f"{filtered['overall_score'].mean():.0f}" if len(filtered) else "—")
recruit_count = len(filtered[filtered["recommended_action"] == "Recruit Now"])
col3.metric("Recruit Now", recruit_count)
escalate_count = len(filtered[filtered["recommended_action"] == "Escalate for Review"])
col4.metric("Escalate", escalate_count)

st.divider()

# ── Partner table ──────────────────────────────────────────────
display_cols = [
    "partner_name", "partner_type", "primary_platform", "niche",
    "overall_score", "risk_level", "recommended_action", "best_use_case",
]
display_df = filtered[display_cols].copy()
display_df.columns = [
    "Partner", "Type", "Platform", "Niche",
    "Score", "Risk", "Action", "Best Use Case",
]

# Configure columns
column_config = {
    "Score": st.column_config.ProgressColumn(
        "Score",
        min_value=0,
        max_value=100,
        format="%d",
    ),
}

# Selection for compare and detail view
event = st.dataframe(
    display_df,
    column_config=column_config,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="multi-row",
)

# ── Action buttons ─────────────────────────────────────────────
selected_rows = event.selection.rows if event.selection else []

col_a, col_b, col_c = st.columns([1, 1, 3])

with col_a:
    if selected_rows and len(selected_rows) == 1:
        if st.button("View Detail →", type="primary"):
            idx = selected_rows[0]
            partner_name = display_df.iloc[idx]["Partner"]
            st.session_state.selected_partner = partner_name
            st.switch_page("views/partner_detail.py")

with col_b:
    if selected_rows and 2 <= len(selected_rows) <= 4:
        if st.button("Compare Selected ⚖️", type="secondary"):
            names = [display_df.iloc[i]["Partner"] for i in selected_rows]
            st.session_state.compare_partners = names
            st.switch_page("views/compare.py")

if selected_rows:
    n = len(selected_rows)
    if n == 1:
        st.caption("Select a row and click **View Detail** to see the full breakdown.")
    elif 2 <= n <= 4:
        st.caption(f"{n} partners selected — click **Compare Selected** to compare them.")
    elif n > 4:
        st.caption("Select up to 4 partners to compare.")
else:
    st.caption("Click a row to select it. Select 1 for detail view, or 2–4 for comparison.")

# ── CSV export ─────────────────────────────────────────────────
st.divider()
st.download_button(
    "📥 Export Filtered Results (CSV)",
    data=partner_summary_csv(filtered),
    file_name="partner_scorecard_export.csv",
    mime="text/csv",
)
