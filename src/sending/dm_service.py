"""
Instagram DM Delivery & Manual Workflow Manager.
Complies with Meta API Terms of Service (which prohibit unsanctioned cold DM bot automation)
by providing a simulated queue and one-click manual outreach clipboard system.
"""

import logging
from typing import Dict, Any, List, Optional
from .tracker import OutreachTracker

logger = logging.getLogger(__name__)

class InstagramDMManager:
    def __init__(self, tracker: Optional[OutreachTracker] = None):
        self.tracker = tracker or OutreachTracker()

    def process_dm(self, creator: Dict[str, Any], simulate_send: bool = True) -> Dict[str, Any]:
        """
        Processes an Instagram DM for the creator.
        Logs to tracker under channel INSTAGRAM_DM.
        """
        name = creator.get("name", "Creator")
        cid = creator.get("id")
        dm_content = creator.get("instagram_dm", "")
        handle = creator.get("handle", "")
        platform = creator.get("platform", "Instagram")

        if not dm_content or dm_content.startswith("N/A"):
            return {"influencer": name, "handle": handle, "status": "SKIPPED", "details": "No DM generated"}

        status = "DM_SIMULATED_SENT" if simulate_send else "DM_QUEUED"
        notes = "Processed via simulated Instagram DM outreach queue."

        self.tracker.log_outreach(
            influencer_name=name,
            influencer_id=cid,
            platform=platform,
            email=creator.get("contact_email", "Not Found"),
            channel="INSTAGRAM_DM",
            message_content=dm_content,
            status=status,
            notes=notes
        )

        return {
            "influencer": name,
            "handle": handle,
            "profile_url": creator.get("profile_url", ""),
            "status": status,
            "message": dm_content,
            "word_count": creator.get("dm_word_count", 0)
        }

    def batch_process_dms(self, creators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Queues/simulates DMs for all shortlisted creators.
        """
        results = []
        for c in creators:
            if c.get("filter_status") == "PASSED" and c.get("instagram_dm"):
                results.append(self.process_dm(c, simulate_send=True))
        return results
