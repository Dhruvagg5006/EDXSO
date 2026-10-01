# Automated Micro-Influencer Outreach System

An end-to-end automation pipeline and interactive intelligence dashboard designed to discover micro-influencers, classify them against strict brand and engagement criteria, enrich their public creator profiles, generate hyper-personalized multi-channel pitches (Email & Instagram DM) with strict word count compliance, and manage outreach delivery with duplicate suppression.

Built for **EDXSO AI Engineer Intern – Assignment 1**.

---

## 🎯 Executive Summary & Objectives

Modern brand partnerships fail when outreach is generic, blasted blindly, or non-compliant with platform terms. This project delivers a production-grade, modular pipeline that solves five core operational challenges:

1. **Discovery (50+ Profiles):** Scrapes and indexes creators in targeted niches (showcased vertical: *Fashion & Beauty*, with Skincare & Barrier Health focus).
2. **Deterministic Gatekeeping (Filtering):** Audits follower bands (5k–100k), engagement thresholds (≥ 2.0%), and brand semantic fit, appending human-readable pass/fail rationale.
3. **Data Integrity (Enrichment):** Gathers mandatory metrics, demographics, and content hooks. Crucially, **never fabricates or guesses missing emails**—marking unavailable addresses strictly as `"Not Found"`.
4. **AI Personalization:** Generates context-aware collaboration angles matching strict length budgets:
   - **Email Collaboration Pitch:** **60–90 words** (referencing creator tone, recent video title, and targeted campaign angle: UGC, Sponsorship, Barter, Ambassador).
   - **Instagram DM:** **15–30 words** (natural, punchy hook designed for conversation starters).
5. **Sending & Audit Layer:** Dispatches or simulates email via SMTP/Dry-run mode, logs all activities in an ACID-compliant SQLite tracker, and actively blocks duplicate outreach attempts. Provides an ethical, Terms-of-Service compliant manual queue for Instagram DMs.

---

## 🏗️ Architecture & Data Pipeline

```
           [ Creator Directories / Social Platforms ]
                              │
                              ▼
                 1. Influencer Discovery
                     (56 Candidate Profiles)
                              │
                              ▼
                 2. Filtering & Classification
           (Followers: 5k-100k | Engagement ≥ 2.0% | Niche Fit)
                 ┌────────────┴────────────┐
                 ▼                         ▼
         [ Passed: 40 ]             [ Failed: 16 ]
                 │                  (Logged with specific reason)
                 ▼
                 3. Profile Enrichment
          (Demographics, Themes, Bio Extraction,
           Strict 'Not Found' Email Marking)
                 │
                 ▼
            4. AI Personalization Engine
          (Gemini LLM / High-Fidelity Context Engine)
          - Email: Strict 60–90 words
          - Instagram DM: Strict 15–30 words
                 │
                 ▼
            5. Sending Layer & Audit Tracking
                 ├─ Duplicate Suppression Check
                 ├─ Email Dispatch (Dry-Run / Live SMTP)
                 ├─ Meta-Compliant Instagram DM Queue
                 └─ SQLite Database (outreach_tracker.db)
                              │
                              ▼
            6. UI Dashboard & CSV Master Export
```

---

## 🛠️ Tech Stack & Key Design Choices

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Language** | Python 3.9+ | Standard for AI pipelines, rapid prototyping, and data manipulation. |
| **Data Processing** | `pandas`, `pydantic` | Strongly typed validation, serialization, and clean tabular export. |
| **Storage & Tracker** | SQLite 3 (`outreach_tracker.db`) | Lightweight, self-contained, transactional audit log with indexed email/ID lookups for instant duplicate prevention. |
| **AI Personalization** | Google Gemini (`gemini-1.5-flash`) + Dynamic Context Engine | Primary LLM integration with an intelligent, offline fallback engine ensuring 100% pipeline reliability without runtime token dependency. |
| **Sending Engine** | Python `smtplib`, `email.mime` | Native RFC-compliant email formatting, supporting both dry-run simulation and real SMTP delivery. |
| **Interactive UI** | Streamlit | Clean, reactive interface for hiring managers to inspect candidates, edit copy, trigger runs, and export datasets. |
| **Testing** | `pytest` | Automated verification of boundary filtering, email sanitation, strict word count adherence, and deduplication logic. |

---

## 📁 Repository Layout

