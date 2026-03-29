"""Screen 4: Weekly Summary — manager roll-up view."""

import streamlit as st
from datetime import date


def _partner_card(row, card_type: str):
    """Render a compact partner card for the summary view."""
    if card_type == "recruit":
        color = "#22c55e"
        detail = f"Score: {row['overall_score']:.0f} · {row['best_use_case']}"
    elif card_type == "seeding":
        color = "#eab308"
        detail = f"Score: {row['overall_score']:.0f} · {row['primary_platform']}"
    else:
        color = "#ef4444"
        detail = f"Risk: {row['risk_score']:.0f} · {row['risk_level']}"

    st.markdown(
        f"""
        <div style="background:#1e1e2e;border-left:3px solid {color};border-radius:6px;
                    padding:8px 12px;margin-bottom:6px;">
            <div style="font-weight:600;color:#e2e8f0;font-size:0.9rem;">{row['partner_name']}</div>
            <div style="color:#9ca3af;font-size:0.75rem;">{row['partner_type']} · {row['primary_platform']}</div>
            <div style="color:{color};font-size:0.8rem;margin-top:2px;">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.title("Weekly Summary")
st.caption(f"Partner pipeline overview — {date.today().strftime('%B %d, %Y')}")

df = st.session_state.scored_df

st.divider()

# ── Top picks ──────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🟢 Top 5: Recruit Now")
    recruit = df[df["recommended_action"] == "Recruit Now"].head(5)
    if recruit.empty:
        st.caption("No partners flagged for immediate recruitment.")
    for _, row in recruit.iterrows():
        _partner_card(row, "recruit")

with col2:
    st.subheader("🟡 Top 3: Seeding Candidates")
    seeding = df[df["recommended_action"] == "Test with Seeding"].head(3)
    if seeding.empty:
        st.caption("No seeding candidates identified.")
    for _, row in seeding.iterrows():
        _partner_card(row, "seeding")

with col3:
    st.subheader("🔴 Top 3: Risk Review")
    risky = df.nlargest(3, "risk_score")
    for _, row in risky.iterrows():
        _partner_card(row, "risk")

st.divider()

# ── Common themes ──────────────────────────────────────────────
st.subheader("Common Themes")

# Platform distribution among top performers
top_half = df[df["overall_score"] >= df["overall_score"].median()]
platform_counts = top_half["primary_platform"].value_counts()
top_platform = platform_counts.index[0] if not platform_counts.empty else "N/A"
top_platform_pct = (platform_counts.iloc[0] / len(top_half) * 100) if not platform_counts.empty else 0

# Risk issues
disclosure_issues = len(df[df["disclosure_quality"].isin(["Poor", "None"])])
suspicious = len(df[df["suspected_engagement_quality"].isin(["Questionable", "Suspicious"])])
coupon_heavy = len(df[df["coupon_heavy"].astype(str).str.upper() == "TRUE"])

# Niche distribution
niche_counts = top_half["niche"].value_counts()

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Pipeline Insights**")
    st.markdown(f"- **{top_platform_pct:.0f}%** of high-scoring partners are on **{top_platform}**")
    st.markdown(f"- Top niches among strong partners: **{', '.join(niche_counts.head(3).index.tolist())}**")
    st.markdown(f"- **{len(df[df['recommended_action'] == 'Recruit Now'])}** partners ready for immediate recruitment")
    avg_score = df["overall_score"].mean()
    st.markdown(f"- Average pipeline score: **{avg_score:.0f}/100**")

with col_b:
    st.markdown("**Risk Overview**")
    st.markdown(f"- **{disclosure_issues}** partners with poor or missing disclosure practices")
    st.markdown(f"- **{suspicious}** partners with questionable or suspicious engagement")
    st.markdown(f"- **{coupon_heavy}** coupon-heavy partners (potential brand dilution)")
    escalate = len(df[df["recommended_action"] == "Escalate for Review"])
    st.markdown(f"- **{escalate}** partners flagged for escalation review")

st.divider()

# ── Suggested actions ──────────────────────────────────────────
st.subheader("Suggested Next Actions")

actions = []

# Recruitment outreach
recruit_names = df[df["recommended_action"] == "Recruit Now"].head(3)["partner_name"].tolist()
if recruit_names:
    actions.append(f"**Outreach**: Contact **{', '.join(recruit_names)}** for partnership discussions this week.")

# Seeding
seed_names = df[df["recommended_action"] == "Test with Seeding"].head(2)["partner_name"].tolist()
if seed_names:
    actions.append(f"**Seeding**: Send product samples to **{', '.join(seed_names)}** for trial content.")

# Risk review
if disclosure_issues > 0:
    risk_names = df[df["disclosure_quality"].isin(["Poor", "None"])]["partner_name"].tolist()
    actions.append(f"**Compliance**: Request disclosure audits for **{', '.join(risk_names[:3])}**.")

if suspicious > 0:
    sus_names = df[df["suspected_engagement_quality"].isin(["Questionable", "Suspicious"])]["partner_name"].tolist()
    actions.append(f"**Investigation**: Review engagement authenticity for **{', '.join(sus_names[:3])}**.")

# Platform diversification
if top_platform_pct > 50:
    actions.append(f"**Diversification**: {top_platform_pct:.0f}% of top partners are on {top_platform} — consider expanding to other platforms.")

for action in actions:
    st.markdown(f"- {action}")
