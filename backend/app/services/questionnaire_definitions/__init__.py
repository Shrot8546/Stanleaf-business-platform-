from typing import Dict, Any, List, Optional
from app.services.questionnaire_definitions.restaurant import RESTAURANT_QUESTIONS
from app.services.questionnaire_definitions.ecommerce import ECOMMERCE_QUESTIONS

# Supported industry registry
QUESTIONNAIRE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "restaurant": {
        "industry": "restaurant",
        "title": "Restaurant Performance & Operations Diagnostic",
        "description": "Comprehensive diagnostic collecting financial, operational, order volume, and reputation metrics for restaurants and food service providers.",
        "questions": sorted(RESTAURANT_QUESTIONS, key=lambda q: q["display_order"]),
    },
    "ecommerce": {
        "industry": "ecommerce",
        "title": "E-Commerce & D2C Growth Diagnostic",
        "description": "Operational diagnostic collecting sales revenue, customer unit economics, margins, fulfillment, and conversion metrics for online retail stores.",
        "questions": sorted(ECOMMERCE_QUESTIONS, key=lambda q: q["display_order"]),
    },
}

# Industry normalization aliases map
INDUSTRY_ALIASES: Dict[str, str] = {
    "restaurant": "restaurant",
    "restaurants": "restaurant",
    "food & beverage": "restaurant",
    "food and beverage": "restaurant",
    "hospitality": "restaurant",
    "ecommerce": "ecommerce",
    "e-commerce": "ecommerce",
    "e-commerce & d2c": "ecommerce",
    "d2c": "ecommerce",
    "online retail": "ecommerce",
    "retail & consumer goods": "ecommerce",
}


def normalize_industry(industry: str) -> Optional[str]:
    """
    Normalizes user-supplied industry string to standard registry key.
    Returns normalized key if supported, or None if currently unsupported.
    """
    if not industry:
        return None
    cleaned = industry.strip().lower()
    return INDUSTRY_ALIASES.get(cleaned, cleaned if cleaned in QUESTIONNAIRE_REGISTRY else None)


def get_questionnaire_definition(industry: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves questionnaire definition for the given industry.
    """
    normalized = normalize_industry(industry)
    if not normalized or normalized not in QUESTIONNAIRE_REGISTRY:
        return None
    return QUESTIONNAIRE_REGISTRY[normalized]


def list_supported_industries() -> List[str]:
    """
    Returns list of supported industry identifiers.
    """
    return list(QUESTIONNAIRE_REGISTRY.keys())
