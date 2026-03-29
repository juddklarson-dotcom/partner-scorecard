"""Plotly chart helpers for radar and bar charts."""

from __future__ import annotations
import plotly.graph_objects as go
from config import score_color


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert hex color to rgba string for Plotly compatibility."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

SCORE_LABELS = ["Brand Fit", "Audience Fit", "Conversion", "Content Quality", "Risk (inv)"]
SCORE_KEYS = ["brand_fit", "audience_fit", "conversion_potential", "content_quality", "risk_inverse"]


def radar_chart(partner_name: str, scores: dict, height: int = 350) -> go.Figure:
    """Single-partner radar chart of 5 sub-scores."""
    values = [scores.get(k, 0) for k in SCORE_KEYS]
    values.append(values[0])  # close the polygon

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=SCORE_LABELS + [SCORE_LABELS[0]],
        fill="toself",
        name=partner_name,
        line=dict(color=score_color(scores.get("overall", 50))),
        fillcolor=_hex_to_rgba(score_color(scores.get("overall", 50)), 0.2),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def multi_radar_chart(partners: list[dict], height: int = 400) -> go.Figure:
    """Overlay radar chart for multiple partners."""
    colors = ["#60a5fa", "#f472b6", "#34d399", "#fbbf24", "#a78bfa"]
    fig = go.Figure()
    for i, p in enumerate(partners):
        values = [p["scores"].get(k, 0) for k in SCORE_KEYS]
        values.append(values[0])
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=SCORE_LABELS + [SCORE_LABELS[0]],
            fill="toself",
            name=p["name"],
            line=dict(color=color),
            fillcolor=_hex_to_rgba(color, 0.13),
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
        margin=dict(l=40, r=40, t=20, b=40),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def grouped_bar_chart(partners: list[dict], height: int = 350) -> go.Figure:
    """Grouped bar chart comparing sub-scores across partners."""
    colors = ["#60a5fa", "#f472b6", "#34d399", "#fbbf24", "#a78bfa"]
    fig = go.Figure()
    for i, p in enumerate(partners):
        fig.add_trace(go.Bar(
            name=p["name"],
            x=SCORE_LABELS,
            y=[p["scores"].get(k, 0) for k in SCORE_KEYS],
            marker_color=colors[i % len(colors)],
        ))
    fig.update_layout(
        barmode="group",
        yaxis=dict(range=[0, 100], title="Score"),
        margin=dict(l=40, r=20, t=20, b=40),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
    )
    return fig