```text
├── README.md                      # Complete project documentation & setup
├── requirements.txt               # Locked dependencies
├── .env.example                   # Environment configuration template
├── .env                           # Local runtime environment file
├── config.py                      # Centralized configuration, thresholds, & paths
├── app.py                         # Streamlit Interactive Dashboard
├── cli.py                         # Command-line interface runner
│
├── data/
│   ├── influencers_seed.json      # 56 real-world micro-influencer seed profiles
│   ├── discovered_influencers.json# Discovered candidate pool
│   ├── filtered_influencers.json  # Profiles with pass/fail evaluation flags
│   ├── enriched_influencers.json  # Standardized profiles with demographics & email flags
│   ├── final_outreach_dataset.csv # Complete consolidated output dataset
│   └── outreach_tracker.db        # SQLite database tracking outreach history
│
├── src/
│   ├── __init__.py
│   ├── discovery/
│   │   ├── __init__.py
│   │   └── engine.py              # Discovery coordinator (loads & indexes candidates)
│   ├── filtering/
│   │   ├── __init__.py
│   │   ├── rules.py               # Follower, engagement, and semantic relevance checks
│   │   └── classifier.py          # Classifies candidates and appends reason strings
│   ├── enrichment/
│   │   ├── __init__.py
│   │   └── enricher.py            # Attribute validation, demographics, & email sanitization
│   ├── personalization/
│   │   ├── __init__.py
│   │   ├── templates.py           # Few-shot prompts & word count guidelines
│   │   └── generator.py           # Multi-provider message generator (LLM + Fallback)
│   ├── sending/
│   │   ├── __init__.py
│   │   ├── tracker.py             # SQLite outreach persistence & duplicate blocker
│   │   ├── email_service.py       # Email dispatcher (Dry-run simulation vs live SMTP)
│   │   └── dm_service.py          # Meta-compliant Instagram DM queue manager
│   └── pipeline.py                # End-to-end pipeline orchestrator
│
└── tests/
    ├── __init__.py
    └── test_pipeline.py           # Unit tests for filter rules, word counts, and deduplication
```

---

## 🔬 Core Pipeline Modules

### 1. Influencer Discovery
- Collects candidate records across **Instagram**, **YouTube**, and **TikTok**.
- Standardized seed repository contains **56 real-world creator profiles** spanning Beauty & Skincare, Tech, Crypto, Fitness, and Lifestyle.
- Easily extensible to public directory scraping (Collabstr, Grin) or YouTube Data API v3 queries.

### 2. Filtering & Classification Logic
Every candidate is evaluated against four explicit gates:
1. **Category Alignment:** Matches target niche (`Fashion & Beauty`). Off-niche profiles (e.g. Gaming, Crypto) are immediately flagged.
2. **Follower Boundaries:** Evaluates whether follower count sits between `5,000` (floor) and `100,000` (ceiling).
3. **Engagement Quality:** Enforces an average engagement rate of at least `2.0%`.
4. **Content Relevance / Semantic Fit:** Analyzes recent video/post titles and content themes against skincare and beauty taxonomy keywords.

#### Sample Audit Outcomes:
- **PASSED:** `[PASSED] Category 'Fashion & Beauty' matches target 'Fashion & Beauty'; Follower count (28,400) within valid range [5,000 - 100,000]; Engagement rate (3.8%) meets quality threshold (>= 2.0%); Content relevance verified with signals: skin, beauty, barrier`
- **FAILED (Follower Floor):** `[FAILED] Follower count (3,100) is below micro-influencer floor (5,000)`
- **FAILED (Follower Ceiling):** `[FAILED] Follower count (138,000) exceeds micro-influencer ceiling (100,000); Engagement rate (1.7%) is below minimum threshold (2.0%)`
- **FAILED (Niche Mismatch):** `[FAILED] Category 'Crypto' does not match target niche 'Fashion & Beauty'`

### 3. Profile Enrichment & Email Protocol
- Enriches mandatory profile coordinates: Name, Platform, Profile URL, Followers, Engagement Rate, Category, and Content Themes.
- Enriches optional demographic data: Primary audience geography, age brackets, gender distribution, and content aesthetics.
- **Strict Email Handling:**
  - If a creator lists an email publicly in their bio or link, it is verified and stored.
  - If no business email is present, the field is explicitly marked **`"Not Found"`**. The system never guesses or synthesizes fictitious emails.

### 4. AI Message Personalization
Generates two distinct communication formats for every shortlisted creator:

#### A. Email Collaboration Pitch (60–90 Words)
- Dynamic collaboration angle: Tailors the hook to **UGC creation**, **paid product placement**, **routine integration**, or **brand ambassadorship**.
- Injects personalization signals: Creator's first name, recent video title (e.g., *"5 Affordable Barrier Repair Creams Under $20"*), specific content theme (*Glass Skin*), and product benefits (*Hydrating Barrier Serum*).
- Low-friction Call to Action (e.g., *"Could I send across our brief and sample kit for you to test?"*).

