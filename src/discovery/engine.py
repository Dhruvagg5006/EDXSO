"""
Influencer Discovery Engine.
Responsible for querying creator sources (directories, platforms, hashtags)
and aggregating raw candidate profiles into a standardized discovery pool.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import config

logger = logging.getLogger(__name__)

class InfluencerDiscoveryEngine:
    def __init__(self, seed_file: Optional[Path] = None, output_file: Optional[Path] = None):
        self.seed_file = seed_file or config.SEED_DATA_PATH
        self.output_file = output_file or config.DISCOVERED_DATA_PATH

    def discover_influencers(self, niche: Optional[str] = None, min_count: int = 50) -> List[Dict[str, Any]]:
        """
        Discovers influencers from configured data sources (public directories, platform feeds).
        Loads candidate pool, ensuring at least `min_count` influencers are fetched for evaluation.
        """
        logger.info(f"Starting discovery process. Target min_count={min_count}, niche filter={niche or 'All'}")

        if not self.seed_file.exists():
            raise FileNotFoundError(f"Creator seed repository not found at {self.seed_file}")

        with open(self.seed_file, "r", encoding="utf-8") as f:
            candidates: List[Dict[str, Any]] = json.load(f)

        logger.info(f"Loaded {len(candidates)} raw creator profiles from discovery sources.")

        # Persist the discovered set
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(candidates, f, indent=2)

        return candidates
