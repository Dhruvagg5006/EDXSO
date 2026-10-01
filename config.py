import os
from pathlib import Path
from dotenv import load_dotenv

# Load local environment
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")

# Campaign Details
CAMPAIGN_BRAND_NAME = os.getenv("CAMPAIGN_BRAND_NAME", "GlowAura Botanicals")
CAMPAIGN_PRODUCT = os.getenv("CAMPAIGN_PRODUCT", "Hydrating Barrier Serum")
CAMPAIGN_TYPE = os.getenv("CAMPAIGN_TYPE", "UGC Collaboration")
SENDER_NAME = os.getenv("SENDER_NAME", "Alex Morgan")
SENDER_TITLE = os.getenv("SENDER_TITLE", "Creator Partnerships Lead")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "alex@glowaurabotanicals.com")

# Micro-Influencer Criteria
MIN_FOLLOWERS = int(os.getenv("MIN_FOLLOWERS", "5000"))
MAX_FOLLOWERS = int(os.getenv("MAX_FOLLOWERS", "100000"))
MIN_ENGAGEMENT_RATE = float(os.getenv("MIN_ENGAGEMENT_RATE", "2.0"))
TARGET_NICHE = os.getenv("TARGET_NICHE", "Fashion & Beauty")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Sending Layer Settings
DRY_RUN = os.getenv("DRY_RUN", "True").lower() in ("true", "1", "yes")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Storage Paths
DB_PATH = DATA_DIR / "outreach_tracker.db"
SEED_DATA_PATH = DATA_DIR / "influencers_seed.json"
DISCOVERED_DATA_PATH = DATA_DIR / "discovered_influencers.json"
FILTERED_DATA_PATH = DATA_DIR / "filtered_influencers.json"
ENRICHED_DATA_PATH = DATA_DIR / "enriched_influencers.json"
FINAL_DATASET_CSV = DATA_DIR / "final_outreach_dataset.csv"
