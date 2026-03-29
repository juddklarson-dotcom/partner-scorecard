import streamlit as st

st.set_page_config(
    page_title="Partner Scorecard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Cache scored data once ──────────────────────────────────────────
from scoring.engine import load_and_score


@st.cache_data
def get_scored_data():
    return load_and_score()


if "scored_df" not in st.session_state:
    st.session_state.scored_df = get_scored_data()
if "selected_partner" not in st.session_state:
    st.session_state.selected_partner = None
if "compare_partners" not in st.session_state:
    st.session_state.compare_partners = []

# ── Page routing ────────────────────────────────────────────────────
pages = st.navigation(
    [
        st.Page("views/partner_list.py", title="Partner List", icon="📋", default=True),
        st.Page("views/partner_detail.py", title="Partner Detail", icon="🔍"),
        st.Page("views/compare.py", title="Compare Partners", icon="⚖️"),
        st.Page("views/weekly_summary.py", title="Weekly Summary", icon="📊"),
    ]
)
pages.run()
