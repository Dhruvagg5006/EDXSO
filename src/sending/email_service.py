"""
Email Dispatcher with Duplicate Outreach Prevention.
Supports both realistic dry-run simulation mode and live SMTP dispatch.
"""

import time
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
import config
from .tracker import OutreachTracker

logger = logging.getLogger(__name__)

class EmailDispatcher:
    def __init__(self, tracker: Optional[OutreachTracker] = None, dry_run: bool = config.DRY_RUN):
        self.tracker = tracker or OutreachTracker()
        self.dry_run = dry_run

    def send_single_pitch(self, creator: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single qualified influencer for email outreach.
        Enforces validation, duplicate checking, and audit tracking.
        """
        name = creator.get("name", "Creator")
        email = creator.get("contact_email", "Not Found")
        cid = creator.get("id")
        platform = creator.get("platform", "Email")
        pitch = creator.get("email_pitch", "")

        # 1. Validation: check if email exists
        if not email or email == "Not Found":
            logger.info(f"Skipping email outreach for {name}: Contact email marked as 'Not Found'.")
            self.tracker.log_outreach(
                influencer_name=name,
                influencer_id=cid,
                platform=platform,
                email="Not Found",
                channel="EMAIL",
                message_content="N/A - Email address missing in public profile",
                status="SKIPPED_NO_EMAIL",
                notes="Creator profile has no public business email."
            )
            return {"influencer": name, "email": email, "status": "SKIPPED_NO_EMAIL", "details": "No email address found"}

        # 2. Duplicate Prevention
        if self.tracker.is_already_contacted(email=email, influencer_id=cid):
            logger.warning(f"Duplicate outreach prevented for {name} ({email}).")
            self.tracker.log_outreach(
                influencer_name=name,
                influencer_id=cid,
                platform=platform,
                email=email,
                channel="EMAIL",
                message_content=pitch,
                status="DUPLICATE_SUPPRESSED",
                notes="System blocked redundant outreach to previously contacted creator."
            )
            return {"influencer": name, "email": email, "status": "DUPLICATE_SUPPRESSED", "details": "Already contacted previously"}

        subject = f"Collaboration with {config.CAMPAIGN_BRAND_NAME} x {name}"

        # 3. Sending or Simulation
        if self.dry_run:
            # Simulate network handoff
            logger.info(f"[SIMULATED EMAIL] To: {email} | Subject: '{subject}'")
            self.tracker.log_outreach(
                influencer_name=name,
                influencer_id=cid,
                platform=platform,
                email=email,
                channel="EMAIL",
                message_content=pitch,
                status="SIMULATED_SENT",
                notes=f"Simulated dispatch via DRY_RUN mode. Subject: {subject}"
            )
            return {"influencer": name, "email": email, "status": "SIMULATED_SENT", "details": "Simulated successful delivery"}
        else:
            # Real SMTP execution
            try:
                msg = MIMEMultipart()
                msg["From"] = f"{config.SENDER_NAME} <{config.SENDER_EMAIL}>"
                msg["To"] = email
                msg["Subject"] = subject
                msg.attach(MIMEText(pitch, "plain"))

                with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
                    server.starttls()
                    server.login(config.SMTP_USER, config.SMTP_PASSWORD)
                    server.send_message(msg)

                logger.info(f"[LIVE EMAIL SENT] Successfully delivered to {email}")
                self.tracker.log_outreach(
                    influencer_name=name,
                    influencer_id=cid,
                    platform=platform,
                    email=email,
                    channel="EMAIL",
                    message_content=pitch,
                    status="SENT",
                    notes="Live delivery via SMTP host."
                )
                return {"influencer": name, "email": email, "status": "SENT", "details": "Successfully delivered via SMTP"}
            except Exception as e:
                logger.error(f"SMTP sending error for {email}: {e}")
                self.tracker.log_outreach(
                    influencer_name=name,
                    influencer_id=cid,
                    platform=platform,
                    email=email,
                    channel="EMAIL",
                    message_content=pitch,
                    status="FAILED",
                    notes=f"SMTP transport failure: {str(e)}"
                )
                return {"influencer": name, "email": email, "status": "FAILED", "details": str(e)}

    def batch_dispatch(self, creators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Executes email outreach for an entire batch of candidate creators.
        """
        logger.info(f"Starting email dispatch pipeline for {len(creators)} candidate records...")
        results = []
        for creator in creators:
            # Only process if creator passed filter and has pitch
            if creator.get("filter_status") == "PASSED" and creator.get("email_pitch"):
                res = self.send_single_pitch(creator)
                results.append(res)
        return results
