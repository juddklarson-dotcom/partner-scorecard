"""Scoring engine — loads CSV, computes all scores, returns enriched DataFrame."""

from __future__ import annotations
import os
import pandas as pd
from scoring.rules import (
    brand_fit_score,
    audience_fit_score,
    conversion_potential_score,
    content_quality_score,
    risk_score,
)
from config import WEIGHTS, ACTION_RULES, risk_label


DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "partners.csv")


def get_scores_dict(row) -> dict:
    """Extract the sub-scores dict used by charts and detail views."""
    return {
        "brand_fit": row["brand_fit"],
        "audience_fit": row["audience_fit"],
        "conversion_potential": row["conversion_potential"],
        "content_quality": row["content_quality"],
        "risk_inverse": 100 - row["risk_score"],
        "overall": row["overall_score"],
    }


def load_and_score() -> pd.DataFrame:
    """Load partner CSV and compute all scores. Returns enriched DataFrame."""
    df = pd.read_csv(DATA_PATH, keep_default_na=False, na_values=[""])

    # Compute sub-scores
    df["brand_fit"] = df.apply(brand_fit_score, axis=1)
    df["audience_fit"] = df.apply(audience_fit_score, axis=1)
    df["conversion_potential"] = df.apply(conversion_potential_score, axis=1)
    df["content_quality"] = df.apply(content_quality_score, axis=1)
    df["risk_score"] = df.apply(risk_score, axis=1)

    # Composite score
    df["overall_score"] = (
        WEIGHTS["brand_fit"] * df["brand_fit"]
        + WEIGHTS["audience_fit"] * df["audience_fit"]
        + WEIGHTS["conversion_potential"] * df["conversion_potential"]
        + WEIGHTS["content_quality"] * df["content_quality"]
        + WEIGHTS["risk_inverse"] * (100 - df["risk_score"])
    ).round(1)

    # Risk level label
    df["risk_level"] = df["risk_score"].apply(risk_label)

    # Recommended action
    df["recommended_action"] = df.apply(_map_action, axis=1)

    # Best use case
    df["best_use_case"] = df.apply(_map_use_case, axis=1)

    return df.sort_values("overall_score", ascending=False).reset_index(drop=True)


def _map_action(row) -> str:
    """Deterministic action mapping based on score/risk thresholds."""
    score = row["overall_score"]
    risk = row["risk_score"]

    for rule in ACTION_RULES:
        min_score = rule.get("min_score", 0)
        max_risk = rule.get("max_risk", 100)
        min_risk = rule.get("min_risk", 0)

        if score >= min_score and min_risk <= risk <= max_risk:
            return rule["action"]

    return "Monitor"


def _map_use_case(row) -> str:
    """Map best use case based on highest sub-score and partner type."""
    partner_type = str(row.get("partner_type", "")).lower()

    sub_scores = {
        "brand_fit": row["brand_fit"],
        "audience_fit": row["audience_fit"],
        "conversion_potential": row["conversion_potential"],
        "content_quality": row["content_quality"],
    }
    top_score = max(sub_scores, key=sub_scores.get)

    # Partner type overrides
    if "ugc" in partner_type:
        return "UGC Creation"

    # Content-based signals
    content = str(row.get("sample_content_text", "")).lower()
    niche = str(row.get("niche", "")).lower()

    if any(kw in content for kw in ("review", "comparison", "versus", "vs", "teardown")):
        return "Review / Comparison Content"

    if any(kw in niche for kw in ("deal", "coupon")) or str(row.get("coupon_heavy", "")).upper() == "TRUE":
        return "Seasonal Promotion"

    # Score-based mapping
    if top_score == "brand_fit" and row.get("follower_count", 0) > 200000:
        return "Awareness"
    if top_score == "conversion_potential":
        return "Conversion Push"
    if top_score == "content_quality":
        return "Review / Comparison Content"
    if top_score == "audience_fit":
        return "Product Launch"

    return "Awareness"
