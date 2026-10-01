"""
End-to-End Orchestrator Pipeline.
Coordinates:
1. Influencer Discovery (50+ profiles)
2. Filtering & Classification (pass/fail reason audit)
3. Profile Enrichment (mandatory fields, contact email verification)
4. AI Personalization (60-90 words email, 15-30 words DM)
5. Sending Layer & Audit Tracking (duplicate suppression, dry-run simulation)
6. Consolidated Dataset Export (CSV / JSON)
"""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import logging
import pandas as pd
from typing import Dict, Any, Optional
import config
from src.discovery.engine import InfluencerDiscoveryEngine
from src.filtering.classifier import InfluencerClassifier
from src.enrichment.enricher import ProfileEnricher
from src.personalization.generator import MessagePersonalizer
from src.sending.tracker import OutreachTracker
from src.sending.email_service import EmailDispatcher
from src.sending.dm_service import InstagramDMManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("PipelineRunner")

class MicroInfluencerPipeline:
    def __init__(
        self,
        niche: str = config.TARGET_NICHE,
        dry_run: bool = config.DRY_RUN
    ):
        self.niche = niche
        self.dry_run = dry_run
        self.discovery_engine = InfluencerDiscoveryEngine()
        self.classifier = InfluencerClassifier(target_niche=self.niche)
        self.enricher = ProfileEnricher()
        self.personalizer = MessagePersonalizer()
        self.tracker = OutreachTracker()
        self.email_dispatcher = EmailDispatcher(tracker=self.tracker, dry_run=self.dry_run)
        self.dm_manager = InstagramDMManager(tracker=self.tracker)

    def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Executes all pipeline phases and generates submission datasets.
        """
        logger.info("=== STEP 1: INFLUENCER DISCOVERY ===")
        raw_influencers = self.discovery_engine.discover_influencers(min_count=50)
        logger.info(f"Discovered {len(raw_influencers)} raw creator records.")

        logger.info("=== STEP 2: FILTERING & CLASSIFICATION ===")
        classified_influencers = self.classifier.filter_and_classify(raw_influencers)
        passed_count = sum(1 for c in classified_influencers if c["filter_status"] == "PASSED")
        failed_count = sum(1 for c in classified_influencers if c["filter_status"] == "FAILED")
        logger.info(f"Classification completed: {passed_count} Passed | {failed_count} Failed.")

        logger.info("=== STEP 3: PROFILE ENRICHMENT ===")
        enriched_influencers = self.enricher.enrich_dataset(classified_influencers, only_passed=False)
        valid_emails = sum(1 for c in enriched_influencers if c.get("has_valid_email") and c["filter_status"] == "PASSED")
        logger.info(f"Enrichment completed. Shortlisted with verified emails: {valid_emails}")

        logger.info("=== STEP 4: AI MESSAGE PERSONALIZATION ===")
        personalized_influencers = self.personalizer.batch_personalize(enriched_influencers)
        logger.info("Generated personalized emails (60-90 words) and DMs (15-30 words) for shortlisted creators.")

        logger.info("=== STEP 5: SENDING LAYER & OUTREACH TRACKING ===")
        email_outcomes = self.email_dispatcher.batch_dispatch(personalized_influencers)
        dm_outcomes = self.dm_manager.batch_process_dms(personalized_influencers)
        logger.info(f"Sending complete: {len(email_outcomes)} emails dispatched/simulated, {len(dm_outcomes)} DMs logged.")

        logger.info("=== STEP 6: EXPORTING CONSOLIDATED DATASET ===")
        df_export = []
        for c in personalized_influencers:
            df_export.append({
                "Name": c.get("name"),
                "Platform": c.get("platform"),
                "Followers": c.get("followers"),
                "Engagement": f"{c.get('engagement_rate', 0):.1f}%",
                "Niche": c.get("category"),
                "Email": c.get("contact_email"),
                "Profile URL": c.get("profile_url"),
                "Content Theme": ", ".join(c.get("content_themes", [])),
                "Status": c.get("filter_status"),
                "Filter Reason": c.get("filter_reason"),
                "Email Pitch": c.get("email_pitch"),
                "Email Word Count": c.get("email_word_count"),
                "Instagram DM": c.get("instagram_dm"),
                "DM Word Count": c.get("dm_word_count")
            })

        df = pd.DataFrame(df_export)
        df.to_csv(config.FINAL_DATASET_CSV, index=False)
        logger.info(f"Saved master dataset ({len(df)} rows) to {config.FINAL_DATASET_CSV}")

        return {
            "total_discovered": len(raw_influencers),
            "passed_filter": passed_count,
            "failed_filter": failed_count,
            "emails_dispatched": len(email_outcomes),
            "dms_queued": len(dm_outcomes),
            "csv_path": str(config.FINAL_DATASET_CSV),
            "db_path": str(config.DB_PATH)
        }

if __name__ == "__main__":
    pipeline = MicroInfluencerPipeline()
    summary = pipeline.run_full_pipeline()
    print("\n--- Pipeline Execution Summary ---")
    for k, v in summary.items():
        print(f"{k}: {v}")
