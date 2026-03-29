"""Reusable score card and badge components."""

from __future__ import annotations
import streamlit as st
from config import score_color, RISK_COLORS, ACTION_COLORS


def render_score_badge(label: str, value: float, delta: float | None = None):
    """Render a colored metric card for a score 0-100."""
    color = score_color(value)
    delta_html = ""
    if delta is not None:
        arrow = "▲" if delta >= 0 else "▼"
        delta_color = "#22c55e" if delta >= 0 else "#ef4444"
        delta_html = f'<span style="font-size:0.8rem;color:{delta_color}">{arrow} {abs(delta):.1f} vs avg</span>'

    st.markdown(
        f"""
        <div style="background:#1e1e2e;border-left:4px solid {color};border-radius:8px;
                    padding:12px 16px;margin-bottom:8px;">
            <div style="color:#9ca3af;font-size:0.8rem;margin-bottom:4px;">{label}</div>
            <div style="color:{color};font-size:1.8rem;font-weight:700;">{value:.0f}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_risk_badge(risk_level: str):
    """Render a colored risk level badge."""
    color = RISK_COLORS.get(risk_level, "#9ca3af")
    st.markdown(
        f'<span style="background:{color}22;color:{color};padding:4px 12px;'
        f'border-radius:12px;font-weight:600;font-size:0.85rem;">{risk_level} Risk</span>',
        unsafe_allow_html=True,
    )


def render_action_badge(action: str):
    """Render a colored action recommendation badge."""
    color = ACTION_COLORS.get(action, "#9ca3af")
    st.markdown(
        f'<span style="background:{color}22;color:{color};padding:4px 12px;'
        f'border-radius:12px;font-weight:600;font-size:0.85rem;">{action}</span>',
        unsafe_allow_html=True,
    )
