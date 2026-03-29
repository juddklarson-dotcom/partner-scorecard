"""Export helpers for CSV and text summaries."""

from __future__ import annotations
import pandas as pd


def partner_summary_csv(df: pd.DataFrame) -> str:
    """Export scored partner data as CSV string."""
    export_cols = [
        "partner_name", "partner_type", "primary_platform", "niche",
        "overall_score", "brand_fit", "audience_fit", "conversion_potential",
        "content_quality", "risk_score", "risk_level", "recommended_action",
        "best_use_case",
    ]
    return df[export_cols].to_csv(index=False)


def partner_detail_text(row: pd.Series, ai_texts: dict | None = None) -> str:
    """Generate a plain-text summary for a single partner."""
    lines = [
        f"Partner Scorecard — {row['partner_name']}",
        "=" * 50,
        f"Type: {row['partner_type']}",
        f"Platform: {row['primary_platform']}",
        f"Niche: {row['niche']}",
        f"Region: {row['audience_region']}",
        f"Followers: {row['follower_count']:,}",
        f"Engagement Rate: {row['engagement_rate']}%",
        "",
        "SCORES",
        "-" * 30,
        f"Overall Score:        {row['overall_score']:.1f} / 100",
        f"Brand Fit:            {row['brand_fit']:.1f} / 100",
        f"Audience Fit:         {row['audience_fit']:.1f} / 100",
        f"Conversion Potential:  {row['conversion_potential']:.1f} / 100",
        f"Content Quality:      {row['content_quality']:.1f} / 100",
        f"Risk Score:           {row['risk_score']:.1f} / 100 ({row['risk_level']})",
        "",
        f"Recommended Action:   {row['recommended_action']}",
        f"Best Use Case:        {row['best_use_case']}",
    ]

    if ai_texts:
        lines += ["", "AI ANALYSIS", "-" * 30]
        for title, text in ai_texts.items():
            lines += [f"\n{title}:", text]

    return "\n".join(lines)
