"""
Validation rules and threshold checks for micro-influencer filtering.
"""

from typing import Dict, Any, Tuple, List
import config

BEAUTY_BRAND_KEYWORDS = [
    "skin", "beauty", "skincare", "glow", "barrier", "serum", "clean",
    "hair", "cosmetic", "derma", "botanical", "hydrat", "makeup", "aesthetic",
    "wardrobe", "style", "chic", "fashion"
]

def check_category_match(candidate: Dict[str, Any], target_niche: str = config.TARGET_NICHE) -> Tuple[bool, str]:
    category = candidate.get("category", "").strip().lower()
    target = target_niche.strip().lower()

    if category == target:
        return True, f"Category '{candidate.get('category')}' matches target '{target_niche}'"
    return False, f"Category '{candidate.get('category')}' does not match target niche '{target_niche}'"

def check_follower_bounds(candidate: Dict[str, Any], min_fol: int = config.MIN_FOLLOWERS, max_fol: int = config.MAX_FOLLOWERS) -> Tuple[bool, str]:
    followers = candidate.get("followers", 0)
    if followers < min_fol:
        return False, f"Follower count ({followers:,}) is below micro-influencer floor ({min_fol:,})"
    if followers > max_fol:
        return False, f"Follower count ({followers:,}) exceeds micro-influencer ceiling ({max_fol:,})"
    return True, f"Follower count ({followers:,}) within valid range [{min_fol:,} - {max_fol:,}]"

def check_engagement_rate(candidate: Dict[str, Any], min_rate: float = config.MIN_ENGAGEMENT_RATE) -> Tuple[bool, str]:
    rate = candidate.get("engagement_rate", 0.0)
    if rate < min_rate:
        return False, f"Engagement rate ({rate:.1f}%) is below minimum threshold ({min_rate:.1f}%)"
    return True, f"Engagement rate ({rate:.1f}%) meets quality threshold (>= {min_rate:.1f}%)"

def check_content_relevance(candidate: Dict[str, Any]) -> Tuple[bool, str]:
    themes = candidate.get("content_themes", [])
    recent = candidate.get("recent_content", "")
    text_corpus = (" ".join(themes) + " " + recent).lower()

    matches = [kw for kw in BEAUTY_BRAND_KEYWORDS if kw in text_corpus]
    if matches:
        return True, f"Content relevance verified with signals: {', '.join(matches[:3])}"
    return False, "Content themes show insufficient alignment with brand vertical"