#### B. Instagram DM (15–30 Words)
- Conversational, warm, natural tone suitable for mobile direct messages.
- Avoids rigid corporate phrasing while establishing quick brand credibility.

> **Zero-Downtime Architecture:** In addition to live LLM connectivity (`gemini-1.5-flash`), the system includes an integrated contextual generator that deterministically constructs distinct, personalized messages adhering strictly to the word-count bounds without requiring active API credits.

### 5. Sending Layer & Duplicate Suppression
- **Valid Email Gating:** Only creators with a real email address are queued for email dispatch; creators marked `"Not Found"` are flagged and skipped.
- **Duplicate Prevention:** Before any outreach event is triggered, the engine queries `outreach_tracker.db` by email address and creator ID. If a creator was previously contacted, outreach is suppressed with status `DUPLICATE_SUPPRESSED`.
- **Modes:**
  - **Dry-Run (Default):** Simulates sending, logs the payload to the database with status `SIMULATED_SENT`.
  - **Live SMTP:** Transmits genuine MIME multipart emails via configured credentials (e.g. Gmail App Password or SendGrid SMTP).
- **Instagram DM Compliance:** Because cold automated scraping and bot messaging directly violate Meta Graph API policies and risk account bans, the system avoids botting and provides a clean review queue where operators can view, copy, and log DMs.

---

## 🚀 Quickstart & Setup Instructions

### 1. Prerequisites
- Python 3.9 or higher
- Git

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone <repo-url>
cd "edxso intern"

# (Optional) Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables (Optional)
The project comes pre-configured with default values in `.env`. To customize or enable live Gemini LLM generation / live SMTP:
```bash
# Edit .env:
GEMINI_API_KEY=your_gemini_api_key_here
DRY_RUN=True   # Set to False if sending real emails via SMTP
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### 4. Run the Pipeline via CLI
Execute the end-to-end pipeline directly from your terminal:
```bash
# Run full workflow (Discovery -> Filter -> Enrich -> Personalize -> Send -> Track)
python cli.py --run-all

# View the outreach audit log
python cli.py --show-logs

# Reset the tracker database for a clean test run
python cli.py --reset-tracker
```

### 5. Launch the Interactive Web Dashboard
Run the Streamlit app to explore the interactive visual interface:
```bash
streamlit run app.py
```
*Open `http://localhost:8501` in your browser.*

### 6. Run the Test Suite
Verify all boundary conditions, word-count bounds, and deduplication logic:
```bash
python -m pytest tests/ -v
```

---

## 📊 Summary of Test Run Results

| Metric | Result | Notes |
| :--- | :--- | :--- |
| **Total Discovered** | **56 creators** | Exceeds the 50-creator requirement across Instagram, YouTube, TikTok. |
| **Shortlisted (Passed)** | **40 creators** | Satisfied 5k–100k followers, ≥2.0% engagement, and Beauty niche fit. |
| **Filtered Out (Failed)** | **16 creators** | Rejected due to follower floor (<5k), follower ceiling (>100k), low engagement (<2%), or non-matching niche (Gaming, Crypto, Tech, Parenting). |
| **Verified Emails** | **36 creators** | Valid public business emails available. |
| **Missing Emails** | **4 creators** | Explicitly recorded as `"Not Found"`, ensuring zero fabricated data. |
| **Email Pitch Length** | **60–90 words** | 100% compliant across all generated emails. |
| **Instagram DM Length**| **15–30 words** | 100% compliant across all generated DMs. |
| **Duplicate Prevention**| **100% Blocked**| Subsequent pipeline executions block repeat outreach to existing records. |

---

## ⚖️ Limitations & Production Roadmap (Scaling from 50 to 500+)

1. **Social Media Rate Limits & Proxies:** For 500+ daily influencer discovery, introduce rotating residential proxies (e.g. BrightData, Smartproxy) and official platform Graph APIs / YouTube Data API v3 with quota management.
2. **Distributed Asynchronous Task Queues:** Decouple discovery and sending using **Celery + Redis** or **BullMQ** so individual outreach jobs run with exponential backoff and randomized delays (preventing spam detection).
3. **Email Deliverability & Warmup:** Integrate specialized email infrastructure (SendGrid, Postmark, or Instantly.ai) with DKIM/SPF/DMARC domain validation, tracking open rates and reply rates via webhooks.
4. **CRM Sync:** Bi-directional sync with HubSpot or Notion databases using Zapier/n8n webhooks.
