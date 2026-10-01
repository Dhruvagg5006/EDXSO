"""
Profile Enrichment Module.
Standardizes and verifies mandatory and optional profile attributes,
strictly handling contact discovery and flagging 'Not Found' emails.
"""

import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import config

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class ProfileEnricher:
    def __init__(self, output_file: Optional[Path] = None):
        self.output_file = output_file or config.ENRICHED_DATA_PATH

    def sanitize_email(self, email: Optional[str]) -> str:
        """
        Validates contact email address.
        If missing, empty, or improperly formatted, explicitly returns 'Not Found'.
        Never guesses or fabricates emails.
        """
        if not email or not isinstance(email, str):
            return "Not Found"
        
        cleaned = email.strip()
        if cleaned.lower() in ("not found", "none", "n/a", "null", ""):
            return "Not Found"

        if EMAIL_REGEX.match(cleaned):
            return cleaned
        return "Not Found"

    def enrich_profile(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates mandatory fields and normalizes optional demographic signals.
        """
        enriched = dict(candidate)

        # 1. Mandatory Fields
        name = str(enriched.get("name", "Unknown Creator")).strip()
        platform = str(enriched.get("platform", "Unknown")).strip()
        profile_url = str(enriched.get("profile_url", "")).strip()
        followers = int(enriched.get("followers", 0))
        engagement_rate = float(enriched.get("engagement_rate", 0.0))
        category = str(enriched.get("category", "General")).strip()
        
        raw_themes = enriched.get("content_themes", [])
        if isinstance(raw_themes, list):
            content_themes = [str(t).strip() for t in raw_themes if str(t).strip()]
        else:
            content_themes = [str(raw_themes).strip()]
        
        contact_email = self.sanitize_email(enriched.get("contact_email"))

        enriched["name"] = name
        enriched["platform"] = platform
        enriched["profile_url"] = profile_url
        enriched["followers"] = followers
        enriched["engagement_rate"] = engagement_rate
        enriched["category"] = category
        enriched["content_themes"] = content_themes
        enriched["contact_email"] = contact_email

        # 2. Optional Demographic & Platform Metadata
        enriched["handle"] = enriched.get("handle") or f"@{name.lower().replace(' ', '')}"
        enriched["website"] = enriched.get("website") or "Not Specified"
        enriched["audience_age"] = enriched.get("audience_age") or "Demographic data pending"
        enriched["audience_gender"] = enriched.get("audience_gender") or "Demographic data pending"
        enriched["audience_geography"] = enriched.get("audience_geography") or "Global"
        
        # Operational enrichment metadata
        enriched["has_valid_email"] = (contact_email != "Not Found")
        enriched["enriched_at"] = datetime.utcnow().isoformat() + "Z"
        
        return enriched

    def enrich_dataset(
        self,
        candidates: List[Dict[str, Any]],
        only_passed: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Enriches records in dataset.
        If only_passed is True, filters to only shortlisted influencers.
        """
        records_to_process = [
            c for c in candidates 
            if (not only_passed or c.get("filter_status") == "PASSED")
        ]

        logger.info(f"Enriching {len(records_to_process)} influencer records...")
        enriched_list = [self.enrich_profile(c) for c in records_to_process]

        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(enriched_list, f, indent=2)

        return enriched_list
