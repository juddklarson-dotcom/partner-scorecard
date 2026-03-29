"""Deterministic sub-score functions.

Each function takes a single partner row (pandas Series) and returns a float 0–100.
"""

from __future__ import annotations
import re
from config import (
    BRAND_RELEVANT_NICHES,
    BRAND_RELEVANT_CONTENT_KEYWORDS,
    PLATFORM_SCORES,
    TARGET_REGIONS,
    FOLLOWER_SWEET_SPOT,
    DISCLOSURE_SCORES,
    ENGAGEMENT_QUALITY_SCORES,
)


def _keyword_density(text: str, keywords: list[str]) -> float:
    """Return fraction of keywords found in text (0-1)."""
    if not text:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw in text_lower)
    return min(hits / max(len(keywords) * 0.3, 1), 1.0)


def brand_fit_score(row) -> float:
    """How well does this partner's content align with a gaming/PC hardware brand?"""
    score = 0.0

    # Niche match (0-40 pts)
    niche = str(row.get("niche", "")).lower().strip()
    if niche in BRAND_RELEVANT_NICHES:
        score += 40
    elif any(kw in niche for kw in ("tech", "gaming", "pc", "stream", "esport")):
        score += 25
    elif any(kw in niche for kw in ("diy", "maker", "review")):
        score += 15
    else:
        score += 5

    # Content keyword relevance (0-30 pts)
    content = str(row.get("sample_content_text", "")) + " " + str(row.get("sample_bio", ""))
    density = _keyword_density(content, BRAND_RELEVANT_CONTENT_KEYWORDS)
    score += density * 30

    # Prior brand examples (0-20 pts)
    brands = str(row.get("prior_brand_examples", ""))
    if brands and brands.lower() not in ("none", "nan", ""):
        brand_list = [b.strip() for b in brands.split(",") if b.strip()]
        tech_brands = [b for b in brand_list if any(kw in b.lower() for kw in (
            "corsair", "logitech", "razer", "hyperx", "steelseries", "nzxt",
            "asus", "msi", "evga", "seasonic", "thermaltake", "lian li",
            "elgato", "cooler master", "be quiet", "samsung", "kingston",
        ))]
        if tech_brands:
            score += min(len(tech_brands) * 7, 20)
        else:
            score += 5  # worked with brands, just not tech
    # else: 0 pts

    # Platform fit bonus (0-10 pts)
    platform = str(row.get("primary_platform", ""))
    plat_score = PLATFORM_SCORES.get(platform, 30)
    score += (plat_score / 90) * 10

    return min(round(score, 1), 100)


def audience_fit_score(row) -> float:
    """Does the partner's audience match target geography and demographics?"""
    score = 0.0

    # Region match (0-35 pts)
    region = str(row.get("audience_region", "")).strip()
    if region in TARGET_REGIONS:
        score += 35
    elif region == "LATAM":
        score += 15
    else:
        score += 10

    # Platform relevance (0-25 pts)
    platform = str(row.get("primary_platform", ""))
    plat_score = PLATFORM_SCORES.get(platform, 30)
    score += (plat_score / 90) * 25

    # Follower count sweet-spot curve (0-25 pts)
    followers = float(row.get("follower_count", 0))
    lo, hi = FOLLOWER_SWEET_SPOT
    if lo <= followers <= hi:
        score += 25  # sweet spot
    elif followers < lo:
        score += max(10, 25 * (followers / lo))
    else:
        # Diminishing returns past sweet spot
        excess = (followers - hi) / hi
        score += max(12, 25 - excess * 8)

    # Niche signals buyer intent (0-15 pts)
    niche = str(row.get("niche", "")).lower()
    if any(kw in niche for kw in ("review", "pc", "hardware", "build", "tech")):
        score += 15
    elif any(kw in niche for kw in ("gaming", "stream", "esport")):
        score += 10
    elif "diy" in niche or "maker" in niche:
        score += 8
    else:
        score += 3

    return min(round(score, 1), 100)


