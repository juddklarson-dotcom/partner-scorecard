"""Screen 2: Partner Detail — score breakdown, AI analysis, and recommendations."""

import streamlit as st
from components.score_card import render_score_badge, render_risk_badge, render_action_badge
from components.charts import radar_chart
from components.export import partner_detail_text
from scoring.engine import get_scores_dict


df = st.session_state.scored_df
all_names = df["partner_name"].tolist()

# ── Partner selection ──────────────────────────────────────────
default_idx = 0
if st.session_state.selected_partner and st.session_state.selected_partner in all_names:
    default_idx = all_names.index(st.session_state.selected_partner)

partner_name = st.selectbox(
    "Select a partner",
    options=all_names,
    index=default_idx,
)
st.session_state.selected_partner = partner_name

match = df[df["partner_name"] == partner_name]
if match.empty:
    st.error(f"Partner '{partner_name}' not found.")
    st.stop()

row = match.iloc[0]
scores = get_scores_dict(row)
avgs = {
    "brand_fit": df["brand_fit"].mean(),
    "audience_fit": df["audience_fit"].mean(),
    "conversion_potential": df["conversion_potential"].mean(),
    "content_quality": df["content_quality"].mean(),
    "risk_score": df["risk_score"].mean(),
}

# ── Header ─────────────────────────────────────────────────────
st.header(partner_name)
st.caption(f"{row['partner_type']}  ·  {row['primary_platform']}  ·  {row['niche']}  ·  {row['audience_region']}")

st.divider()

# ── Score cards ────────────────────────────────────────────────
cols = st.columns(6)
with cols[0]:
    render_score_badge("Overall Score", row["overall_score"])
with cols[1]:
    render_score_badge("Brand Fit", row["brand_fit"], row["brand_fit"] - avgs["brand_fit"])
with cols[2]:
    render_score_badge("Audience Fit", row["audience_fit"], row["audience_fit"] - avgs["audience_fit"])
with cols[3]:
    render_score_badge("Conversion", row["conversion_potential"], row["conversion_potential"] - avgs["conversion_potential"])
with cols[4]:
    render_score_badge("Content Quality", row["content_quality"], row["content_quality"] - avgs["content_quality"])
with cols[5]:
    render_score_badge("Risk", row["risk_score"], row["risk_score"] - avgs["risk_score"])

# ── Radar chart + key stats ────────────────────────────────────
col_chart, col_info = st.columns([3, 2])

with col_chart:
    st.subheader("Score Breakdown")
    fig = radar_chart(partner_name, scores)
    st.plotly_chart(fig, use_container_width=True)

with col_info:
    st.subheader("Recommendation")
    render_action_badge(row["recommended_action"])
    st.write("")
    render_risk_badge(row["risk_level"])
    st.write("")
    st.markdown(f"**Best Use Case:** {row['best_use_case']}")

    st.divider()
    st.markdown("**Key Stats**")
    st.markdown(f"- Followers: **{row['follower_count']:,}**")
    st.markdown(f"- Engagement Rate: **{row['engagement_rate']}%**")
    st.markdown(f"- Avg Views: **{row['avg_views']:,}**")
    st.markdown(f"- Est. Cost: **{row['estimated_cost_or_commission']}**")
    st.markdown(f"- Disclosure: **{row['disclosure_quality']}**")
    st.markdown(f"- Coupon Heavy: **{'Yes' if str(row['coupon_heavy']).upper() == 'TRUE' else 'No'}**")

st.divider()

# ── Content samples ────────────────────────────────────────────
col_bio, col_content = st.columns(2)
with col_bio:
    st.markdown("**Bio**")
    st.info(row["sample_bio"])
with col_content:
    st.markdown("**Sample Content**")
    st.info(row["sample_content_text"])

if str(row["prior_brand_examples"]).lower() not in ("none", "nan", ""):
    st.markdown(f"**Prior Brand Work:** {row['prior_brand_examples']}")

st.divider()

# ── AI Analysis ────────────────────────────────────────────────
st.subheader("AI Analysis")

try:
    from ai.rationale import generate_fit_rationale, generate_campaign_angle, generate_risk_summary
    ai_available = True
except Exception:
    ai_available = False

ai_texts = {}

with st.expander("Fit Rationale", expanded=True):
    if ai_available:
        with st.spinner("Generating analysis..."):
            text = generate_fit_rationale(row.to_dict(), scores)
            st.write(text)
            ai_texts["Fit Rationale"] = text
    else:
        st.caption("AI analysis unavailable — install google-genai to enable.")
        st.write(f"Overall score {row['overall_score']:.0f}/100. "
                 f"Strongest area: brand fit ({row['brand_fit']:.0f}). "
                 f"Risk level: {row['risk_level']}.")

with st.expander("Campaign Angle"):
    if ai_available:
        with st.spinner("Generating campaign suggestion..."):
            text = generate_campaign_angle(row.to_dict(), row["best_use_case"])
            st.write(text)
            ai_texts["Campaign Angle"] = text
    else:
        st.caption("AI analysis unavailable — install google-genai to enable.")
        st.write(f"Suggested use case: {row['best_use_case']}.")

with st.expander("Risk Assessment"):
    if ai_available:
        with st.spinner("Generating risk assessment..."):
            text = generate_risk_summary(row.to_dict(), row["risk_score"])
            st.write(text)
            ai_texts["Risk Assessment"] = text
    else:
        st.caption("AI analysis unavailable — install google-genai to enable.")
        st.write(f"Risk score: {row['risk_score']:.0f}/100 ({row['risk_level']}). "
                 f"Engagement quality: {row['suspected_engagement_quality']}. "
                 f"Disclosure: {row['disclosure_quality']}.")

# ── Export ─────────────────────────────────────────────────────
st.divider()
summary = partner_detail_text(row, ai_texts if ai_texts else None)
st.download_button(
    "📥 Export Partner Summary",
    data=summary,
    file_name=f"partner_summary_{partner_name.replace(' ', '_').lower()}.txt",
    mime="text/plain",
)
