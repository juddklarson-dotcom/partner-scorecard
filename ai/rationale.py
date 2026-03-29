"""AI explanation layer using Google Gemini API.

Generates rationale, campaign angles, and risk assessments.
All responses are cached to avoid repeated API calls.
"""

from __future__ import annotations
import streamlit as st

try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

from config import AI_MODEL, AI_MAX_TOKENS, AI_TEMPERATURE, GEMINI_API_KEY

_CLIENT = None

SYSTEM_PROMPT = (
    "You are a marketing analyst assistant for a gaming and PC hardware brand "
    "(similar to Corsair). You help evaluate creator and affiliate partners. "
    "Be specific, concise, and actionable. Use plain business language."
)


def _get_client():
    global _CLIENT
    if _CLIENT is None:
        if not GEMINI_API_KEY:
            raise ValueError("No Gemini API key configured")
        _CLIENT = genai.Client(api_key=GEMINI_API_KEY)
    return _CLIENT


@st.cache_data(ttl=3600, show_spinner=False)
def generate_fit_rationale(partner: dict, scores: dict) -> str:
    """Generate 2-3 sentence explanation of why this partner scored the way they did."""
    prompt = f"""Given this partner profile and their pre-computed scores, write 2-3 sentences explaining why they received this overall score. Be specific about strengths and weaknesses. Do NOT assign scores yourself — the scores are already computed.

Partner: {partner.get('partner_name')}
Type: {partner.get('partner_type')}
Platform: {partner.get('primary_platform')}
Niche: {partner.get('niche')}
Region: {partner.get('audience_region')}
Followers: {partner.get('follower_count'):,}
Engagement Rate: {partner.get('engagement_rate')}%
Bio: {partner.get('sample_bio')}
Sample content: {partner.get('sample_content_text')}
Prior brands: {partner.get('prior_brand_examples')}
Disclosure quality: {partner.get('disclosure_quality')}
Engagement quality: {partner.get('suspected_engagement_quality')}

Scores: Brand Fit {scores.get('brand_fit', 0):.0f}/100, Audience Fit {scores.get('audience_fit', 0):.0f}/100, Conversion Potential {scores.get('conversion_potential', 0):.0f}/100, Content Quality {scores.get('content_quality', 0):.0f}/100, Risk {100 - scores.get('risk_inverse', 100):.0f}/100
Overall: {scores.get('overall', 0):.0f}/100

Respond in 2-3 sentences, plain language, no markdown formatting."""

    return _call_ai(prompt)


@st.cache_data(ttl=3600, show_spinner=False)
def generate_campaign_angle(partner: dict, best_use_case: str) -> str:
    """Generate a suggested campaign angle and outreach approach."""
    prompt = f"""Suggest a specific campaign angle and outreach approach for this partner. Include what type of content to request, talking points for the outreach, and one creative campaign idea.

Partner: {partner.get('partner_name')}
Type: {partner.get('partner_type')}
Platform: {partner.get('primary_platform')}
Niche: {partner.get('niche')}
Followers: {partner.get('follower_count'):,}
Bio: {partner.get('sample_bio')}
Sample content: {partner.get('sample_content_text')}
Prior brands: {partner.get('prior_brand_examples')}
Recommended use case: {best_use_case}

Respond in 3-4 sentences, plain language, no markdown formatting. Be specific and actionable."""

    return _call_ai(prompt)


@st.cache_data(ttl=3600, show_spinner=False)
def generate_risk_summary(partner: dict, risk_score_val: float) -> str:
    """Identify specific risk flags from bio and content."""
    prompt = f"""Analyze this partner for potential risks. Consider: disclosure compliance, engagement authenticity, brand safety, content quality, and any red flags in their bio or content samples.

Partner: {partner.get('partner_name')}
Type: {partner.get('partner_type')}
Platform: {partner.get('primary_platform')}
Followers: {partner.get('follower_count'):,}
Engagement Rate: {partner.get('engagement_rate')}%
Bio: {partner.get('sample_bio')}
Sample content: {partner.get('sample_content_text')}
Prior brands: {partner.get('prior_brand_examples')}
Disclosure quality: {partner.get('disclosure_quality')}
Engagement quality: {partner.get('suspected_engagement_quality')}
Coupon heavy: {partner.get('coupon_heavy')}
Risk score: {risk_score_val:.0f}/100

Respond in 2-3 sentences identifying specific risk factors, plain language, no markdown formatting. If risk is low, say so clearly."""

    return _call_ai(prompt)


def _call_ai(prompt: str) -> str:
    """Make the Gemini API call with error handling."""
    if not HAS_GEMINI:
        return "AI analysis unavailable — google-genai package not installed. Run: pip install google-genai"

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=AI_MODEL,
            contents=f"{SYSTEM_PROMPT}\n\n{prompt}",
            config={
                "max_output_tokens": AI_MAX_TOKENS,
                "temperature": AI_TEMPERATURE,
            },
        )
        return response.text
    except ValueError as e:
        return f"AI analysis unavailable — {e}"
    except Exception as e:
        error_type = type(e).__name__
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return "AI analysis temporarily unavailable — Gemini API rate limit reached. Please try again shortly."
        return f"AI analysis temporarily unavailable ({error_type})."