def conversion_potential_score(row) -> float:
    """How likely is this partner to drive actual purchases?"""
    score = 0.0

    # Engagement rate (0-25 pts) — moderate is best, very high can be fake
    engagement = float(row.get("engagement_rate", 0))
    if 2.0 <= engagement <= 7.0:
        score += 25  # healthy range
    elif 1.0 <= engagement < 2.0:
        score += 15
    elif 7.0 < engagement <= 10.0:
        score += 18  # high but possibly inflated
    else:
        score += 8  # too low or suspiciously high

    # Views efficiency — avg_views / follower_count (0-20 pts)
    followers = float(row.get("follower_count", 1))
    avg_views = float(row.get("avg_views", 0))
    view_ratio = avg_views / max(followers, 1)
    if view_ratio >= 0.3:
        score += 20
    elif view_ratio >= 0.15:
        score += 15
    elif view_ratio >= 0.05:
        score += 10
    else:
        score += 5

    # Cost efficiency (0-20 pts) — lower cost relative to reach is better
    cost_str = str(row.get("estimated_cost_or_commission", ""))
    cost_num = _extract_cost(cost_str)
    if cost_num > 0 and avg_views > 0:
        cpm = (cost_num / max(avg_views, 1)) * 1000
        if cpm < 5:
            score += 20
        elif cpm < 15:
            score += 15
        elif cpm < 30:
            score += 10
        else:
            score += 5
    elif "commission" in cost_str.lower() or "affiliate" in cost_str.lower():
        score += 18  # performance-based = good
    else:
        score += 10

    # Coupon-heavy penalty (0 or -15 pts)
    coupon = str(row.get("coupon_heavy", "")).upper()
    if coupon == "TRUE":
        score -= 15

    # Content type signals (0-15 pts)
    content = (str(row.get("sample_content_text", "")) + " " + str(row.get("niche", ""))).lower()
    if any(kw in content for kw in ("review", "comparison", "benchmark", "teardown", "guide", "tutorial")):
        score += 15
    elif any(kw in content for kw in ("build", "setup", "roundup", "deal")):
        score += 10
    elif any(kw in content for kw in ("unbox", "haul", "tip")):
        score += 7
    else:
        score += 3

    # Engagement quality bonus (0-20 pts)
    eq = str(row.get("suspected_engagement_quality", ""))
    eq_score = ENGAGEMENT_QUALITY_SCORES.get(eq, 50)
    score += (eq_score / 100) * 20

    return min(max(round(score, 1), 0), 100)


def content_quality_score(row) -> float:
    """Proxy for content production quality and professionalism."""
    score = 0.0

    # Content substance — length and specificity (0-30 pts)
    content = str(row.get("sample_content_text", ""))
    word_count = len(content.split())
    if word_count >= 25:
        score += 30
    elif word_count >= 15:
        score += 20
    else:
        score += 10

    # Bio quality (0-15 pts)
    bio = str(row.get("sample_bio", ""))
    bio_words = len(bio.split())
    if bio_words >= 10:
        score += 15
    elif bio_words >= 5:
        score += 10
    else:
        score += 5

    # Disclosure quality (0-25 pts)
    disc = str(row.get("disclosure_quality", "Fair"))
    disc_score = DISCLOSURE_SCORES.get(disc, 50)
    score += (disc_score / 100) * 25

    # Prior brand diversity (0-15 pts)
    brands = str(row.get("prior_brand_examples", ""))
    if brands and brands.lower() not in ("none", "nan", ""):
        brand_count = len([b.strip() for b in brands.split(",") if b.strip()])
        score += min(brand_count * 4, 15)
    else:
        score += 3  # no brand work yet, neutral

    # Content specificity — mentions data, numbers, details (0-15 pts)
    if re.search(r'\d+\s*(fps|hz|gb|tb|mm|\$|%|hours?|days?|weeks?)', content.lower()):
        score += 15
    elif re.search(r'\d', content):
        score += 8
    else:
        score += 3

    return min(round(score, 1), 100)


def risk_score(row) -> float:
    """Higher = riskier. This gets inverted for the composite score."""
    risk = 0.0

    # Engagement quality (0-35 pts of risk)
    eq = str(row.get("suspected_engagement_quality", ""))
    eq_val = ENGAGEMENT_QUALITY_SCORES.get(eq, 50)
    risk += (100 - eq_val) / 100 * 35

    # Disclosure quality (0-25 pts of risk)
    disc = str(row.get("disclosure_quality", "Fair"))
    disc_val = DISCLOSURE_SCORES.get(disc, 50)
    risk += (100 - disc_val) / 100 * 25

    # Coupon spam (0-10 pts of risk)
    coupon = str(row.get("coupon_heavy", "")).upper()
    if coupon == "TRUE":
        risk += 10

    # Engagement rate anomaly (0-15 pts of risk)
    engagement = float(row.get("engagement_rate", 0))
    followers = float(row.get("follower_count", 0))
    if engagement > 10:
        risk += 15  # very suspicious
    elif engagement > 8 and followers > 500000:
        risk += 12  # hard to maintain high engagement at scale
    elif engagement > 7 and followers > 200000:
        risk += 6

    # Views-to-follower mismatch (0-10 pts of risk)
    avg_views = float(row.get("avg_views", 0))
    if followers > 0:
        ratio = avg_views / followers
        if ratio < 0.02 and followers > 100000:
            risk += 10  # tons of followers, nobody watches
        elif ratio < 0.05 and followers > 100000:
            risk += 5

    # Sketchy content signals (0-5 pts of risk)
    content = str(row.get("sample_content_text", "")).lower()
    hype_words = sum(1 for w in ("omg", "insane", "literally", "best ever", "need this", "link in bio", "not sponsored") if w in content)
    if hype_words >= 3:
        risk += 5
    elif hype_words >= 2:
        risk += 3

    return min(round(risk, 1), 100)


def _extract_cost(cost_str: str) -> float:
    """Pull a dollar amount from strings like '$1500/video' or '$800/month'."""
    match = re.search(r'\$(\d[\d,]*)', cost_str)
    if match:
        return float(match.group(1).replace(",", ""))
    return 0.0
