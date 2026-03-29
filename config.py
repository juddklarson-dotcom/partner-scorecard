# Partner Scorecard — Configuration & Constants
import os

# ── Scoring Weights (must sum to 1.0) ──────────────────────────────
WEIGHTS = {
    "brand_fit": 0.25,
    "audience_fit": 0.20,
    "conversion_potential": 0.20,
    "content_quality": 0.15,
    "risk_inverse": 0.20,  # applied as (100 - risk_score)
}

# ── Niche keywords that signal brand relevance (gaming/PC hardware) ─
BRAND_RELEVANT_NICHES = {
    "pc gaming", "gaming", "tech reviews", "pc builds", "streaming",
    "esports", "peripherals", "tech", "diy/maker", "pc hardware",
    "streaming/esports", "mechanical keyboards", "pc modding",
}

BRAND_RELEVANT_CONTENT_KEYWORDS = [
    "gaming", "pc", "build", "setup", "stream", "esport", "peripheral",
    "keyboard", "mouse", "headset", "monitor", "gpu", "cpu", "ram",
    "cooler", "case", "rgb", "corsair", "review", "benchmark", "fps",
    "hardware", "tech", "mod", "overclock", "battlestation",
]

# ── Platform relevance for a gaming/PC hardware brand ──────────────
PLATFORM_SCORES = {
    "YouTube": 90,
    "Twitch": 85,
    "TikTok": 70,
    "Instagram": 55,
    "Twitter/X": 50,
    "Blog": 75,
    "Discord": 40,
    "Podcast": 60,
}

# ── Target audience regions ────────────────────────────────────────
TARGET_REGIONS = {"NA", "EU", "Global"}

# ── Follower count scoring curve (diminishing returns) ─────────────
FOLLOWER_SWEET_SPOT = (10_000, 500_000)  # micro to mid-tier
FOLLOWER_MAX_SCORE = 100

# ── Disclosure quality mapping ─────────────────────────────────────
DISCLOSURE_SCORES = {
    "Excellent": 100,
    "Good": 80,
    "Fair": 50,
    "Poor": 25,
    "None": 0,
}

# ── Engagement quality mapping ─────────────────────────────────────
ENGAGEMENT_QUALITY_SCORES = {
    "Authentic": 100,
    "Likely Authentic": 75,
    "Questionable": 35,
    "Suspicious": 10,
}

# ── Action thresholds ──────────────────────────────────────────────
# Evaluated top-to-bottom; first match wins
ACTION_RULES = [
    {"min_score": 75, "max_risk": 30, "action": "Recruit Now"},
    {"min_score": 75, "max_risk": 50, "action": "Offer Hybrid Deal"},
    {"min_score": 60, "max_risk": 30, "action": "Test with Seeding"},
    {"min_score": 60, "max_risk": 50, "action": "Offer Affiliate-Only"},
    {"min_score": 0,  "min_risk": 50, "action": "Escalate for Review"},
    {"min_score": 45, "max_risk": 50, "action": "Monitor"},
    {"min_score": 0,  "max_risk": 50, "action": "Pause"},
]

# ── Recommended actions & best use cases ───────────────────────────
ACTIONS = [
    "Recruit Now",
    "Test with Seeding",
    "Offer Affiliate-Only",
    "Offer Hybrid Deal",
    "Monitor",
    "Pause",
    "Escalate for Review",
]

USE_CASES = [
    "Awareness",
    "UGC Creation",
    "Product Launch",
    "Conversion Push",
    "Review / Comparison Content",
    "Seasonal Promotion",
]

# ── Risk level labels ──────────────────────────────────────────────
RISK_LEVELS = {
    (0, 25): "Low",
    (25, 50): "Medium",
    (50, 75): "High",
    (75, 101): "Critical",
}

def risk_label(risk_score: float) -> str:
    for (lo, hi), label in RISK_LEVELS.items():
        if lo <= risk_score < hi:
            return label
    return "Unknown"

# ── Score color thresholds ─────────────────────────────────────────
SCORE_COLORS = {
    (75, 101): "#22c55e",  # green
    (60, 75):  "#84cc16",  # yellow-green
    (45, 60):  "#eab308",  # yellow
    (30, 45):  "#f97316",  # orange
    (0, 30):   "#ef4444",  # red
}

RISK_COLORS = {
    "Low": "#22c55e",
    "Medium": "#eab308",
    "High": "#f97316",
    "Critical": "#ef4444",
}

ACTION_COLORS = {
    "Recruit Now": "#22c55e",
    "Test with Seeding": "#84cc16",
    "Offer Affiliate-Only": "#60a5fa",
    "Offer Hybrid Deal": "#a78bfa",
    "Monitor": "#eab308",
    "Pause": "#9ca3af",
    "Escalate for Review": "#ef4444",
}

def score_color(score: float) -> str:
    for (lo, hi), color in SCORE_COLORS.items():
        if lo <= score < hi:
            return color
    return "#9ca3af"

# ── AI Configuration ───────────────────────────────────────────────
AI_MODEL = "gemini-2.5-flash"
AI_MAX_TOKENS = 300
AI_TEMPERATURE = 0.3
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
