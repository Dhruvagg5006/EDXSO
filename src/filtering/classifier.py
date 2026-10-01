"""
Influencer Classifier & Gatekeeper.
Evaluates candidate profiles against criteria and records explicit pass/fail rationale.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import config
from .rules import (
    check_category_match,
    check_follower_bounds,
    check_engagement_rate,
    check_content_relevance,
)

logger = logging.getLogger(__name__)

class InfluencerClassifier:
    def __init__(self, target_niche: str = config.TARGET_NICHE):
        self.target_niche = target_niche

    def evaluate_candidate(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs comprehensive rule-checks on candidate. Returns enriched candidate with status and reason.
        """
        reasons_failed = []
        reasons_passed = []

        # 1. Category Match
        ok_cat, cat_msg = check_category_match(candidate, self.target_niche)
        if ok_cat:
            reasons_passed.append(cat_msg)
        else:
            reasons_failed.append(cat_msg)

        # 2. Follower Count (5,000 - 100,000)
        ok_fol, fol_msg = check_follower_bounds(candidate, config.MIN_FOLLOWERS, config.MAX_FOLLOWERS)
        if ok_fol:
            reasons_passed.append(fol_msg)
        else:
            reasons_failed.append(fol_msg)

        # 3. Engagement Rate (>= 2.0%)
        ok_eng, eng_msg = check_engagement_rate(candidate, config.MIN_ENGAGEMENT_RATE)
        if ok_eng:
            reasons_passed.append(eng_msg)
        else:
            reasons_failed.append(eng_msg)

        # 4. Content Relevance / Brand Fit
        ok_rel, rel_msg = check_content_relevance(candidate)
        if ok_rel:
            reasons_passed.append(rel_msg)
        else:
            # Relevance is a warning if category matched, but fails if not matched
            if not ok_cat:
                reasons_failed.append(rel_msg)

        # Overall Status
        passed = (len(reasons_failed) == 0)
        status = "PASSED" if passed else "FAILED"
        summary_reason = "; ".join(reasons_passed) if passed else "; ".join(reasons_failed)

        candidate_record = dict(candidate)
        candidate_record["filter_status"] = status
        candidate_record["filter_reason"] = f"[{status}] {summary_reason}"
        return candidate_record

    def filter_and_classify(
        self,
        candidates: List[Dict[str, Any]],
        output_file: Optional[Path] = None
    ) -> List[Dict[str, Any]]:
        """
        Classifies all candidates, segregates passed vs failed, and persists the dataset.
        """
        output_path = output_file or config.FILTERED_DATA_PATH
        logger.info(f"Classifying {len(candidates)} candidates for niche '{self.target_niche}'...")

        classified: List[Dict[str, Any]] = []
        passed_count = 0
        failed_count = 0

        for c in candidates:
            evaluated = self.evaluate_candidate(c)
            classified.append(evaluated)
            if evaluated["filter_status"] == "PASSED":
                passed_count += 1
            else:
                failed_count += 1

        logger.info(f"Classification completed: {passed_count} PASSED, {failed_count} FAILED.")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(classified, f, indent=2)

        return classified
