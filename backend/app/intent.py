import re

SIGNAL_KEYWORDS = [
    ("PROCUREMENT_INTENT", ["procurement", "looking to procure", "procure"]),
    ("VENDOR_SEARCH", ["looking for a vendor", "looking for vendors", "seeking vendor", "looking for a partner", "implementation partner"]),
    ("HIRING", ["we're hiring", "we are hiring", "hiring", "open roles", "join our team", "recruiting"]),
    ("FUNDING", ["raised", "funding", "funded", "series a", "series b", "series c", "investment"]),
    ("PRODUCT_LAUNCH", ["launching", "launched", "new product", "product launch", "now live"]),
    ("AI_INITIATIVE", ["ai initiative", "generative ai", "genai", "artificial intelligence", "machine learning"]),
    ("CLOUD_MIGRATION", ["cloud migration", "migrating to aws", "migrating to azure", "migrating to gcp", "move to cloud"]),
    ("DIGITAL_TRANSFORMATION", ["digital transformation", "modernization", "modernising", "modernizing"]),
    ("EXPANSION", ["expanding", "expansion", "new office", "new market"]),
    ("PARTNERSHIP", ["partnership", "partnered with", "strategic partner"]),
    ("PAIN_POINT", ["struggling with", "challenge", "pain point", "problem with", "need help"]),
    ("LEADERSHIP_CHANGE", ["joined as", "appointed", "new ceo", "new cto", "new cio", "promoted to"]),
    ("COMPANY_GROWTH", ["growing", "growth", "scaling", "scale up"]),
    ("JOB_CHANGE", ["started a new role", "new role", "excited to join"]),
]

INTENT_SCORE = {
    "PROCUREMENT_INTENT": ("HIGH", 95),
    "VENDOR_SEARCH": ("HIGH", 92),
    "HIRING": ("HIGH", 88),
    "FUNDING": ("HIGH", 85),
    "CLOUD_MIGRATION": ("HIGH", 84),
    "AI_INITIATIVE": ("MEDIUM", 72),
    "PRODUCT_LAUNCH": ("MEDIUM", 68),
    "DIGITAL_TRANSFORMATION": ("MEDIUM", 66),
    "EXPANSION": ("MEDIUM", 64),
    "PARTNERSHIP": ("MEDIUM", 62),
    "PAIN_POINT": ("MEDIUM", 60),
    "LEADERSHIP_CHANGE": ("LOW", 45),
    "COMPANY_GROWTH": ("LOW", 42),
    "JOB_CHANGE": ("LOW", 35),
    "TECHNOLOGY_ADOPTION": ("MEDIUM", 65),
    "OTHER": ("NONE", 0),
}

def detect_signal(text: str) -> tuple[str, str, float, str | None]:
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    for signal, keywords in SIGNAL_KEYWORDS:
        for keyword in keywords:
            if keyword in normalized:
                intent, score = INTENT_SCORE[signal]
                return signal, intent, float(score), keyword
    return "OTHER", "NONE", 0.0, None
